# Sistema de Hackathons Acadêmicos

Frontend da aplicação de hackathons acadêmicos. A interface foi construída com [Streamlit](https://streamlit.io/) e consome a API do backend por HTTP.

## Requisitos

- Python 3.9 ou superior
- Backend da aplicação em execução na porta `8000`

Por padrão, o frontend consulta a API em `http://localhost:8000`.

## Instalação

Clone o repositório e entre neste diretório:

```bash
cd frontend
```

Crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows, use:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

## Execução

Com o backend disponível em `localhost:8000`, execute:

```bash
streamlit run main.py
```

O Streamlit exibirá no terminal o endereço local da aplicação, normalmente `http://localhost:8501`.

