import streamlit as st
import router
import utils

router.remove_sidebar()
router.require_login(admin_only=True)

@st.dialog("Novo Evento")
def new_hackathon():
    with st.form("New Hackathon"):
        nome = st.text_input("Título")
        data_inicio = st.datetime_input("Data de Início")
        data_fim = st.datetime_input("Data de Encerramento")
        max_equipes = st.number_input("Máximo de equipes", 1, 20)

        payload = {
            "nome": nome,
            "data_inicio": data_inicio.isoformat(),
            "data_fim": data_fim.isoformat(),
            "max_equipes": max_equipes
        }

        def handle_submission():
            response = router.post("/hackathon/", payload)
            st.info(response["message"])
        
        if st.form_submit_button("Enviar"):
            handle_submission()


@st.dialog("Registrar mentoria")
def add_mentoring(hackathon_id, team, mentors):
    if not mentors:
        st.warning("Nenhum mentor foi cadastrado nesta hackathon.")
        return

    mentor_options = {
        f"{mentor['nome']} <{mentor['email']}>": mentor["id"]
        for mentor in mentors
    }
    with st.form(f"mentoring-form-{hackathon_id}-{team['id']}"):
        selected_mentor = st.selectbox("Mentor responsável", list(mentor_options))
        comments = st.text_area("Comentários sobre a orientação")
        if st.form_submit_button("Registrar mentoria", type="primary"):
            if not comments.strip():
                st.warning("Informe os comentários da orientação.")
                return

            router.post(
                "/hackathon/mentoring/",
                {
                    "id_mentor": mentor_options[selected_mentor],
                    "id_equipe": team["id"],
                    "comentarios": comments.strip(),
                },
            )
            st.success("Mentoria registrada com sucesso.")
            st.rerun()


@st.dialog("Registrar avaliação")
def add_evaluation(hackathon_id, team, judges):
    if not judges:
        st.warning("Nenhum jurado foi cadastrado nesta hackathon.")
        return

    judge_options = {
        f"{judge['nome']} <{judge['email']}>": judge["id"]
        for judge in judges
    }
    with st.form(f"evaluation-form-{hackathon_id}-{team['id']}"):
        selected_judge = st.selectbox("Jurado responsável", list(judge_options))
        grade = st.number_input("Nota", min_value=0, max_value=10, step=1)
        comments = st.text_area("Comentários da avaliação")
        if st.form_submit_button("Registrar avaliação", type="primary"):
            if not comments.strip():
                st.warning("Informe os comentários da avaliação.")
                return

            router.post(
                "/hackathon/evaluation/",
                {
                    "id_jurado": judge_options[selected_judge],
                    "id_equipe": team["id"],
                    "nota": grade,
                    "comentarios": comments.strip(),
                },
            )
            st.success("Avaliação registrada com sucesso.")
            st.rerun()

st.title("Painel Administrativo")

users = router.get("/user/")
user_options = {
    f"{item['nome']} <{item['email']}>": item["id"]
    for item in users
}

if st.button("Novo Evento", icon=":material/calendar_add_on:"):
    new_hackathon()

for hackathon in router.get("/hackathon"):
    data_inicio = utils.format_datetime(hackathon["data_inicio"])
    data_fim = utils.format_datetime(hackathon["data_fim"])
    
    card = st.container(border=True)
    card.write(f"##### {hackathon["nome"]}")
    card.write(f":material/calendar_clock: {data_inicio} → {data_fim}")
    card.write(f":material/group: Máximo de {hackathon["max_equipes"]} equipes")

    mentors = router.get(
        "/hackathon/mentoring/mentors/",
        params={"id_hackathon": hackathon["id"]},
    )
    judges = router.get(
        "/hackathon/evaluation/judges",
        params={"id_hackathon": hackathon["id"]},
    )

    with card.expander("Cadastrar responsáveis"):
        selected_user = st.selectbox(
            "Usuário",
            list(user_options),
            key=f"user-{hackathon['id']}",
        )
        col_mentor, col_judge = st.columns(2)
        if col_mentor.button("Cadastrar mentor", key=f"mentor-{hackathon['id']}"):
            router.post(
                "/hackathon/register/mentor/",
                {
                    "id_hackathon": hackathon["id"],
                    "id_usuario": user_options[selected_user],
                },
            )
            st.rerun()
        if col_judge.button("Cadastrar jurado", key=f"judge-{hackathon['id']}"):
            router.post(
                "/hackathon/register/judge/",
                {
                    "id_hackathon": hackathon["id"],
                    "id_usuario": user_options[selected_user],
                },
            )
            st.rerun()

    card.write("**Equipes**")

    card2 = card.container(border=True)

    for team in router.get(f"/hackathon/teams?id_hackathon={hackathon["id"]}"):
        card2.write(f"**#{team["id"]} -- {team["nome"]}**")
        card2.write(f"Integrantes: {", ".join([f"{i["nome"]} `<{i["email"]}>`" for i in team["integrantes"]])}")

        card3 = card2.container(border=True)
        card3.write(f"**{team["titulo_projeto"]}**")
        card3.write(f"{team["descricao_projeto"]}")
        card3.write(f":blue-badge[{team["area_tematica"]}]")

        if card2.button("Adicionar mentoria", key=f"mentoring-{hackathon['id']}-{team['id']}"):
            add_mentoring(hackathon["id"], team, mentors)
        if card2.button("Adicionar avaliação", key=f"evaluation-{hackathon['id']}-{team['id']}"):
            add_evaluation(hackathon["id"], team, judges)

        mentorings = router.get(
            "/hackathon/mentoring/",
            params={"id_hackathon": hackathon["id"], "id_equipe": team["id"]},
        )
        evaluations = router.get(
            "/hackathon/evaluation/",
            params={"id_equipe": team["id"]},
        )

        with card2.expander("Mentorias registradas"):
            if not mentorings:
                st.info("Nenhuma mentoria registrada.")
            for mentoring in mentorings:
                st.write(
                    f"**{mentoring['mentor']['nome']}**: "
                    f"{mentoring['comentarios']}"
                )

        with card2.expander("Avaliações registradas"):
            if not evaluations:
                st.info("Nenhuma avaliação registrada.")
            for evaluation in evaluations:
                st.write(
                    f"**{evaluation['jurado']['nome']}** - "
                    f"Nota: **{evaluation['nota']}** - "
                    f"{evaluation['comentarios']}"
                )