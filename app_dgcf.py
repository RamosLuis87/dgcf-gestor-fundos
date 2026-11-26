
"""
DGCF | Gestor de Fundos
Versão P002 · 0.2 (Demonstração)
Alinhada com a informação da versão Tkinter 0.15
Dados 100% fictícios — Município "Vila Nova do Norte"
"""

import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

VERSION = "P002 · 0.2 (Demo)"
DB_PATH = Path(__file__).parent / "dgcf_demo_dummy.db"

st.set_page_config(
    page_title=f"DGCF | Gestor de Fundos ({VERSION})",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-header { font-size: 1.7rem; font-weight: 700; color: #1e293b; margin-bottom: 0.15rem; }
    .sub-header { color: #64748b; font-size: 0.92rem; margin-bottom: 1.2rem; }
    .kpi-card {
        background: white; border: 1px solid #e2e8f0; border-radius: 12px;
        padding: 1.1rem 1.3rem; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .kpi-label { font-size: 0.78rem; color: #64748b; font-weight: 500; text-transform: uppercase; letter-spacing: 0.03em; }
    .kpi-value { font-size: 1.55rem; font-weight: 700; color: #0f172a; margin-top: 0.2rem; }
    .kpi-sub { font-size: 0.78rem; color: #94a3b8; margin-top: 0.12rem; }
    .status-badge {
        display: inline-block; padding: 0.18rem 0.6rem; border-radius: 999px;
        font-size: 0.72rem; font-weight: 600;
    }
    .status-em-execucao { background: #dbeafe; color: #1e40af; }
    .status-aprovada { background: #dcfce7; color: #166534; }
    .status-concluida { background: #e0e7ff; color: #3730a3; }
    .status-submetida { background: #fef3c7; color: #92400e; }
    .status-vazio { background: #f1f5f9; color: #475569; }
    .pri-1 { background: #fee2e2; color: #991b1b; font-weight: 700; padding: 2px 8px; border-radius: 6px; }
    .pri-2 { background: #ffedd5; color: #9a3412; font-weight: 600; padding: 2px 8px; border-radius: 6px; }
    .pri-3 { background: #fef9c3; color: #854d0e; padding: 2px 8px; border-radius: 6px; }
    div[data-testid="stSidebar"] { background: #0f172a; }
    div[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    .sidebar-title { font-size: 1.1rem; font-weight: 700; color: white !important; }
    .demo-banner {
        background: #fef3c7; border: 1px solid #f59e0b; color: #92400e;
        padding: 0.55rem 1rem; border-radius: 8px; font-size: 0.85rem; margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=30)
def load_projetos():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM projeto ORDER BY designacao", conn)
    conn.close()
    num_cols = [
        "custos_totais", "adjudicado", "invest_elegivel", "fundo_previsto",
        "fundo_solicitado", "fundo_recebido", "adiantamentos",
        "pct_adiantamento", "pct_exec_fisica", "pct_exec_financeira",
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

@st.cache_data(ttl=30)
def load_tramitacoes():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT t.*, p.designacao
        FROM tramitacao t
        LEFT JOIN projeto p ON p.id = t.projeto_id
        ORDER BY t.data DESC
    """, conn)
    conn.close()
    return df

@st.cache_data(ttl=30)
def load_ocorrencias(projeto_id=None):
    conn = sqlite3.connect(DB_PATH)
    if projeto_id is None:
        df = pd.read_sql_query("""
            SELECT o.*, p.designacao
            FROM ocorrencia o LEFT JOIN projeto p ON p.id = o.projeto_id
            ORDER BY o.data DESC
        """, conn)
    else:
        df = pd.read_sql_query("""
            SELECT * FROM ocorrencia WHERE projeto_id = ? ORDER BY data DESC
        """, conn, params=(projeto_id,))
    conn.close()
    return df

@st.cache_data(ttl=30)
def load_execucao(projeto_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT tipo, adjudicado, realizado FROM execucao_fisica WHERE projeto_id = ?",
        conn, params=(projeto_id,),
    )
    conn.close()
    return df

@st.cache_data(ttl=30)
def load_atencao_manual():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT a.*, p.designacao
        FROM atencao_manual a LEFT JOIN projeto p ON p.id = a.projeto_id
        ORDER BY a.prioridade, a.created DESC
    """, conn)
    conn.close()
    return df

def format_euro(value):
    try:
        if value is None or pd.isna(value):
            return "—"
        return f"€ {float(value):,.0f}".replace(",", " ")
    except Exception:
        return "—"

def format_pct(value):
    try:
        if value is None or pd.isna(value):
            return "—"
        return f"{float(value) * 100:.1f}%"
    except Exception:
        return "—"

def status_class(estado):
    if not estado:
        return "status-vazio"
    e = str(estado).lower()
    if "execução" in e:
        return "status-em-execucao"
    if "aprovad" in e:
        return "status-aprovada"
    if "conclu" in e:
        return "status-concluida"
    if "submet" in e:
        return "status-submetida"
    return "status-vazio"

def collect_attention(df, tram, attn_manual):
    items = []
    for _, r in attn_manual.iterrows():
        items.append({
            "pri": int(r["prioridade"]),
            "tipo": r["tipo"],
            "id": r["projeto_id"],
            "titulo": r["titulo"] or r.get("designacao", ""),
            "detalhe": r["detalhe"],
            "origem": "Manual",
        })
    for _, r in tram.iterrows():
        if str(r.get("resolvido", "")).lower() in ("não", "nao", "n", ""):
            dias = r.get("dias") or 0
            pri = 1 if dias >= 30 else (2 if dias >= 10 else 3)
            items.append({
                "pri": pri,
                "tipo": "Tramitação pendente",
                "id": r["projeto_id"],
                "titulo": r.get("designacao") or f"Projeto {r['projeto_id']}",
                "detalhe": f"{r.get('assunto', '')} · {dias} dias · {r.get('remetente', '')}",
                "origem": "Auto",
            })
    for _, r in df.iterrows():
        if r["estado"] == "Em execução":
            pct = r["pct_exec_fisica"] or 0
            if pct < 0.30 and (r["adjudicado"] or 0) > 0:
                items.append({
                    "pri": 2,
                    "tipo": "Execução física baixa",
                    "id": r["id"],
                    "titulo": r["designacao"],
                    "detalhe": f"Apenas {format_pct(pct)} de execução física com adjudicação de {format_euro(r['adjudicado'])}",
                    "origem": "Auto",
                })
            pct_f = r["pct_exec_financeira"] or 0
            if abs(pct - pct_f) > 0.15 and pct > 0:
                items.append({
                    "pri": 3,
                    "tipo": "Desvio físico/financeiro",
                    "id": r["id"],
                    "titulo": r["designacao"],
                    "detalhe": f"Física {format_pct(pct)} vs Financeira {format_pct(pct_f)}",
                    "origem": "Auto",
                })
    items.sort(key=lambda x: (x["pri"], str(x["id"])))
    return items

with st.sidebar:
    st.markdown('<div class="sidebar-title">DGCF | Gestor de Fundos</div>', unsafe_allow_html=True)
    st.caption(f"Versão {VERSION}")
    st.markdown("---")
    pagina = st.radio(
        "Navegação",
        ["Painel geral", "Atenção", "Projetos", "Tramitações", "Históricos", "Relatórios"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("Município fictício: Vila Nova do Norte")
    st.caption("Dados 100% de demonstração")

df = load_projetos()
tram = load_tramitacoes()
attn_manual = load_atencao_manual()

st.markdown(
    '<div class="demo-banner">⚠️ <b>Demonstração</b> — Todos os dados são fictícios. Não correspondem a nenhum município real.</div>',
    unsafe_allow_html=True,
)

if pagina == "Painel geral":
    st.markdown('<div class="main-header">Painel geral</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Visão global da carteira de candidaturas (dados fictícios)</div>', unsafe_allow_html=True)

    total = len(df)
    em_exec = len(df[df["estado"] == "Em execução"])
    concluidas = len(df[df["estado"] == "Concluída"])
    orcamento = pd.to_numeric(df["custos_totais"], errors="coerce").sum()
    recebido = pd.to_numeric(df["fundo_recebido"], errors="coerce").sum()
    adiant = pd.to_numeric(df["adiantamentos"], errors="coerce").sum()
    media_fis = pd.to_numeric(df["pct_exec_fisica"], errors="coerce").mean()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Projetos</div>
            <div class="kpi-value">{total}</div>
            <div class="kpi-sub">{em_exec} em execução · {concluidas} concluídas</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Orçamento Total</div>
            <div class="kpi-value">{format_euro(orcamento)}</div>
            <div class="kpi-sub">Custos totais dos projetos</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Fundo Recebido</div>
            <div class="kpi-value">{format_euro(recebido)}</div>
            <div class="kpi-sub">Adiantamentos: {format_euro(adiant)}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Execução Física Média</div>
            <div class="kpi-value">{format_pct(media_fis)}</div>
            <div class="kpi-sub">Média de todos os projetos</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Projetos em execução")
        df_exec = df[df["estado"] == "Em execução"].sort_values("pct_exec_fisica", ascending=False)
        for _, row in df_exec.iterrows():
            pct_val = row["pct_exec_fisica"]
            progress_value = 0.0 if pd.isna(pct_val) else max(0.0, min(float(pct_val), 1.0))
            st.markdown(f"**{row['designacao']}**")
            st.caption(f"ID {row['id']} · {row['programa'] or '—'}")
            m1, m2, m3 = st.columns(3)
            m1.metric("Orçamento", format_euro(row["custos_totais"]))
            m2.metric("Recebido", format_euro(row["fundo_recebido"]))
            m3.metric("Exec. física", format_pct(row["pct_exec_fisica"]))
            st.progress(progress_value)
            st.markdown("---")

    with col_b:
        st.subheader("Tramitações por acompanhar")
        pendentes = tram[tram["resolvido"].str.lower().isin(["não", "nao", "n"]) | tram["resolvido"].isna()]
        if pendentes.empty:
            st.info("Não existem tramitações pendentes.")
        else:
            for _, r in pendentes.iterrows():
                st.markdown(f"**{r.get('designacao', '')}**")
                st.caption(f"{r.get('data', '')} · {r.get('remetente', '')} · {r.get('dias', 0)} dias")
                st.write(r.get("assunto", ""))
                st.markdown("---")

elif pagina == "Atenção":
    st.markdown('<div class="main-header">Atenção</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Situações a acompanhar / que podem exigir intervenção</div>', unsafe_allow_html=True)

    items = collect_attention(df, tram, attn_manual)
    st.caption(f"{len(items)} itens de atenção")

    if not items:
        st.success("Nenhum item de atenção no momento.")
    else:
        for it in items:
            pri_html = f'<span class="pri-{it["pri"]}">P{it["pri"]}</span>'
            st.markdown(
                f"{pri_html} &nbsp; **{it['tipo']}** &nbsp;·&nbsp; ID {it['id']} &nbsp;·&nbsp; "
                f"<span style='color:#64748b;font-size:0.8rem'>{it['origem']}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**{it['titulo']}**")
            st.write(it["detalhe"])
            st.markdown("---")

elif pagina == "Projetos":
    st.markdown('<div class="main-header">Projetos</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Lista completa com filtros e ficha detalhada</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 2, 3])
    with c1:
        estados = ["Todos"] + sorted([e for e in df["estado"].dropna().unique().tolist()])
        f_estado = st.selectbox("Estado", estados)
    with c2:
        programas = ["Todos"] + sorted([p for p in df["programa"].dropna().unique().tolist()])
        f_programa = st.selectbox("Programa", programas)
    with c3:
        pesquisa = st.text_input("Pesquisar (nome ou ID)", placeholder="Ex: creche, 9001, saúde...")

    c4, c5 = st.columns(2)
    with c4:
        so_exec = st.checkbox("Só com execução física registada")
    with c5:
        so_recebido = st.checkbox("Só com fundo recebido > 0")

    df_f = df.copy()
    if f_estado != "Todos":
        df_f = df_f[df_f["estado"] == f_estado]
    if f_programa != "Todos":
        df_f = df_f[df_f["programa"] == f_programa]
    if pesquisa:
        q = pesquisa.lower()
        df_f = df_f[
            df_f["designacao"].str.lower().str.contains(q, na=False)
            | df_f["codigo"].astype(str).str.contains(q, na=False)
            | df_f["programa"].str.lower().str.contains(q, na=False)
        ]
    if so_exec:
        df_f = df_f[df_f["pct_exec_fisica"].fillna(0) > 0]
    if so_recebido:
        df_f = df_f[df_f["fundo_recebido"].fillna(0) > 0]

    st.caption(f"{len(df_f)} projeto(s) encontrado(s)")

    for _, row in df_f.iterrows():
        estado = row["estado"] or "Sem estado"
        cls = status_class(row["estado"])
        pct_val = row["pct_exec_fisica"]
        progress_value = 0.0 if pd.isna(pct_val) else max(0.0, min(float(pct_val), 1.0))

        with st.expander(f"**{row['designacao']}**  ·  ID {row['id']}  ·  {estado}"):
            left, right = st.columns([2, 1])
            with left:
                st.markdown(f"**Programa:** {row['programa'] or '—'}  \n**Aviso:** {row['aviso'] or '—'}  \n**Área:** {row['area'] or '—'}")
                st.markdown("##### Execução Financeira")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Custos totais", format_euro(row["custos_totais"]))
                m2.metric("Adjudicado", format_euro(row["adjudicado"]))
                m3.metric("Fundo recebido", format_euro(row["fundo_recebido"]))
                m4.metric("Adiantamentos", format_euro(row["adiantamentos"]))
                st.markdown("##### Execução Física e Financeira")
                p1, p2, p3 = st.columns(3)
                p1.metric("% Exec. Física", format_pct(row["pct_exec_fisica"]))
                p2.metric("% Exec. Financeira", format_pct(row["pct_exec_financeira"]))
                p3.metric("% Adiantamento", format_pct(row["pct_adiantamento"]))
            with right:
                st.markdown(f'<span class="status-badge {cls}">{estado}</span>', unsafe_allow_html=True)
                st.progress(progress_value, text=f"Execução física: {format_pct(row['pct_exec_fisica'])}")

            exec_df = load_execucao(int(row["id"]))
            if not exec_df.empty:
                st.markdown("##### Detalhe execução física")
                st.dataframe(
                    exec_df.rename(columns={"tipo": "Tipo", "adjudicado": "Adjudicado (€)", "realizado": "Realizado (€)"}),
                    use_container_width=True, hide_index=True,
                )

            ocorr = load_ocorrencias(int(row["id"]))
            if not ocorr.empty:
                st.markdown("##### Histórico de ocorrências")
                st.dataframe(
                    ocorr[["data", "descricao", "procedimento", "relacionado", "estado", "parecer"]].rename(
                        columns={
                            "data": "Data", "descricao": "Descrição", "procedimento": "Procedimento",
                            "relacionado": "Relacionado", "estado": "Estado", "parecer": "Parecer",
                        }
                    ),
                    use_container_width=True, hide_index=True,
                )

elif pagina == "Tramitações":
    st.markdown('<div class="main-header">Tramitações</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Registo de movimentos e processos com as autoridades de gestão</div>', unsafe_allow_html=True)

    filtro_res = st.selectbox("Resolvido", ["Todos", "Pendentes", "Resolvidos"])
    t = tram.copy()
    if filtro_res == "Pendentes":
        t = t[t["resolvido"].str.lower().isin(["não", "nao", "n"]) | t["resolvido"].isna()]
    elif filtro_res == "Resolvidos":
        t = t[t["resolvido"].str.lower() == "sim"]

    st.caption(f"{len(t)} registo(s)")
    if t.empty:
        st.info("Sem tramitações para os filtros selecionados.")
    else:
        show = t[["data", "projeto_id", "designacao", "remetente", "assunto", "processo", "dias", "resolvido", "despacho"]].copy()
        show.columns = ["Data", "ID", "Projeto", "Remetente", "Assunto", "Processo", "Dias", "Resolvido", "Despacho"]
        st.dataframe(show, use_container_width=True, hide_index=True)

elif pagina == "Históricos":
    st.markdown('<div class="main-header">Históricos por projeto</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Linha do tempo de eventos e decisões</div>', unsafe_allow_html=True)

    projetos_com_hist = load_ocorrencias()
    ids = sorted(projetos_com_hist["projeto_id"].dropna().unique().tolist())
    nomes = {int(r["id"]): r["designacao"] for _, r in df.iterrows()}
    opcoes = ["Todos"] + [f"{i} — {nomes.get(i, '')}" for i in ids]
    escolha = st.selectbox("Projeto", opcoes)

    if escolha == "Todos":
        hist = projetos_com_hist
    else:
        pid = int(escolha.split("—")[0].strip())
        hist = load_ocorrencias(pid)

    if hist.empty:
        st.info("Sem histórico registado.")
    else:
        cols = ["data", "projeto_id", "descricao", "procedimento", "relacionado", "estado", "parecer"]
        cols = [c for c in cols if c in hist.columns]
        st.dataframe(
            hist[cols].rename(columns={
                "data": "Data", "projeto_id": "ID", "descricao": "Descrição",
                "procedimento": "Procedimento", "relacionado": "Relacionado",
                "estado": "Estado", "parecer": "Parecer",
            }),
            use_container_width=True, hide_index=True,
        )

elif pagina == "Relatórios":
    st.markdown('<div class="main-header">Relatórios</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Resumos e exportação</div>', unsafe_allow_html=True)

    st.subheader("Resumo por Estado")
    resumo = df.groupby("estado", dropna=False).agg(
        N=("id", "count"),
        Custos=("custos_totais", "sum"),
        Recebido=("fundo_recebido", "sum"),
        Adiantamentos=("adiantamentos", "sum"),
    ).reset_index()
    resumo["estado"] = resumo["estado"].fillna("(sem estado)")
    st.dataframe(resumo, use_container_width=True, hide_index=True)

    st.subheader("Resumo por Programa")
    resumo_p = df.groupby("programa", dropna=False).agg(
        N=("id", "count"),
        Custos=("custos_totais", "sum"),
        Recebido=("fundo_recebido", "sum"),
    ).reset_index().sort_values("N", ascending=False)
    resumo_p["programa"] = resumo_p["programa"].fillna("(sem programa)")
    st.dataframe(resumo_p, use_container_width=True, hide_index=True)

    st.subheader("Exportar")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Descarregar lista de projetos (CSV)", csv, "dgcf_demo_projetos.csv", "text/csv")
