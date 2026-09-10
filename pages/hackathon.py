import streamlit as st
import router
import utils

router.remove_sidebar()
user = router.require_login()

hackathon_id = st.query_params.get("id")
if hackathon_id is None:
    hackathon_id = st.session_state.get("selected_hackathon_id")

if hackathon_id is None:
    st.error("Nenhuma hackathon foi selecionada.")
    st.switch_page("./pages/home.py")

hackathons = router.get("/hackathon/", params={"id": hackathon_id})
if not hackathons:
    st.error("Hackathon não encontrada.")
    st.stop()

hackathon = hackathons[0]
st.title(hackathon["nome"])
st.write(f":material/calendar_clock: Início em {utils.format_datetime(hackathon['data_inicio'])}")
st.write(f":material/calendar_clock: Encerra em {utils.format_datetime(hackathon['data_fim'])}")

if st.button("Voltar", icon=":material/arrow_back:"):
    st.switch_page("./pages/home.py")

registered_users = router.get(
    "/hackathon/registereds/",
    params={"id_hackathon": hackathon_id},
)
registration = next(
    (item for item in registered_users if item.get("usuario", {}).get("id") == user.get("id")),
    None,
)

if registration is None:
    st.info("Você ainda não está inscrito nesta hackathon.")
    if st.button("Participar", type="primary"):
        router.post(
            "/hackathon/register/",
            {"id_hackathon": int(hackathon_id), "id_usuario": user["id"]},
        )
        st.rerun()
    st.stop()

judges = router.get("/hackathon/evaluation/judges", params={"id_hackathon": hackathon_id})
mentors = router.get("/hackathon/mentoring/mentors/", params={"id_hackathon": hackathon_id})
user_id = user["id"]
is_judge = any(item.get("id") == user_id for item in judges)
is_mentor = any(item.get("id") == user_id for item in mentors)
role = "Jurado" if is_judge else "Mentor" if is_mentor else "Participante"
st.caption(f"Você está acessando como {role}")

teams = router.get("/hackathon/teams/", params={"id_hackathon": hackathon_id})
users = router.get("/user/")

team_feedback = st.session_state.pop("team_feedback", None)
if team_feedback:
    st.success(team_feedback)

