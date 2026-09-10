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

        card2.button("Ver mentorias")
        card2.button("Ver avaliações")