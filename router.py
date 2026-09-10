import streamlit as st
import requests
import extra_streamlit_components as stx
import json
from datetime import datetime, timedelta, timezone

BASE_PATH = "http://localhost:8000"
SESSION_COOKIE = "hackathon_session"
SESSION_DURATION = timedelta(days=1)


def _cookie_manager():
    return stx.CookieManager(key="hackathon-cookie-manager")


def login(user_data):
    session_data = {
        key: value for key, value in user_data.items() if key != "senha"
    }
    st.session_state["current_user"] = session_data
    _cookie_manager().set(
        SESSION_COOKIE,
        json.dumps(session_data),
        expires_at=datetime.now(timezone.utc) + SESSION_DURATION,
    )


def get_current_user():
    current_user = st.session_state.get("current_user")
    if current_user is not None:
        return current_user

    session_value = _cookie_manager().get(SESSION_COOKIE)
    if not session_value:
        return None

    try:
        current_user = json.loads(session_value)
        st.session_state["current_user"] = current_user
        return current_user
    except (TypeError, json.JSONDecodeError):
        logout()
        return None


def logout():
    st.session_state.pop("current_user", None)
    _cookie_manager().delete(SESSION_COOKIE)


def require_login(admin_only=False):
    user = get_current_user()
    if user is None or (admin_only and not user.get("eh_admin", False)):
        st.warning("Sua sessão expirou. Faça login para continuar.")
        st.switch_page("./main.py")
    return user

def get(endpoint: str, params=None):
    response = requests.get(f"{BASE_PATH}{endpoint}", params=params)
    return response.json()

def post(endpoint: str, data=None, params=None):
    response = requests.post(f"{BASE_PATH}{endpoint}", params=params, json=data)
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError as error:
        response.raise_for_status()
        raise RuntimeError(
            f"A API retornou uma resposta inválida para POST {endpoint}: "
            f"HTTP {response.status_code}"
        ) from error

    response.raise_for_status()
    return response_data

def remove_sidebar():
    pass
    # st.markdown(
    #     """
    #     <style>
    #         [data-testid="stSidebar"] {
    #             display: none;
    #         }
    #         [data-testid="collapsedControl"] {
    #             display: none;
    #         }
    #     </style>
    #     """,
    #     unsafe_allow_html=True,
    # )