if role == "Participante":
    own_team = next(
        (
            team for team in teams
            if any(member.get("id") == user_id for member in team.get("integrantes", []))
        ),
        None,
    )

    if own_team is None:
        st.subheader("Minha equipe")
        with st.form("create_team"):
            team_name = st.text_input("Nome da equipe")
            submitted = st.form_submit_button("Cadastrar equipe")
            if submitted:
                if not team_name.strip():
                    st.warning("Informe um nome para a equipe.")
                else:
                    with st.spinner("Cadastrando equipe..."):
                        created_team = router.post(
                            "/hackathon/teams/",
                            {
                                "nome": team_name.strip(),
                                "id_hackathon": int(hackathon_id),
                                "id_usuario": user_id,
                            },
                        )
                        st.session_state["team_feedback"] = (
                            f"Equipe '{team_name.strip()}' cadastrada com sucesso."
                        )
                        st.rerun()
    else:
        st.subheader(f"Minha equipe: {own_team['nome']}")
        team_member_ids = {
            member["id"]
            for team in teams
            for member in team.get("integrantes", [])
        }
        available_members = [
            candidate
            for candidate in users
            if candidate.get("id") not in team_member_ids
            and candidate.get("id") != user_id
            and not candidate.get("eh_admin", False)
        ]

        with st.form("add_member_form"):
            member_options = {
                f"{member['nome']} <{member['email']}>": member["id"]
                for member in available_members
            }
            selected_member = st.selectbox(
                "Participante para adicionar",
                list(member_options),
                disabled=not member_options,
            ) if member_options else None
            add_member = st.form_submit_button(
                "Adicionar integrante",
                disabled=not member_options,
            )
            if add_member and selected_member is not None:
                with st.spinner("Adicionando integrante..."):
                    router.post(
                        "/hackathon/team/add_member",
                        params={
                            "id_hackathon": int(hackathon_id),
                            "id_team": own_team["id"],
                            "id_member": member_options[selected_member],
                        },
                    )
                st.session_state["team_feedback"] = (
                    f"{selected_member} foi adicionado à equipe."
                )
                st.rerun()

        st.write("**Integrantes**")
        for member in own_team.get("integrantes", []):
            st.write(f"- {member['nome']} `<{member['email']}>`")

        with st.form("project_form"):
            title = st.text_input("Título do projeto", own_team.get("titulo_projeto", ""))
            description = st.text_area("Descrição", own_team.get("descricao_projeto", ""))
            area = st.selectbox(
                "Área temática",
                [
                    "Engenharia de Software", "Banco de Dados", "Inteligência Artificial",
                    "Segurança da Informação", "Ciência de Dados",
                    "Interação Humano-Computador",
                ],
            )
            if st.form_submit_button("Salvar projeto", type="primary"):
                router.post(
                    "/hackathon/team/project/",
                    {
                        "id": own_team["id"],
                        "id_hackathon": int(hackathon_id),
                        "titulo_projeto": title,
                        "descricao_projeto": description,
                        "area_tematica": area,
                    },
                )
                st.rerun()

        st.subheader("Avaliações")
        for evaluation in router.get("/hackathon/evaluation/", params={"id_equipe": own_team["id"]}):
            st.write(f"**Nota:** {evaluation['nota']} - {evaluation['comentarios']}")

        st.subheader("Mentorias")
        for mentoring in router.get(
            "/hackathon/mentoring/",
            params={"id_hackathon": hackathon_id, "id_equipe": own_team["id"]},
        ):
            st.write(mentoring["comentarios"])

    if st.button("Sair da hackathon"):
        router.post(
            "/hackathon/register/remove",
            params={"id_hackathon": hackathon_id, "id_registered": user_id},
        )
        st.rerun()

elif role == "Jurado":
    st.subheader("Avaliar projetos")
    if teams:
        team_options = {f"#{team['id']} - {team['nome']}": team["id"] for team in teams}
        selected_team = st.selectbox("Projeto", list(team_options))
        with st.form("evaluation_form"):
            grade = st.number_input("Nota", min_value=0, max_value=10, step=1)
            comments = st.text_area("Comentários")
            if st.form_submit_button("Enviar avaliação", type="primary"):
                router.post(
                    "/hackathon/evaluation/",
                    {
                        "id_jurado": user_id,
                        "id_equipe": team_options[selected_team],
                        "nota": grade,
                        "comentarios": comments,
                    },
                )
                st.success("Avaliação enviada.")

else:
    st.subheader("Adicionar mentoria")
    if teams:
        team_options = {f"#{team['id']} - {team['nome']}": team["id"] for team in teams}
        selected_team = st.selectbox("Equipe", list(team_options))
        with st.form("mentoring_form"):
            comments = st.text_area("Orientação")
            if st.form_submit_button("Registrar mentoria", type="primary"):
                router.post(
                    "/hackathon/mentoring/",
                    {
                        "id_mentor": user_id,
                        "id_equipe": team_options[selected_team],
                        "comentarios": comments,
                    },
                )
                st.success("Mentoria registrada.")

    st.subheader("Minhas mentorias registradas")
    mentorings = router.get(
        "/hackathon/mentoring/",
        params={"id_hackathon": hackathon_id, "id_mentor": user_id},
    )
    if not mentorings:
        st.info("Nenhuma mentoria registrada nesta hackathon.")
    for mentoring in mentorings:
        card = st.container(border=True)
        card.write(f"**Equipe:** {mentoring['equipe']['nome']}")
        card.write(f"**Mentor:** {mentoring['mentor']['nome']}")
        card.write(f"**Comentários:** {mentoring['comentarios']}")
