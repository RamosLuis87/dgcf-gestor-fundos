[README.md](https://github.com/user-attachments/files/35464923/README.md)
# DGCF | Gestor de Fundos

**Versão P002 · 0.2 (Demonstração)**  
Protótipo web alinhado com a informação da versão desktop Tkinter 0.15  
**Dados 100% fictícios** — Município inventado "Vila Nova do Norte"

## Separadores

- **Painel geral** — KPIs + projetos em execução + tramitações pendentes
- **Atenção** — alertas automáticos e manuais (prioridade P1–P3)
- **Projetos** — lista com filtros + ficha detalhada (financeira, física, histórico)
- **Tramitações** — movimentos com autoridades de gestão
- **Históricos** — linha do tempo de eventos por projeto
- **Relatórios** — resumos e exportação CSV

## Correr localmente

```bash
pip install -r requirements.txt
streamlit run app_dgcf.py
```

## Deploy Streamlit Cloud

Main file path: `app_dgcf.py`  
Ficheiros necessários: `app_dgcf.py`, `dgcf_demo_dummy.db`, `requirements.txt`

## Nota

Esta versão serve **apenas para demonstração**.  
Para trabalho real na Câmara utilizar a versão desktop Tkinter (offline).
