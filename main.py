import streamlit as st
import locale
import router

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

@st.dialog("Realizar Cadastro")
def signup():
    st.text("Preencha os campos abaixo para realizar o cadastro")

    with st.form("signup_form"):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail", type="email")
        senha = st.text_input("Senha", type="password")

        payload = {
            "nome": nome,
            "email": email,
            "senha": senha,
            "eh_admin": False
        }

        def handle_submission():
            response = router.post("/user/", payload)
            st.info(response["message"])

        if st.form_submit_button("Enviar"):
            handle_submission()

st.write("# Sistema de Hackathons Acadêmicos")

with st.form("login_form"):
    email = st.text_input("E-mail", type="email")
    senha = st.text_input("Senha", type="password")

    payload = {
        "email": email,
        "senha": senha
    }

    def handle_auth():
        response = router.get("/authenticate/", params=payload)

        if "message" in response:
            st.error(response["message"])

    if st.form_submit_button("Entrar"):
        handle_auth()

st.text("Não possui conta?")

if st.button("Cadastre-se"):
    signup()
