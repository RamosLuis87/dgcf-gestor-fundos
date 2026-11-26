# DGCF | Gestor de Fundos

**Versão P001 · 0.1**  
Protótipo de gestão de candidaturas e execução de projetos PRR / Fundos Europeus  
Município de Barcelos

## Descrição

Aplicação offline/web para acompanhamento de candidaturas a fundos europeus (PRR), com:

- Painel de controlo (KPIs)
- Lista de projetos com filtros
- Ficha detalhada de cada projeto (execução física e financeira + histórico)
- Relatórios e exportação CSV

## Como correr localmente

```bash
pip install -r requirements.txt
streamlit run app_dgcf.py
```

## Deploy no Streamlit Community Cloud (teste)

1. Criar repositório no GitHub e enviar estes ficheiros
2. Ir a [share.streamlit.io](https://share.streamlit.io)
3. "New app" → escolher o repositório → Main file path: `app_dgcf.py`
4. Deploy

**Nota:** Nesta versão de teste a base de dados SQLite é apenas de leitura. Em ambiente de produção recomenda-se servidor interno da Câmara.

## Ficheiros

| Ficheiro | Descrição |
|----------|-----------|
| `app_dgcf.py` | Aplicação principal |
| `dgcf_gestor_fundos.db` | Base de dados SQLite (76 projetos) |
| `requirements.txt` | Dependências |

## Versão

P001 · 0.1 — Novembro 2026
