"""
ARGUS — AI Financial Research Intelligence
See Beyond the Narrative | Independent Prototype for Charles Schwab Investment Research
=======================================================================================
Main Streamlit Application (`app.py`)
Run with:
    streamlit run app.py
"""

from __future__ import annotations
import json
import os
from typing import Dict, Any, List

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

import argus_engine as ae
import research_lab as rl


# ==============================================================================
# PAGE CONFIGURATION & INSTITUTIONAL DARK CHARCOAL AESTHETIC
# ==============================================================================
st.set_page_config(
    page_title="ARGUS | AI Financial Research Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

INSTITUTIONAL_CSS = """
<style>
    /* Institutional Finance Aesthetic: Dark Charcoal Background, Restrained Accents */
    .stApp {
        background-color: #0D1117;
        color: #E6EDF3;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #131822;
        border-right: 1px solid #262E3D;
    }
    .argus-header {
        background: linear-gradient(90deg, #131A26 0%, #172234 100%);
        border: 1px solid #28344A;
        border-left: 4px solid #38BDF8;
        border-radius: 6px;
        padding: 18px 24px;
        margin-bottom: 20px;
    }
    .argus-title {
        font-size: 1.65rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        color: #F8FAFC;
        margin: 0;
    }
    .argus-subtitle {
        font-size: 0.92rem;
        color: #94A3B8;
        margin-top: 4px;
        margin-bottom: 0;
    }
    .kpi-card {
        background-color: #151B26;
        border: 1px solid #262F40;
        border-radius: 6px;
        padding: 16px 18px;
        height: 100%;
    }
    .kpi-label {
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #8B9BB4;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.55rem;
        font-weight: 700;
        color: #F1F5F9;
        font-variant-numeric: tabular-nums;
    }
    .kpi-sub {
        font-size: 0.80rem;
        color: #64748B;
        margin-top: 4px;
    }
    .evidence-box {
        background-color: #141A24;
        border: 1px solid #263042;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .excerpt-quote {
        background-color: #0F141C;
        border-left: 3px solid #38BDF8;
        padding: 12px 16px;
        font-style: italic;
        color: #CBD5E1;
        border-radius: 0 4px 4px 0;
        margin: 8px 0;
    }
    .badge-mismatch {
        background-color: rgba(239, 68, 68, 0.16);
        color: #FCA5A5;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-divergence {
        background-color: rgba(245, 158, 11, 0.16);
        color: #FCD34D;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-consistent {
        background-color: rgba(16, 185, 129, 0.16);
        color: #6EE7B7;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-insufficient {
        background-color: rgba(148, 163, 184, 0.16);
        color: #CBD5E1;
        border: 1px solid rgba(148, 163, 184, 0.4);
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; }
    h3 { margin-top: 0.4rem; }
    h4 { margin-top: 1.4rem; color: #CBD5E1; }
    button[data-baseweb="tab"] { font-weight: 600; letter-spacing: 0.01em; }
    .rl-note {
        background-color: #131C2A;
        border: 1px solid #263A52;
        border-left: 3px solid #38BDF8;
        border-radius: 4px;
        padding: 10px 14px;
        font-size: 0.86rem;
        color: #B6C4D9;
        margin: 8px 0 14px 0;
    }
    .chain-step {
        background-color: #161E2E;
        border: 1px solid #2B3954;
        border-radius: 6px;
        padding: 10px 14px;
        text-align: center;
        font-size: 0.84rem;
        color: #E2E8F0;
    }
</style>
"""
st.markdown(INSTITUTIONAL_CSS, unsafe_allow_html=True)


# ==============================================================================
# DATA LOADING & SESSION STATE
# ==============================================================================
@st.cache_data
def get_base_data() -> Dict[str, Any]:
    return ae.load_argus_data()


base_data = get_base_data()
if "custom_comparisons" not in st.session_state:
    st.session_state["custom_comparisons"] = []

all_comparisons: List[Dict[str, Any]] = base_data["comparisons"] + st.session_state["custom_comparisons"]
metrics_df = pd.DataFrame(base_data["metrics"]).sort_values("period_order")
manifest = base_data["manifest"]


def render_category_badge(category: str) -> str:
    if category == ae.CATEGORY_MISMATCH:
        return f'<span class="badge-mismatch">1. {category}</span>'
    if category == ae.CATEGORY_DIVERGENCE:
        return f'<span class="badge-divergence">2. {category}</span>'
    if category == ae.CATEGORY_NO_DISCREPANCY:
        return f'<span class="badge-consistent">3. {category}</span>'
    return f'<span class="badge-insufficient">4. {category}</span>'


# ==============================================================================
# SIDEBAR CONTROLS & SYSTEM STATUS
# ==============================================================================
with st.sidebar:
    st.markdown("### 🏛️ ARGUS CONTROL PANEL")
    st.caption("Proposed User: **Charles Schwab Investment Research Team** *(Independent Prototype)*")

    selected_company = st.selectbox(
        "Research Subject (Company)",
        options=["NVIDIA Corporation (NASDAQ: NVDA)"],
        index=0,
    )

    available_periods = ["All Periods (Q1 FY26 – Q2 FY27)"] + list(metrics_df["period"].unique())
    selected_period_filter = st.selectbox(
        "Reporting Period Focus",
        options=available_periods,
        index=0,
    )

    selected_category_filter = st.multiselect(
        "Filter Findings by Category",
        options=ae.VALID_CATEGORIES,
        default=ae.VALID_CATEGORIES,
    )

    st.markdown("---")
    st.markdown("#### Matching Engine Status")
    st.info(ae.ENGINE_STATUS_MESSAGE)
    if os.environ.get("GEMINI_API_KEY"):
        st.caption("A GEMINI_API_KEY is set in this environment but is not used by any code path.")
    st.caption("Calculations and classifications are deterministic Python.")

    st.markdown("#### 📜 Auditable Chain Guarantee")
    st.caption(
        "1. **Company Statement** (Exact Excerpt)\n"
        "2. **Original Source** (SEC / IR Link & Date)\n"
        "3. **Financial Metric** (GAAP / Non-GAAP & Units)\n"
        "4. **Deterministic Python Check** (Formula)\n"
        "5. **Analyst Finding** (4-Tier Classification)"
    )


# ==============================================================================
# TOP BANNER
# ==============================================================================
st.markdown(
    """
    <div class="argus-header">
        <div class="argus-title">ARGUS — See Beyond the Narrative</div>
        <div class="argus-subtitle">
            Financial Research Intelligence Prototype &nbsp;|&nbsp;
            Subject: <strong>NVIDIA Corp. (NVDA, CIK: 0001045810)</strong> &nbsp;|&nbsp;
            Built for: <strong>Charles Schwab Equity Research Workflow</strong> (Independent Competition Prototype)
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Filter comparisons based on sidebar
filtered_comparisons = [
    c for c in all_comparisons
    if c["category"] in selected_category_filter
    and (
        selected_period_filter == "All Periods (Q1 FY26 – Q2 FY27)"
        or selected_period_filter in c["baseline_period"]
        or selected_period_filter in c["target_period"]
    )
]

if selected_period_filter == "All Periods (Q1 FY26 – Q2 FY27)":
    filtered_metrics_df = metrics_df.copy()
else:
    filtered_metrics_df = metrics_df[metrics_df["period"] == selected_period_filter].copy()


# ==============================================================================
# APPLICATION TABS
# ==============================================================================
tab_exec, tab_timeline, tab_explorer, tab_inspector, tab_research, tab_ai_eval = st.tabs([
    "Dashboard",
    "Timeline",
    "Evidence Explorer",
    "Finding Inspector",
    "Research Lab",
    "Validation",
])


# ==============================================================================
# TAB A: EXECUTIVE DASHBOARD
# ==============================================================================
with tab_exec:
    # KPI Row
    total_sources = len(manifest["sources"])
    total_comparisons = len(all_comparisons)
    mismatch_count = sum(1 for c in all_comparisons if c["category"] == ae.CATEGORY_MISMATCH)
    divergence_count = sum(1 for c in all_comparisons if c["category"] == ae.CATEGORY_DIVERGENCE)
    consistent_count = sum(1 for c in all_comparisons if c["category"] == ae.CATEGORY_NO_DISCREPANCY)
    insufficient_count = sum(1 for c in all_comparisons if c["category"] == ae.CATEGORY_INSUFFICIENT)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(
            f"""<div class="kpi-card">
                <div class="kpi-label">Verified Filings Reviewed</div>
                <div class="kpi-value">{total_sources}</div>
                <div class="kpi-sub">Q2 FY26–Q2 FY27 Releases & FY26 10-K</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class="kpi-card">
                <div class="kpi-label">Auditable Comparisons</div>
                <div class="kpi-value">{total_comparisons}</div>
                <div class="kpi-sub">100% Deterministic Python Verified</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""<div class="kpi-card">
                <div class="kpi-label">Verified Numerical Mismatch</div>
                <div class="kpi-value" style="color:#FCA5A5;">{mismatch_count}</div>
                <div class="kpi-sub">OpEx Guidance & SBC Restatement</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""<div class="kpi-card">
                <div class="kpi-label">Narrative–Metric Divergence</div>
                <div class="kpi-value" style="color:#FCD34D;">{divergence_count}</div>
                <div class="kpi-sub">Q2 FY27 OCF Drop & Q3 Margin Guide</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col5:
        st.markdown(
            f"""<div class="kpi-card">
                <div class="kpi-label">Consistent / Insufficient</div>
                <div class="kpi-value" style="color:#6EE7B7;">{consistent_count} / {insufficient_count}</div>
                <div class="kpi-sub">{consistent_count} corroborated | {insufficient_count} evidence gap</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.caption(
        "Audit chain: company statement → original source (URL & date) → financial metric (units) → "
        "deterministic Python check → analyst classification."
    )

    st.markdown("### Executive Summary: NVIDIA (Q1 FY26 – Q2 FY27)")
    st.markdown(
        rl.md_safe(
            "- **Corroborated:** Data Center revenue rose from $39,100M (Q1 FY26) to $89,000M (Q2 FY27), supporting the demand narrative.\n"
            "- **Research lead:** Q2 FY27 revenue grew +17.90% QoQ while operating cash flow fell -52.18% QoQ "
            "as accounts receivable rose +$22,349M (DSO 45.4 → 59.6 days).\n"
            "- **Numerical mismatches:** FY26 OpEx growth (40.66% GAAP) exceeded the \"high-30% range\" guidance; "
            "the Q1 FY27 SBC change restated Q4 FY26 Non-GAAP OpEx from $5,102M to $6,666M (+$1,564M)."
        )
    )

    # Executive Charts Row
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_rev_ocf = make_subplots(specs=[[{"secondary_y": True}]])
        fig_rev_ocf.add_trace(
            go.Bar(
                x=metrics_df["period"],
                y=metrics_df["revenue_m"],
                name="Total Revenue ($M)",
                marker_color="#38BDF8",
                opacity=0.85,
            ),
            secondary_y=False,
        )
        fig_rev_ocf.add_trace(
            go.Bar(
                x=metrics_df["period"],
                y=metrics_df["operating_cash_flow_m"],
                name="Operating Cash Flow ($M)",
                marker_color="#10B981",
                opacity=0.85,
            ),
            secondary_y=False,
        )
        fig_rev_ocf.add_trace(
            go.Scatter(
                x=metrics_df["period"],
                y=metrics_df["accounts_receivable_m"],
                name="Accounts Receivable ($M)",
                mode="lines+markers",
                line=dict(color="#F59E0B", width=3),
                marker=dict(size=8),
            ),
            secondary_y=True,
        )
        fig_rev_ocf.update_layout(
            title=dict(text="Revenue, Operating Cash Flow & Receivables", font=dict(size=15), x=0.0, xanchor="left"),
            template="plotly_dark",
            paper_bgcolor="#151B26",
            plot_bgcolor="#151B26",
            barmode="group",
            height=430,
            legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="left", x=0, font=dict(size=11)),
            margin=dict(l=40, r=40, t=50, b=40),
        )
        fig_rev_ocf.update_yaxes(title_text="Revenue & OCF ($M)", secondary_y=False)
        fig_rev_ocf.update_yaxes(title_text="Accounts Receivable ($M)", secondary_y=True)
        st.plotly_chart(fig_rev_ocf, use_container_width=True)
        st.caption("Source: NVIDIA Q1 FY26–Q2 FY27 earnings releases & FY26 Form 10-K. Units: $ in millions.")

    with chart_col2:
        fig_opex = go.Figure()
        fig_opex.add_trace(
            go.Scatter(
                x=metrics_df["period"],
                y=metrics_df["gaap_opex_m"],
                name="GAAP OpEx ($M)",
                mode="lines+markers",
                line=dict(color="#F43F5E", width=3),
            )
        )
        fig_opex.add_trace(
            go.Scatter(
                x=metrics_df["period"],
                y=metrics_df["nongaap_opex_reported_m"],
                name="Non-GAAP OpEx (As Originally Reported, $M)",
                mode="lines+markers",
                line=dict(color="#38BDF8", width=3, dash="dot"),
            )
        )
        fig_opex.add_trace(
            go.Scatter(
                x=metrics_df["period"],
                y=metrics_df["nongaap_opex_sbc_restated_m"],
                name="Non-GAAP OpEx (SBC-Adjusted Like-for-Like, $M)",
                mode="lines+markers",
                line=dict(color="#A855F7", width=3),
            )
        )
        fig_opex.update_layout(
            title=dict(text="Operating Expenses: GAAP vs. Non-GAAP (Original vs. SBC-Restated)", font=dict(size=15), x=0.0, xanchor="left"),
            template="plotly_dark",
            paper_bgcolor="#151B26",
            plot_bgcolor="#151B26",
            height=430,
            legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="left", x=0, font=dict(size=11)),
            margin=dict(l=40, r=40, t=50, b=40),
            yaxis_title="Operating Expenses ($M)",
        )
        st.plotly_chart(fig_opex, use_container_width=True)
        st.caption("Source: NVIDIA Q2 FY26–Q2 FY27 GAAP-to-Non-GAAP Reconciliations. Units: $ in millions.")

    st.markdown("#### Summary of Verified Findings")
    summary_rows = []
    for c in filtered_comparisons:
        summary_rows.append({
            "ID": c["comparison_id"],
            "Comparison Title": c["title"],
            "Periods": f"{c['baseline_period']} → {c['target_period']}",
            "Finding Category": c["category"],
            "Concept Match Score (local)": c["matching_metadata"]["ai_semantic_score"],
            "Keyword Score": c["matching_metadata"]["keyword_overlap_score"],
            "Deterministic Delta": c["metric_verification"]["calculated_delta"],
            "Source Document": c["statement_origin"]["source_id"],
        })
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)


# ==============================================================================
# TAB B: NARRATIVE-VERSUS-METRICS TIMELINE
# ==============================================================================
with tab_timeline:
    st.markdown("### Narrative vs. Metrics (Q1 FY26 – Q2 FY27)")
    st.caption("Management narrative alongside reported GAAP / Non-GAAP metrics, units, and filing links.")

    metric_selector = st.selectbox(
        "Select Primary Financial Metric to Overlay on Narrative Timeline",
        options=[
            ("revenue_m", "Total Consolidated Revenue ($ in millions)"),
            ("data_center_rev_m", "Data Center Segment Revenue ($ in millions)"),
            ("gaap_gross_margin_pct", "GAAP Gross Margin (%)"),
            ("operating_cash_flow_m", "GAAP Operating Cash Flow ($ in millions)"),
            ("free_cash_flow_m", "Free Cash Flow ($ in millions)"),
            ("accounts_receivable_m", "Accounts Receivable, Net ($ in millions)"),
            ("inventories_m", "Inventories ($ in millions)"),
        ],
        format_func=lambda x: x[1],
    )
    metric_col, metric_label = metric_selector

    fig_timeline = go.Figure()
    fig_timeline.add_trace(
        go.Scatter(
            x=metrics_df["period"],
            y=metrics_df[metric_col],
            mode="lines+markers+text",
            text=[f"{v:,.1f}" for v in metrics_df[metric_col]],
            textposition="top center",
            line=dict(color="#38BDF8", width=4),
            marker=dict(size=12, color="#0D1117", line=dict(color="#38BDF8", width=3)),
            name=metric_label,
        )
    )
    fig_timeline.update_layout(
        title=dict(text=f"NVIDIA: {metric_label}", font=dict(size=15), x=0.0, xanchor="left"),
        template="plotly_dark",
        paper_bgcolor="#151B26",
        plot_bgcolor="#151B26",
        height=340,
        margin=dict(l=40, r=40, t=55, b=35),
        yaxis_title=metric_label,
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

    st.markdown("#### Verified Financial Table by Period")
    display_df = filtered_metrics_df[[
        "period", "period_ended", "revenue_m", "data_center_rev_m", "gaap_gross_margin_pct",
        "gaap_opex_m", "gaap_net_income_m", "operating_cash_flow_m", "free_cash_flow_m",
        "accounts_receivable_m", "inventories_m", "units", "source_id", "source_url"
    ]].rename(columns={
        "period": "Period",
        "period_ended": "Period Ended",
        "revenue_m": "Revenue ($M)",
        "data_center_rev_m": "Data Center ($M)",
        "gaap_gross_margin_pct": "GAAP GM (%)",
        "gaap_opex_m": "GAAP OpEx ($M)",
        "gaap_net_income_m": "GAAP Net Inc ($M)",
        "operating_cash_flow_m": "Operating CF ($M)",
        "free_cash_flow_m": "Free CF ($M)",
        "accounts_receivable_m": "Accounts Rec ($M)",
        "inventories_m": "Inventories ($M)",
        "units": "Units",
        "source_id": "Source ID",
        "source_url": "Filing URL",
    })
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("#### Source Filings (newest first)")
    for src in reversed(manifest["sources"]):
        with st.expander(f"{src['reporting_period']} (Published: {src['publication_date']}) — {src['title']}", expanded=False):
            st.markdown(f"**Primary Source URL:** [{src['url']}]({src['url']}) &nbsp;|&nbsp; **Mirror / SEC Filing:** [{src['sec_mirror_url']}]({src['sec_mirror_url']})")
            st.markdown("**Extracted Financial Metrics (Verified with Units):**")
            for m_item in src["extracted_metrics"]:
                st.markdown(f"- {rl.md_safe(m_item)}")


# ==============================================================================
# TAB C: EVIDENCE EXPLORER & INTERACTIVE RELATIONSHIP GRAPH
# ==============================================================================
with tab_explorer:
    st.markdown("### Evidence Explorer")
    st.caption("Select a comparison to inspect the full chain: statements, sources, dates, formula, and evidence.")

    selected_comp_id = st.selectbox(
        "Select Comparison to Inspect in Evidence Explorer",
        options=[c["comparison_id"] for c in all_comparisons],
        format_func=lambda cid: next(f"{c['comparison_id']} — {c['title']} [{c['category']}]" for c in all_comparisons if c["comparison_id"] == cid),
    )
    comp = next(c for c in all_comparisons if c["comparison_id"] == selected_comp_id)

    # Build Interactive Plotly Evidence Network Graph for the selected comparison
    nodes_x = [0.0, 1.0, 1.0, 2.0, 3.0]
    nodes_y = [0.5, 0.85, 0.15, 0.5, 0.5]
    node_labels = [
        f"1. Origin Statement<br>({comp['statement_origin']['reporting_period']})",
        f"2A. Follow-Up Filing<br>({comp['follow_up_statement']['reporting_period']})",
        f"2B. Reported Metric<br>{comp['metric_verification']['metric_name'][:28]}...",
        f"3. Python Verification<br>Concept match={comp['matching_metadata']['ai_semantic_score']:.2f}",
        f"4. Analyst Finding<br>{comp['category']}",
    ]
    node_colors = ["#38BDF8", "#818CF8", "#34D399", "#A855F7", "#F59E0B" if "divergence" in comp["category"].lower() else ("#EF4444" if "mismatch" in comp["category"].lower() else "#10B981")]

    edges_x = []
    edges_y = []
    edge_pairs = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)]
    for u, v in edge_pairs:
        edges_x.extend([nodes_x[u], nodes_x[v], None])
        edges_y.extend([nodes_y[u], nodes_y[v], None])

    fig_graph = go.Figure()
    fig_graph.add_trace(
        go.Scatter(
            x=edges_x,
            y=edges_y,
            mode="lines",
            line=dict(color="#475569", width=2.5),
            hoverinfo="none",
            showlegend=False,
        )
    )
    fig_graph.add_trace(
        go.Scatter(
            x=nodes_x,
            y=nodes_y,
            mode="markers+text",
            text=node_labels,
            textposition="bottom center",
            marker=dict(size=34, color=node_colors, line=dict(color="#F8FAFC", width=2)),
            hoverinfo="text",
            showlegend=False,
        )
    )
    fig_graph.update_layout(
        title=dict(text=f"Evidence chain: {comp['comparison_id']}", font=dict(size=15), x=0.0, xanchor="left"),
        template="plotly_dark",
        paper_bgcolor="#151B26",
        plot_bgcolor="#151B26",
        height=270,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.4, 3.4]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.25, 1.15]),
        margin=dict(l=20, r=20, t=45, b=20),
    )
    st.plotly_chart(fig_graph, use_container_width=True)

    st.markdown(f"#### {comp['comparison_id']}: {rl.md_safe(comp['title'])} &nbsp; {render_category_badge(comp['category'])}", unsafe_allow_html=True)

    ex_col1, ex_col2 = st.columns(2)
    with ex_col1:
        orig = comp["statement_origin"]
        st.markdown(
            f"""
            <div class="evidence-box">
                <strong>1. Original Statement & Exact Excerpt</strong><br>
                <span style="color:#94A3B8; font-size:0.85rem;">
                    Speaker/Section: {rl.html_safe(orig['speaker'])} &nbsp;|&nbsp; Period: <strong>{orig['reporting_period']}</strong> &nbsp;|&nbsp; Date: <strong>{orig['publication_date']}</strong>
                </span>
                <div class="excerpt-quote">"{rl.html_safe(orig['exact_excerpt'])}"</div>
                <span style="font-size:0.84rem;">Source: <a href="{orig['source_url']}" target="_blank" style="color:#38BDF8;">{rl.html_safe(orig['document_title'])} ({orig['source_id']})</a></span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with ex_col2:
        foll = comp["follow_up_statement"]
        st.markdown(
            f"""
            <div class="evidence-box">
                <strong>2. Follow-Up Statement / Financial Table Excerpt</strong><br>
                <span style="color:#94A3B8; font-size:0.85rem;">
                    Speaker/Section: {rl.html_safe(foll['speaker'])} &nbsp;|&nbsp; Period: <strong>{foll['reporting_period']}</strong> &nbsp;|&nbsp; Date: <strong>{foll['publication_date']}</strong>
                </span>
                <div class="excerpt-quote">"{rl.html_safe(foll['exact_excerpt'])}"</div>
                <span style="font-size:0.84rem;">Source: <a href="{foll['source_url']}" target="_blank" style="color:#38BDF8;">{rl.html_safe(foll['document_title'])} ({foll['source_id']})</a></span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    mv = comp["metric_verification"]
    ver_col1, ver_col2 = st.columns([1.15, 1.0])
    with ver_col1:
        st.markdown("##### 3. Relevant Financial Metric & Deterministic Python Verification")
        st.markdown(f"- **Metric Analyzed:** `{mv['metric_name']}`")
        st.markdown(f"- **Units:** `{mv['units']}`")
        st.markdown(f"- **Baseline / Claimed Value:** `{mv['baseline_label']}`")
        st.markdown(f"- **Reported / Target Value:** `{mv['reported_label']}`")
        st.markdown(f"- **Calculated Deterministic Delta:** **{rl.md_safe(mv['calculated_delta'])}**")
        st.markdown("**Deterministic Python Calculation & Formula:**")
        st.code(mv["python_formula"], language="python")
        st.info(f"**Deterministic Rule Triggered:** {rl.md_safe(mv['rule_triggered'])}")

    with ver_col2:
        ea = comp["evidence_assessment"]
        st.markdown("##### 4. Supporting & Contrary Evidence, Context & Limitations")
        st.markdown("**Supporting Evidence:**")
        for s_item in ea["supporting_evidence"]:
            st.markdown(f"- ✅ {rl.md_safe(s_item)}")
        st.markdown("**Contrary / Mitigating Evidence:**")
        if ea["contrary_evidence"]:
            for c_item in ea["contrary_evidence"]:
                st.markdown(f"- ⚖️ {rl.md_safe(c_item)}")
        else:
            st.markdown("- *No contrary evidence is recorded for this finding (missing recorded evidence, not proof that none exists).*")
        st.markdown("**Alternative Explanations:**")
        for alt in ea["alternative_explanations"]:
            st.markdown(f"- 💡 {rl.md_safe(alt)}")
        st.markdown(f"**Limitations & Uncertainty:** {rl.md_safe(ea['limitations_and_uncertainty'])}")


# ==============================================================================
# TAB D: FINDING INSPECTOR & CUSTOM EVIDENCE INGESTION
# ==============================================================================
with tab_inspector:
    st.markdown("### Finding Inspector")
    st.caption(
        "Every comparison is classified into one of four categories. A potential narrative–metric divergence is a "
        "research lead for an analyst, not an accusation of management wrongdoing."
    )

    cat_choice = st.radio(
        "Select Finding Category to Inspect",
        options=["All Categories"] + ae.VALID_CATEGORIES,
        horizontal=True,
    )

    inspected_list = [
        c for c in all_comparisons
        if cat_choice == "All Categories" or c["category"] == cat_choice
    ]

    for item in inspected_list:
        with st.expander(f"[{item['category']}] {item['comparison_id']}: {item['title']} ({item['baseline_period']} → {item['target_period']})", expanded=True):
            st.markdown(render_category_badge(item["category"]), unsafe_allow_html=True)
            st.markdown(f"**Why the local concept matcher linked this pair (concept score: `{item['matching_metadata']['ai_semantic_score']:.2f}` vs. keyword baseline: `{item['matching_metadata']['keyword_overlap_score']:.2f}`):**")
            st.markdown(rl.md_safe(item["matching_metadata"]["why_semantic_wins"]))
            st.markdown(f"**Deterministic Delta:** {rl.md_safe(item['metric_verification']['calculated_delta'])}")
            _alts = item['evidence_assessment']['alternative_explanations']
            st.markdown(f"**Alternative Explanations:** {rl.md_safe('; '.join(_alts)) if _alts else '_None recorded._'}")
            st.markdown(f"**Missing Context / Limitations:** {rl.md_safe(item['evidence_assessment']['limitations_and_uncertainty'])}")

    st.markdown("---")
    st.markdown("#### Add Sourced Evidence for Verification")
    st.caption(
        "Enter your own sourced excerpts and values. ARGUS computes the local concept-match and keyword scores and runs "
        "the deterministic classification rules. Entries are user-supplied and kept for this session only."
    )

    with st.form("custom_evidence_form"):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            custom_title = st.text_input("Comparison Title", value="Q3 FY26 Revenue Guidance vs. Actual Realization")
            custom_base_period = st.text_input("Baseline Period", value="Q2 FY26 Outlook")
            custom_stmt_a = st.text_area(
                "Original Management Statement (Exact Excerpt)",
                value="NVIDIA's outlook for the third quarter of fiscal 2026 is as follows: Revenue is expected to be $54.0 billion, plus or minus 2%.",
            )
            custom_url_a = st.text_input(
                "Origin Source URL",
                value="https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2026",
            )
            custom_val_a = st.number_input("Baseline / Guided Numerical Value", value=54000.0)

        with f_col2:
            custom_comp_type = st.selectbox(
                "Deterministic Rule Type",
                options=["narrative_vs_metric_trajectory", "direct_numerical_or_ceiling"],
            )
            custom_target_period = st.text_input("Target Period", value="Q3 FY26 Actual")
            custom_stmt_b = st.text_area(
                "Follow-Up Statement / Financial Result (Exact Excerpt)",
                value="NVIDIA today reported record revenue for the third quarter ended October 26, 2025, of $57.0 billion [$57,006 million], up 22% from the previous quarter.",
            )
            custom_url_b = st.text_input(
                "Follow-Up Source URL",
                value="https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2026",
            )
            custom_val_b = st.number_input("Reported Numerical Value", value=57006.0)

        custom_units = st.text_input("Metric Name & Units", value="Quarterly Consolidated Revenue ($ in millions)")
        submitted = st.form_submit_button("Run Concept Match & Deterministic Verification")

        if submitted:
            sem_score, sem_meta = ae.compute_semantic_similarity_score(custom_stmt_a, custom_stmt_b)
            kw_score = ae.compute_keyword_baseline_score(custom_stmt_a, custom_stmt_b)
            pct_chg = rl.safe_pct_change(custom_val_a, custom_val_b)  # None when baseline is zero
            cat_res, rule_msg = ae.classify_finding_deterministic(
                comparison_type=custom_comp_type,
                baseline_value=custom_val_a,
                reported_value=custom_val_b,
                tolerance_pct=2.0,
            )
            new_id = f"CMP-CUSTOM-{len(st.session_state['custom_comparisons']) + 1:03d}"
            st.session_state["custom_comparisons"].append({
                "comparison_id": new_id,
                "company": "NVIDIA",
                "title": custom_title,
                "category": cat_res,
                "severity": "User-Submitted Verification",
                "baseline_period": custom_base_period,
                "target_period": custom_target_period,
                "statement_origin": {
                    "speaker": "User-Entered Sourced Excerpt",
                    "document_title": f"Sourced Filing ({custom_base_period})",
                    "source_id": "USER-SOURCE-A",
                    "source_url": custom_url_a,
                    "publication_date": "2026-10-26",
                    "reporting_period": custom_base_period,
                    "exact_excerpt": custom_stmt_a,
                },
                "follow_up_statement": {
                    "speaker": "User-Entered Follow-Up Excerpt",
                    "document_title": f"Sourced Filing ({custom_target_period})",
                    "source_id": "USER-SOURCE-B",
                    "source_url": custom_url_b,
                    "publication_date": "2026-10-26",
                    "reporting_period": custom_target_period,
                    "exact_excerpt": custom_stmt_b,
                },
                "metric_verification": {
                    "metric_name": custom_units,
                    "units": custom_units,
                    "baseline_value": custom_val_a,
                    "baseline_label": f"{custom_val_a:,.2f}",
                    "reported_value": custom_val_b,
                    "reported_label": f"{custom_val_b:,.2f}",
                    "raw_inputs": {"baseline": custom_val_a, "reported": custom_val_b},
                    "python_formula": (
                        f"pct_change = (({custom_val_b} - {custom_val_a}) / abs({custom_val_a})) * 100  # = {pct_chg:+.2f}%"
                        if pct_chg is not None else
                        "# percent change not computed: baseline is zero"
                    ),
                    "calculated_delta": f"{custom_val_b - custom_val_a:+,.2f} ({rl.format_pct(pct_chg)})",
                    "rule_triggered": rule_msg,
                },
                "matching_metadata": {
                    "ai_semantic_score": sem_score,
                    "keyword_overlap_score": kw_score,
                    "why_semantic_wins": f"Shared Financial Concepts: {', '.join(sem_meta['shared_concepts']) or 'Lexical/Contextual Overlap'}",
                },
                "evidence_assessment": {
                    "supporting_evidence": [f"Deterministic calculation: {rl.format_pct(pct_chg)} difference."],
                    "contrary_evidence": [],
                    "alternative_explanations": ["User-submitted comparison evaluated under standard tolerance rules."],
                    "limitations_and_uncertainty": "Verify full footnote context in the linked primary SEC filing.",
                },
            })
            st.success(f"Added `{new_id}` → Category: **{cat_res}** | Concept score: `{sem_score:.3f}` | Keyword score: `{kw_score:.3f}` | Delta: `{rl.format_pct(pct_chg)}`")


# ==============================================================================
# TAB: RESEARCH LAB
# ==============================================================================
with tab_research:
    st.markdown("### Research Lab")
    st.markdown(
        f'<div class="rl-note"><strong>Prototype scope.</strong> {rl.html_safe(rl.PROTOTYPE_NOTICE)} '
        f'{rl.html_safe(ae.ENGINE_STATUS_MESSAGE)}</div>',
        unsafe_allow_html=True,
    )

    rl_q_col, rl_btn_col = st.columns([4, 1])
    with rl_q_col:
        rl_question = st.selectbox(
            "Research question",
            options=list(rl.RESEARCH_QUESTIONS.keys()),
            format_func=lambda k: rl.RESEARCH_QUESTIONS[k],
            key="rl_question",
        )
        st.caption(f"Selection rule: {rl.QUESTION_RULES[rl_question]}")
    with rl_btn_col:
        st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
        rl_run = st.button("Run Research Review", type="primary", use_container_width=True, key="rl_run")

    if rl_run:
        _results = rl.run_research_review(all_comparisons, rl_question)
        st.session_state["rl_review"] = {
            "question": rl_question,
            "ids": [r["finding"]["comparison_id"] for r in _results],
            "reasons": {r["finding"]["comparison_id"]: r["reasons"] for r in _results},
        }

    rl_review = st.session_state.get("rl_review")
    if not rl_review:
        st.info("Choose a research question and press **Run Research Review** to filter the preloaded findings.")
    else:
        if rl_review["question"] != rl_question:
            st.warning(
                f"Showing results for “{rl.RESEARCH_QUESTIONS[rl_review['question']]}”. "
                "Press Run Research Review to apply the new question."
            )
        rl_findings = [c for c in all_comparisons if c["comparison_id"] in rl_review["ids"]]
        st.markdown(
            f"#### Results: {rl.RESEARCH_QUESTIONS[rl_review['question']]} "
            f"({len(rl_findings)} of {len(all_comparisons)} records)"
        )

        if not rl_findings:
            st.warning("No records in the preloaded data matched this question.")
        else:
            rl_ids = [c["comparison_id"] for c in rl_findings]
            rl_chart1, rl_chart2 = st.columns(2)

            with rl_chart1:
                fig_rl_scores = go.Figure()
                fig_rl_scores.add_trace(go.Bar(
                    x=rl_ids,
                    y=[c["matching_metadata"]["ai_semantic_score"] for c in rl_findings],
                    name="Concept match score (local)",
                    marker_color="#38BDF8",
                    customdata=[c["title"] for c in rl_findings],
                    hovertemplate="%{x}<br>%{customdata}<br>Concept score: %{y:.2f}<extra></extra>",
                ))
                fig_rl_scores.add_trace(go.Bar(
                    x=rl_ids,
                    y=[c["matching_metadata"]["keyword_overlap_score"] for c in rl_findings],
                    name="Keyword overlap score",
                    marker_color="#64748B",
                    customdata=[c["title"] for c in rl_findings],
                    hovertemplate="%{x}<br>%{customdata}<br>Keyword score: %{y:.2f}<extra></extra>",
                ))
                fig_rl_scores.update_layout(
                    title=dict(text="Matching scores per finding (0–1)", font=dict(size=15), x=0.0, xanchor="left"),
                    template="plotly_dark", paper_bgcolor="#151B26", plot_bgcolor="#151B26",
                    barmode="group", height=340,
                    legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="left", x=0, font=dict(size=11)),
                    margin=dict(l=40, r=20, t=50, b=40),
                    yaxis=dict(title="Score", range=[0, 1]),
                    xaxis=dict(title="Comparison ID"),
                )
                st.plotly_chart(fig_rl_scores, use_container_width=True)

            with rl_chart2:
                _cat_counts = {cat: sum(1 for c in rl_findings if c["category"] == cat) for cat in ae.VALID_CATEGORIES}
                fig_rl_cats = go.Figure(go.Bar(
                    x=list(_cat_counts.values()),
                    y=list(_cat_counts.keys()),
                    orientation="h",
                    marker_color=[rl.CATEGORY_COLORS[k] for k in _cat_counts],
                    text=list(_cat_counts.values()),
                    textposition="outside",
                    hovertemplate="%{y}: %{x}<extra></extra>",
                ))
                fig_rl_cats.update_layout(
                    title=dict(text="Matching findings by classification", font=dict(size=15), x=0.0, xanchor="left"),
                    template="plotly_dark", paper_bgcolor="#151B26", plot_bgcolor="#151B26",
                    height=340, margin=dict(l=20, r=30, t=50, b=40),
                    xaxis=dict(title="Number of findings", dtick=1, range=[0, max(_cat_counts.values()) + 1]),
                    yaxis=dict(autorange="reversed"),
                )
                st.plotly_chart(fig_rl_cats, use_container_width=True)
            st.caption(
                "Scores come from the local rule-based concept matcher and a keyword-overlap baseline stored with each record; "
                "they are not model confidence."
            )

            rl_sel_id = st.selectbox(
                "Select a finding",
                options=rl_ids,
                format_func=lambda cid: next(f"{c['comparison_id']} — {c['title']}" for c in rl_findings if c["comparison_id"] == cid),
                key=f"rl_finding_{rl_review['question']}",
            )
            rl_c = next(c for c in rl_findings if c["comparison_id"] == rl_sel_id)
            rl_mv = rl_c["metric_verification"]

            st.markdown(
                f"#### {rl_sel_id}: {rl.md_safe(rl_c['title'])} &nbsp; {render_category_badge(rl_c['category'])}",
                unsafe_allow_html=True,
            )
            st.caption(
                f"Periods: {rl_c['baseline_period']} → {rl_c['target_period']}  |  "
                f"Why it matched: {rl.md_safe('; '.join(rl_review['reasons'].get(rl_sel_id, [])))}"
            )
            if rl_c.get("severity") == "User-Submitted Verification":
                st.caption("Data origin: user-entered in this session, not from the preloaded dataset.")

            rl_ex1, rl_ex2 = st.columns(2)
            for _col, _label, _s in (
                (rl_ex1, "Original statement", rl_c["statement_origin"]),
                (rl_ex2, "Follow-up statement", rl_c["follow_up_statement"]),
            ):
                with _col:
                    st.markdown(
                        f"""
                        <div class="evidence-box">
                            <strong>{_label}</strong><br>
                            <span style="color:#94A3B8; font-size:0.85rem;">
                                Period: <strong>{rl.html_safe(_s['reporting_period'])}</strong> &nbsp;|&nbsp;
                                Published: <strong>{rl.html_safe(_s['publication_date'])}</strong>
                            </span>
                            <div class="excerpt-quote">"{rl.html_safe(_s['exact_excerpt'])}"</div>
                            <span style="font-size:0.84rem;">Source: {rl.safe_link(_s.get('source_url'), f"{_s['document_title']} ({_s['source_id']})")}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            rl_m1, rl_m2 = st.columns([1.1, 1.0])
            with rl_m1:
                st.markdown("##### Metric values and calculation")
                st.markdown(f"- **Metric:** {rl.md_safe(rl_mv['metric_name'])}")
                st.markdown(f"- **Units:** {rl.md_safe(rl_mv['units'])}")
                st.markdown(f"- **Baseline / claimed:** {rl.md_safe(rl_mv['baseline_label'])}")
                st.markdown(f"- **Reported / target:** {rl.md_safe(rl_mv['reported_label'])}")
                st.markdown(f"- **Calculated delta:** {rl.md_safe(rl_mv['calculated_delta'])}")
                if rl_mv.get("python_formula"):
                    st.code(rl_mv["python_formula"], language="python")
                else:
                    st.caption("No calculation formula is recorded for this finding.")
            with rl_m2:
                st.markdown("##### Classification")
                st.markdown(render_category_badge(rl_c["category"]), unsafe_allow_html=True)
                st.markdown(rl.md_safe(rl_mv["rule_triggered"]))

            st.markdown("##### Analyst challenge")
            rl_challenge = st.radio(
                "Challenge this finding with",
                options=list(rl.CHALLENGES.keys()),
                format_func=lambda k: rl.CHALLENGES[k],
                horizontal=True,
                key="rl_challenge",
            )
            _view = rl.challenge_view(rl_c, rl_challenge)
            for _item in _view["items"]:
                st.markdown(f"- {rl.md_safe(_item)}")
            if _view["note"]:
                st.caption(rl.md_safe(_view["note"]))
            if _view["code"]:
                st.code(_view["code"], language="python")

            rl_brief = rl.build_research_brief(
                rl_c, rl_review["question"], rl_challenge, rl_review["reasons"].get(rl_sel_id)
            )
            st.download_button(
                "Download research brief (.md)",
                data=rl_brief.encode("utf-8"),
                file_name=rl.brief_filename(rl_c),
                mime="text/markdown",
                key="rl_download",
            )


# ==============================================================================
# TAB E: RESPONSIBLE AI & BENCHMARK EVALUATION
# ==============================================================================
with tab_ai_eval:
    st.markdown("### Validation: Labeled Benchmark Evaluation")
    st.caption(ae.ENGINE_STATUS_MESSAGE)
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.markdown(
            """
            <div class="evidence-box">
                <h4>Role 1: Local Concept-Aware Matching</h4>
                <ul>
                    <li><strong>Task:</strong> Connect related management claims, footnotes, and financial tables across multi-period filings even when terminology shifts.</li>
                    <li><strong>Why Keyword Matching Fails:</strong>
                        <ol>
                            <li><em>Misses Paraphrased Links (False Negatives):</em> When CEO Jensen Huang says <code>"compute is revenue"</code> in Q2 FY27, there is zero lexical overlap with <code>"Changes in accounts receivable &#36;(22,346)M"</code> on the Cash Flow Statement.</li>
                            <li><em>Triggers Boilerplate Collisions (False Positives):</em> Press releases repeat identical sentence templates across unrelated segments (e.g., <code>"Fourth-quarter [Automotive vs. ProViz] revenue was up X% from the previous quarter and up Y% from a year ago"</code>).</li>
                        </ol>
                    </li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with r_col2:
        st.markdown(
            """
            <div class="evidence-box">
                <h4>Role 2: Deterministic Python Verification</h4>
                <ul>
                    <li><strong>Task:</strong> Execute all arithmetic, YoY/QoQ growth rates, basis-point margin checks, DSO calculations, and classification rules in pure, unit-tested Python.</li>
                    <li><strong>Zero Hallucinated Math:</strong> The matcher never computes or judges numerical discrepancies in ARGUS. Python formulas are displayed alongside every finding so analysts can audit the exact inputs.</li>
                    <li><strong>How False Positives & Missed Findings Are Identified:</strong> Analysts can adjust similarity thresholds below and inspect the confusion matrix on our 12-pair manually labeled evaluation benchmark.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### Benchmark: Local Concept-Aware Matcher vs. Exact Keyword Baseline")
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        sem_thresh = st.slider("Concept-Match Threshold", min_value=0.10, max_value=0.90, value=0.50, step=0.05)
    with t_col2:
        kw_thresh = st.slider("Exact Keyword Overlap Threshold", min_value=0.10, max_value=0.90, value=0.22, step=0.02)

    bench_results = ae.evaluate_matching_benchmark(
        base_data["eval_dataset"],
        semantic_threshold=sem_thresh,
        keyword_threshold=kw_thresh,
    )
    sm = bench_results["semantic_metrics"]
    km = bench_results["keyword_metrics"]

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Concept-Match Precision", f"{sm['precision']*100:.1f}%", f"{(sm['precision'] - km['precision'])*100:+.1f}% vs Keyword")
    m_col2.metric("Concept-Match Recall", f"{sm['recall']*100:.1f}%", f"{(sm['recall'] - km['recall'])*100:+.1f}% vs Keyword")
    m_col3.metric("Concept-Match F1", f"{sm['f1']*100:.1f}%", f"{(sm['f1'] - km['f1'])*100:+.1f}% vs Keyword")
    m_col4.metric("Concept-Match False Positives", f"{sm['fp']} / {bench_results['negative_pairs']}", f"Keyword FP: {km['fp']} / {bench_results['negative_pairs']}")

    comp_table = pd.DataFrame([
        {
            "Method": "ARGUS Local Concept-Aware Matcher (rule-based)",
            "Threshold": sem_thresh,
            "Precision": f"{sm['precision']*100:.1f}%",
            "Recall": f"{sm['recall']*100:.1f}%",
            "F1 Score": f"{sm['f1']*100:.1f}%",
            "True Positives (TP)": sm["tp"],
            "False Positives (FP)": sm["fp"],
            "True Negatives (TN)": sm["tn"],
            "False Negatives (FN)": sm["fn"],
        },
        {
            "Method": "Exact Keyword / Lexical Overlap Baseline",
            "Threshold": kw_thresh,
            "Precision": f"{km['precision']*100:.1f}%",
            "Recall": f"{km['recall']*100:.1f}%",
            "F1 Score": f"{km['f1']*100:.1f}%",
            "True Positives (TP)": km["tp"],
            "False Positives (FP)": km["fp"],
            "True Negatives (TN)": km["tn"],
            "False Negatives (FN)": km["fn"],
        },
    ])
    st.dataframe(comp_table, use_container_width=True, hide_index=True)

    st.markdown("##### Pair-by-Pair Labeled Evaluation Results (`data/evaluation_dataset.json`)")
    st.dataframe(pd.DataFrame(bench_results["pair_results"]), use_container_width=True, hide_index=True)

    st.markdown("##### Complete Source Manifest (`data/source_manifest.json`)")
    st.json(manifest)
