import streamlit as st
import router
import utils

router.remove_sidebar()
user = router.require_login()

st.title("Sistema de Hackathons Acadêmicos")
st.write(f"Olá, {user.get('nome', user.get('email', 'usuário'))}!")

if st.button("Sair"):
    router.logout()
    st.switch_page("./main.py")

for hackathon in router.get("/hackathon"):
    nome = hackathon["nome"]
    max_equipes = hackathon["max_equipes"]
    data_inicio = utils.format_datetime(hackathon["data_inicio"])
    data_fim = utils.format_datetime(hackathon["data_fim"])

    card = st.container(border=True)
    card.write(f"**{nome}**")
    card.write(f":material/calendar_clock: {data_inicio} → {data_fim}")
    card.write(f":material/group: Máximo de {max_equipes} equipes")
    if card.button("Selecionar", key=f"select-{hackathon['id']}"):
        st.session_state["selected_hackathon_id"] = hackathon["id"]
        st.query_params["id"] = str(hackathon["id"])
        st.switch_page("./pages/hackathon.py")
