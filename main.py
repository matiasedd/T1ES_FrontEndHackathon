import streamlit as st
import locale
import router
import utils

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

st.write("# Sistema de Hackathons Acadêmicos")

for hackathon in router.get("/hackathon"):
    id, nome, descricao, max_equipes, data_inicio = hackathon

    data_inicio = utils.format_datetime(data_inicio)

    card = st.container(border=True)

    card.write(f"**{nome}**")

    if descricao:
        card.write(descricao)
    else:
        card.caption("(Sem descrição)")

    card.write(f":material/calendar_clock: {data_inicio} → ")
    card.caption(f"Este evento suporta até {max_equipes} equipes")

    card.button("Inscrever-se", key=id)
