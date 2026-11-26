"""
DGCF | Gestor de Fundos
Versão P001 · 0.1
Protótipo offline — Município de Barcelos
Python + SQLite + Streamlit
"""

import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

# -------------------------------------------------
# Configuração
# -------------------------------------------------
VERSION = "P001 · 0.1"

st.set_page_config(
    page_title=f"DGCF | Gestor de Fundos ({VERSION})",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = Path(__file__).parent / "dgcf_gestor_fundos.db"

# -------------------------------------------------
# CSS personalizado (visual moderno tipo dashboard)
# -------------------------------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #64748b;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .kpi-label {
        font-size: 0.8rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 0.25rem;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 0.15rem;
    }
    .project-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.9rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: box-shadow 0.15s;
    }
    .project-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-em-execucao { background: #dbeafe; color: #1e40af; }
    .status-aprovada { background: #dcfce7; color: #166534; }
    .status-concluida { background: #e0e7ff; color: #3730a3; }
    .status-submetida { background: #fef3c7; color: #92400e; }
    .status-vazio { background: #f1f5f9; color: #475569; }
    .progress-bar-bg {
        background: #e2e8f0;
        border-radius: 999px;
        height: 8px;
        margin-top: 0.4rem;
        overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #3b82f6, #2563eb);
    }
    div[data-testid="stSidebar"] {
        background: #0f172a;
    }
    div[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    .sidebar-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: white !important;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Funções de dados
# -------------------------------------------------
@st.cache_data(ttl=60)
def load_projetos():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT 
            id, codigo, designacao, estado, programa, aviso,
            custos_totais, adjudicado, invest_elegivel,
            fundo_previsto, fundo_solicitado, fundo_recebido, adiantamentos,
            pct_adiantamento, pct_exec_fisica, pct_exec_financeira, pct_inv_elegivel,
            area
        FROM projeto
        ORDER BY designacao
    """, conn)
    conn.close()
    return df

@st.cache_data(ttl=60)
def load_ocorrencias(projeto_id: int):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT data, descricao, procedimento, relacionado, estado, parecer
        FROM ocorrencia
        WHERE projeto_id = ?
        ORDER BY data DESC
    """, conn, params=(projeto_id,))
    conn.close()
    return df

@st.cache_data(ttl=60)
def load_execucao_fisica(projeto_id: int):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT tipo, adjudicado, realizado, pct
        FROM execucao_fisica
        WHERE projeto_id = ?
    """, conn, params=(projeto_id,))
    conn.close()
    return df

def format_euro(value):
    if pd.isna(value) or value is None:
        return "—"
    return f"€ {value:,.0f}".replace(",", " ")

def format_pct(value):
    if pd.isna(value) or value is None:
        return "—"
    return f"{value * 100:.1f}%"

def status_class(estado):
    if not estado:
        return "status-vazio"
    e = estado.lower()
    if "execução" in e:
        return "status-em-execucao"
    if "aprovad" in e:
        return "status-aprovada"
    if "conclu" in e:
        return "status-concluida"
    if "submet" in e:
        return "status-submetida"
    return "status-vazio"

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">DGCF | Gestor de Fundos</div>', unsafe_allow_html=True)
    st.caption(f"Versão {VERSION}")
    st.markdown("---")
    
    pagina = st.radio(
        "Navegação",
        ["Painel de Controlo", "Candidaturas e Projetos", "Relatórios"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.caption("Município de Barcelos")
    st.caption("Protótipo offline · PRR / Fundos Europeus")

# -------------------------------------------------
# Carregar dados
# -------------------------------------------------
df = load_projetos()

# -------------------------------------------------
# PÁGINA: Painel de Controlo
# -------------------------------------------------
if pagina == "Painel de Controlo":
    st.markdown('<div class="main-header">Painel de Controlo</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Visão geral das candidaturas e execução PRR</div>', unsafe_allow_html=True)

    # KPIs
    total = len(df)
    em_execucao = len(df[df["estado"] == "Em execução"])
    concluidas = len(df[df["estado"] == "Concluída"])
    aprovadas = len(df[df["estado"] == "Aprovada"])

    orcamento_total = df["custos_totais"].sum(skipna=True)
    fundo_recebido = df["fundo_recebido"].sum(skipna=True)
    adiantamentos = df["adiantamentos"].sum(skipna=True)
    media_fisica = df["pct_exec_fisica"].mean(skipna=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Projetos</div>
            <div class="kpi-value">{total}</div>
            <div class="kpi-sub">{em_execucao} em execução · {concluidas} concluídas</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Orçamento Total</div>
            <div class="kpi-value">{format_euro(orcamento_total)}</div>
            <div class="kpi-sub">Custos totais dos projetos</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Fundo Recebido</div>
            <div class="kpi-value">{format_euro(fundo_recebido)}</div>
            <div class="kpi-sub">Adiantamentos: {format_euro(adiantamentos)}</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Execução Física Média</div>
            <div class="kpi-value">{format_pct(media_fisica)}</div>
            <div class="kpi-sub">Média de todos os projetos</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Projetos em execução (destaque)
    st.subheader("Projetos em execução")
    df_exec = df[df["estado"] == "Em execução"].sort_values("pct_exec_fisica", ascending=False)

    if df_exec.empty:
        st.info("Não existem projetos em execução neste momento.")
    else:
        for _, row in df_exec.iterrows():
            pct = row["pct_exec_fisica"] * 100 if pd.notna(row["pct_exec_fisica"]) else 0
            st.markdown(f"""
            <div class="project-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div style="font-weight:600; font-size:1.05rem; color:#0f172a;">{row['designacao']}</div>
                        <div style="font-size:0.85rem; color:#64748b; margin-top:0.2rem;">
                            ID {row['id']} · {row['programa'] or '—'}
                        </div>
                    </div>
                    <span class="status-badge status-em-execucao">Em execução</span>
                </div>
                <div style="display:flex; gap:2rem; margin-top:0.9rem; font-size:0.9rem;">
                    <div><span style="color:#64748b;">Orçamento</span><br><strong>{format_euro(row['custos_totais'])}</strong></div>
                    <div><span style="color:#64748b;">Adjudicado</span><br><strong>{format_euro(row['adjudicado'])}</strong></div>
                    <div><span style="color:#64748b;">Recebido</span><br><strong>{format_euro(row['fundo_recebido'])}</strong></div>
                    <div><span style="color:#64748b;">Exec. Física</span><br><strong>{format_pct(row['pct_exec_fisica'])}</strong></div>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width:{min(pct,100)}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------
# PÁGINA: Candidaturas e Projetos
# -------------------------------------------------
elif pagina == "Candidaturas e Projetos":
    st.markdown('<div class="main-header">Candidaturas e Projetos</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Lista completa com filtros e ficha detalhada</div>', unsafe_allow_html=True)

    # Filtros
    col_f1, col_f2, col_f3 = st.columns([2, 2, 3])
    with col_f1:
        estados = ["Todos"] + sorted([e for e in df["estado"].dropna().unique().tolist()])
        filtro_estado = st.selectbox("Estado", estados)
    with col_f2:
        programas = ["Todos"] + sorted([p for p in df["programa"].dropna().unique().tolist()])
        filtro_programa = st.selectbox("Programa / Investimento", programas)
    with col_f3:
        pesquisa = st.text_input("Pesquisar (nome ou ID)", placeholder="Ex: creche, 7822, saúde...")

    # Aplicar filtros
    df_filtrado = df.copy()
    if filtro_estado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["estado"] == filtro_estado]
    if filtro_programa != "Todos":
        df_filtrado = df_filtrado[df_filtrado["programa"] == filtro_programa]
    if pesquisa:
        q = pesquisa.lower()
        df_filtrado = df_filtrado[
            df_filtrado["designacao"].str.lower().str.contains(q, na=False) |
            df_filtrado["codigo"].astype(str).str.contains(q, na=False) |
            df_filtrado["programa"].str.lower().str.contains(q, na=False)
        ]

    st.caption(f"{len(df_filtrado)} projeto(s) encontrado(s)")

    # Lista de projetos
    for _, row in df_filtrado.iterrows():
        estado = row["estado"] or "Sem estado"
        cls = status_class(row["estado"])
        pct = (row["pct_exec_fisica"] or 0) * 100

        with st.expander(f"**{row['designacao']}**  ·  ID {row['id']}  ·  {estado}"):
            c1, c2 = st.columns([2, 1])

            with c1:
                st.markdown(f"""
                **Programa:** {row['programa'] or '—'}  
                **Aviso:** {row['aviso'] or '—'}  
                **Área:** {row['area'] or '—'}
                """)

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

            with c2:
                st.markdown(f'<span class="status-badge {cls}">{estado}</span>', unsafe_allow_html=True)
                st.progress(min(pct / 100, 1.0), text=f"Execução física: {format_pct(row['pct_exec_fisica'])}")

            # Histórico de ocorrências
            ocorr = load_ocorrencias(int(row["id"]))
            if not ocorr.empty:
                st.markdown("##### Histórico de ocorrências")
                st.dataframe(
                    ocorr.rename(columns={
                        "data": "Data",
                        "descricao": "Descrição",
                        "procedimento": "Procedimento",
                        "relacionado": "Relacionado",
                        "estado": "Estado",
                        "parecer": "Parecer"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.caption("Sem histórico de ocorrências registado para este projeto.")

            # Execução física detalhada
            exec_fis = load_execucao_fisica(int(row["id"]))
            if not exec_fis.empty:
                st.markdown("##### Detalhe execução física")
                st.dataframe(
                    exec_fis.rename(columns={
                        "tipo": "Tipo",
                        "adjudicado": "Adjudicado (€)",
                        "realizado": "Realizado (€)",
                        "pct": "%"
                    }),
                    use_container_width=True,
                    hide_index=True
                )

# -------------------------------------------------
# PÁGINA: Relatórios
# -------------------------------------------------
elif pagina == "Relatórios":
    st.markdown('<div class="main-header">Relatórios e Exportação</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Listagens e exportação para Excel</div>', unsafe_allow_html=True)

    st.subheader("Resumo por Estado")
    resumo_estado = df.groupby("estado", dropna=False).agg(
        N=("id", "count"),
        Custos=("custos_totais", "sum"),
        Recebido=("fundo_recebido", "sum"),
        Adiantamentos=("adiantamentos", "sum")
    ).reset_index()
    resumo_estado["estado"] = resumo_estado["estado"].fillna("(sem estado)")
    st.dataframe(resumo_estado, use_container_width=True, hide_index=True)

    st.subheader("Resumo por Programa")
    resumo_prog = df.groupby("programa", dropna=False).agg(
        N=("id", "count"),
        Custos=("custos_totais", "sum"),
        Recebido=("fundo_recebido", "sum")
    ).reset_index().sort_values("N", ascending=False)
    resumo_prog["programa"] = resumo_prog["programa"].fillna("(sem programa)")
    st.dataframe(resumo_prog, use_container_width=True, hide_index=True)

    st.subheader("Exportar dados")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descarregar lista completa (CSV)",
        data=csv,
        file_name="dgcf_projetos_prr.csv",
        mime="text/csv"
    )

    st.caption("Os dados são exportados a partir da base de dados local SQLite.")
