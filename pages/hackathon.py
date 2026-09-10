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
st.caption(f"Perfil nesta hackathon: {role}")

teams = router.get("/hackathon/teams/", params={"id_hackathon": hackathon_id})

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
            if st.form_submit_button("Cadastrar equipe", type="primary") and team_name:
                created_team = router.post(
                    "/hackathon/teams/",
                    {"nome": team_name, "id_hackathon": int(hackathon_id)},
                )
                if created_team.get("id"):
                    router.post(
                        "/hackathon/team/add_member",
                        {
                            "id_hackathon": int(hackathon_id),
                            "id_team": created_team["id"],
                            "id_member": user_id,
                        },
                    )
                st.rerun()
    else:
        st.subheader(f"Minha equipe: {own_team['nome']}")
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
