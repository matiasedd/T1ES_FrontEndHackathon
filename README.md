# Sistema de Hackathons Acadêmicos

Frontend da aplicação de hackathons acadêmicos. A interface foi construída com [Streamlit](https://streamlit.io/) e consome a API do backend por HTTP.

## Requisitos

- Python 3.10 ou superior
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

### Backend

Em um terminal, inicie a API:

```bash
cd backend
uv run fastapi dev
```

O backend ficará disponível em `http://localhost:8000`.

### Frontend

Em outro terminal, entre no diretório do frontend, ative o ambiente virtual e execute:

```bash
cd frontend
source .venv/bin/activate
streamlit run main.py
```

O Streamlit exibirá no terminal o endereço local da aplicação, normalmente `http://localhost:8501`.

## Arquivos estáticos

Este frontend usa Streamlit e não possui uma etapa de build que gere uma pasta `dist/` com arquivos HTML, CSS e JavaScript estáticos. A aplicação precisa ser executada pelo servidor Streamlit, pois contém login, cookies, formulários e comunicação dinâmica com a API.

Para disponibilizar a aplicação, execute o backend e o frontend como processos separados. Não é necessário gerar arquivos estáticos.

