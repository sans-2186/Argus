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
    st.markdown("#### 🤖 AI & Verification Engine Status")
    gemini_key_present = bool(os.environ.get("GEMINI_API_KEY"))
    if gemini_key_present:
        st.success("AI Mode: Live Gemini Semantic Embeddings + Concept Ontology Active")
    else:
        st.info(
            "**Engine Mode: Transparent Local Concept-Aware Semantic Baseline**\n\n"
            "No paid API key required. Distinguishes semantic concept matching from "
            "exact keyword matching, paired with 100% deterministic Python financial verification."
        )

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
            AI-Assisted Financial Research Intelligence &nbsp;|&nbsp;
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
tab_exec, tab_timeline, tab_explorer, tab_inspector, tab_ai_eval = st.tabs([
    "📊 A. Executive Dashboard",
    "⏳ B. Narrative-vs-Metrics Timeline",
    "🕸️ C. Evidence Explorer & Graph",
    "🔍 D. Finding Inspector & Custom Ingestion",
    "⚖️ E. Responsible AI & Benchmark Evaluation",
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
                <div class="kpi-sub">2 Corroborated | 1 Sub-Segment Gap</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Auditable Chain Banner
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown('<div class="chain-step"><strong>1. Company Statement</strong><br>Verbatim CEO/CFO Excerpt</div>', unsafe_allow_html=True)
    c2.markdown('<div class="chain-step"><strong>2. Original Source</strong><br>SEC EDGAR / IR URL & Date</div>', unsafe_allow_html=True)
    c3.markdown('<div class="chain-step"><strong>3. Financial Metric</strong><br>Reported GAAP/Non-GAAP ($M)</div>', unsafe_allow_html=True)
    c4.markdown('<div class="chain-step"><strong>4. Deterministic Check</strong><br>Exact Python Formula</div>', unsafe_allow_html=True)
    c5.markdown('<div class="chain-step"><strong>5. Analyst Finding</strong><br>4-Category Classification</div>', unsafe_allow_html=True)

    st.markdown("### Executive Research Summary: NVIDIA (Q1 FY26 – Q2 FY27)")
    st.markdown(
        """
        **ARGUS** connects management commentary across six quarters of NVIDIA earnings releases and the FY2026 Form 10-K,
        then executes deterministic Python verification on the underlying income statement, balance sheet, and cash flow figures:
        * **Top-Line & Data Center Acceleration Corroborated (*No Identified Discrepancy*):** Management's evolving narrative—from *"virtuous cycle of AI"* (Q3 FY26) to *"agentic AI inflection point"* (Q4 FY26) and *"AI factories at full steam"* (Q2 FY27)—is supported by Data Center revenue scaling from **$39,100M** in Q1 FY26 to **$89,000M** in Q2 FY27 (+117% YoY), beating quarterly revenue guidance in every period.
        * **Primary Research Lead — Q2 FY27 Revenue vs. Operating Cash Flow Divergence (*Potential Narrative–Metric Divergence*):** In Q2 FY27 (ended July 26, 2026), CEO Jensen Huang stated *"Its tokens are productive and profitable. Now, compute is revenue."* While GAAP revenue grew **+17.90% QoQ** to **$96,221M**, GAAP Operating Cash Flow fell **-52.18% QoQ** (from **$50,344M** to **$24,077M**) and Free Cash Flow fell **-56.05% QoQ** (to **$21,341M**), driven by a **+$22,349M (+54.90% QoQ)** surge in Accounts Receivable to **$63,059M** (DSO rising from 45.4 to 59.6 days).
        * **Cross-Filing Numerical Mismatches Caught (*Verified Numerical Mismatch*):**
          1. **FY26 OpEx Guidance vs. Actuals:** Q2 FY26 outlook guided full-year FY26 operating expense growth to the *"high-30% range"*, whereas actual FY26 OpEx grew **40.66% GAAP (41% reported)** and **42.49% Non-GAAP (42% reported)**.
          2. **Non-GAAP Stock-Based Compensation (SBC) Restatement:** Beginning Q1 FY27, NVIDIA ceased excluding SBC from Non-GAAP measures and restated historical quarters—causing Q4 FY26 Non-GAAP OpEx to shift from **$5,102M** (in the Q4 FY26 release) to **$6,666M** (in the Q1 FY27 release), a **+$1,564M (+30.65%)** discrepancy for the exact same quarter that breaks unadjusted time-series models.
        """
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
            title="Revenue vs. Operating Cash Flow & Accounts Receivable ($ in Millions)",
            template="plotly_dark",
            paper_bgcolor="#151B26",
            plot_bgcolor="#151B26",
            barmode="group",
            height=390,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=60, b=40),
        )
        fig_rev_ocf.update_yaxes(title_text="Revenue & OCF ($M)", secondary_y=False)
        fig_rev_ocf.update_yaxes(title_text="Accounts Receivable ($M)", secondary_y=True)
        st.plotly_chart(fig_rev_ocf, use_container_width=True)
        st.caption("Source: NVIDIA Q2 FY26–Q2 FY27 Earnings Releases & FY26 Form 10-K. Units: $ in millions.")

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
            title="Operating Expenses: Original Non-GAAP vs. SBC-Restated Series ($ in Millions)",
            template="plotly_dark",
            paper_bgcolor="#151B26",
            plot_bgcolor="#151B26",
            height=390,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=60, b=40),
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
            "AI Semantic Score": c["matching_metadata"]["ai_semantic_score"],
            "Keyword Score": c["matching_metadata"]["keyword_overlap_score"],
            "Deterministic Delta": c["metric_verification"]["calculated_delta"],
            "Source Document": c["statement_origin"]["source_id"],
        })
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)


# ==============================================================================
# TAB B: NARRATIVE-VERSUS-METRICS TIMELINE
# ==============================================================================
with tab_timeline:
    st.markdown("### ⏳ Multi-Period Narrative-versus-Metrics Evolution (Q1 FY26 – Q2 FY27)")
    st.markdown(
        "Inspect how NVIDIA management's strategic narrative evolved across six consecutive reporting periods alongside "
        "verified GAAP and Non-GAAP financial metrics, units, and primary filing links."
    )

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
        title=f"NVIDIA {metric_label} Across Reporting Periods",
        template="plotly_dark",
        paper_bgcolor="#151B26",
        plot_bgcolor="#151B26",
        height=340,
        margin=dict(l=40, r=40, t=55, b=35),
        yaxis_title=metric_label,
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

    st.markdown("#### Period-by-Period Sourced Statements & Verified Financial Table")
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

    st.markdown("#### Chronological Narrative Evolution Cards")
    for src in reversed(manifest["sources"]):
        with st.expander(f"📅 {src['reporting_period']} (Published: {src['publication_date']}) — {src['title']}", expanded=True):
            st.markdown(f"**Primary Source URL:** [{src['url']}]({src['url']}) &nbsp;|&nbsp; **Mirror / SEC Filing:** [{src['sec_mirror_url']}]({src['sec_mirror_url']})")
            st.markdown("**Extracted Financial Metrics (Verified with Units):**")
            for m_item in src["extracted_metrics"]:
                st.markdown(f"- {m_item}")


# ==============================================================================
# TAB C: EVIDENCE EXPLORER & INTERACTIVE RELATIONSHIP GRAPH
# ==============================================================================
with tab_explorer:
    st.markdown("### 🕸️ Auditable Evidence Explorer & Interactive Relationship Graph")
    st.markdown(
        "Select any comparison below to inspect the complete auditable chain: verbatim management statement, "
        "follow-up disclosure, source URLs, publication dates, deterministic Python formula, and supporting/contrary evidence."
    )

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
        f"3. Python Verification<br>Semantic={comp['matching_metadata']['ai_semantic_score']:.2f}",
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
        title=f"Interactive Evidence Relationship Graph: {comp['comparison_id']}",
        template="plotly_dark",
        paper_bgcolor="#151B26",
        plot_bgcolor="#151B26",
        height=270,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.4, 3.4]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.25, 1.15]),
        margin=dict(l=20, r=20, t=45, b=20),
    )
    st.plotly_chart(fig_graph, use_container_width=True)

    st.markdown(f"#### {comp['comparison_id']}: {comp['title']} &nbsp; {render_category_badge(comp['category'])}", unsafe_allow_html=True)

    ex_col1, ex_col2 = st.columns(2)
    with ex_col1:
        orig = comp["statement_origin"]
        st.markdown(
            f"""
            <div class="evidence-box">
                <strong>1. Original Statement & Exact Excerpt</strong><br>
                <span style="color:#94A3B8; font-size:0.85rem;">
                    Speaker/Section: {orig['speaker']} &nbsp;|&nbsp; Period: <strong>{orig['reporting_period']}</strong> &nbsp;|&nbsp; Date: <strong>{orig['publication_date']}</strong>
                </span>
                <div class="excerpt-quote">"{orig['exact_excerpt']}"</div>
                <span style="font-size:0.84rem;">Source: <a href="{orig['source_url']}" target="_blank" style="color:#38BDF8;">{orig['document_title']} ({orig['source_id']})</a></span>
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
                    Speaker/Section: {foll['speaker']} &nbsp;|&nbsp; Period: <strong>{foll['reporting_period']}</strong> &nbsp;|&nbsp; Date: <strong>{foll['publication_date']}</strong>
                </span>
                <div class="excerpt-quote">"{foll['exact_excerpt']}"</div>
                <span style="font-size:0.84rem;">Source: <a href="{foll['source_url']}" target="_blank" style="color:#38BDF8;">{foll['document_title']} ({foll['source_id']})</a></span>
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
        st.markdown(f"- **Calculated Deterministic Delta:** **{mv['calculated_delta']}**")
        st.markdown("**Deterministic Python Calculation & Formula:**")
        st.code(mv["python_formula"], language="python")
        st.info(f"**Deterministic Rule Triggered:** {mv['rule_triggered']}")

    with ver_col2:
        ea = comp["evidence_assessment"]
        st.markdown("##### 4. Supporting & Contrary Evidence, Context & Limitations")
        st.markdown("**Supporting Evidence:**")
        for s_item in ea["supporting_evidence"]:
            st.markdown(f"- ✅ {s_item}")
        st.markdown("**Contrary / Mitigating Evidence:**")
        if ea["contrary_evidence"]:
            for c_item in ea["contrary_evidence"]:
                st.markdown(f"- ⚖️ {c_item}")
        else:
            st.markdown("- *No contrary numerical evidence identified in primary filings.*")
        st.markdown("**Alternative Explanations:**")
        for alt in ea["alternative_explanations"]:
            st.markdown(f"- 💡 {alt}")
        st.markdown(f"**Limitations & Uncertainty:** {ea['limitations_and_uncertainty']}")


# ==============================================================================
# TAB D: FINDING INSPECTOR & CUSTOM EVIDENCE INGESTION
# ==============================================================================
with tab_inspector:
    st.markdown("### 🔍 Finding Inspector & Interactive Evidence Ingestion")
    st.markdown(
        """
        ARGUS classifies every comparison into one of four institutional research categories.
        **Important Analytical Principle:** *A potential narrative–metric divergence is an investigative research lead for an analyst,
        never an automatic accusation of management dishonesty or securities fraud.*
        """
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
            st.markdown(f"**Why AI Semantic Matching Connected This Pair (Score: `{item['matching_metadata']['ai_semantic_score']:.2f}` vs. Keyword Baseline: `{item['matching_metadata']['keyword_overlap_score']:.2f}`):**")
            st.write(item["matching_metadata"]["why_semantic_wins"])
            st.markdown(f"**Deterministic Delta:** {item['metric_verification']['calculated_delta']}")
            st.markdown(f"**Alternative Explanations:** {'; '.join(item['evidence_assessment']['alternative_explanations'])}")
            st.markdown(f"**Missing Context / Limitations:** {item['evidence_assessment']['limitations_and_uncertainty']}")

    st.markdown("---")
    st.markdown("#### ➕ Manually Load or Enter New Sourced Evidence for Live Verification")
    st.caption(
        "Use this form to test ARGUS on additional sourced excerpts or financial metrics from SEC filings or earnings releases. "
        "ARGUS computes the semantic vs. keyword match score and runs deterministic Python classification rules immediately."
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
        submitted = st.form_submit_button("Run Semantic Match & Deterministic Python Verification")

        if submitted:
            sem_score, sem_meta = ae.compute_semantic_similarity_score(custom_stmt_a, custom_stmt_b)
            kw_score = ae.compute_keyword_baseline_score(custom_stmt_a, custom_stmt_b)
            pct_chg = ae.calculate_pct_change(custom_val_a, custom_val_b)
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
                    "python_formula": f"pct_change = (({custom_val_b} - {custom_val_a}) / {custom_val_a}) * 100  # = {pct_chg:+.2f}%",
                    "calculated_delta": f"{custom_val_b - custom_val_a:+,.2f} ({pct_chg:+.2f}%)",
                    "rule_triggered": rule_msg,
                },
                "matching_metadata": {
                    "ai_semantic_score": sem_score,
                    "keyword_overlap_score": kw_score,
                    "why_semantic_wins": f"Shared Financial Concepts: {', '.join(sem_meta['shared_concepts']) or 'Lexical/Contextual Overlap'}",
                },
                "evidence_assessment": {
                    "supporting_evidence": [f"Deterministic calculation verified {pct_chg:+.2f}% difference."],
                    "contrary_evidence": [],
                    "alternative_explanations": ["User-submitted comparison evaluated under standard tolerance rules."],
                    "limitations_and_uncertainty": "Verify full footnote context in the linked primary SEC filing.",
                },
            })
            st.success(f"Added `{new_id}` → Category: **{cat_res}** | Semantic Score: `{sem_score:.3f}` | Keyword Score: `{kw_score:.3f}` | Delta: `{pct_chg:+.2f}%`")


# ==============================================================================
# TAB E: RESPONSIBLE AI & BENCHMARK EVALUATION
# ==============================================================================
with tab_ai_eval:
    st.markdown("### ⚖️ Responsible AI Architecture & Labeled Benchmark Evaluation")
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.markdown(
            """
            <div class="evidence-box">
                <h4>🤖 Role 1: AI-Assisted Semantic Discovery</h4>
                <ul>
                    <li><strong>Task:</strong> Connect related management claims, footnotes, and financial tables across multi-period filings even when terminology shifts.</li>
                    <li><strong>Why Keyword Matching Fails:</strong>
                        <ol>
                            <li><em>Misses Paraphrased Links (False Negatives):</em> When CEO Jensen Huang says <code>"compute is revenue"</code> in Q2 FY27, there is zero lexical overlap with <code>"Changes in accounts receivable $(22,346)M"</code> on the Cash Flow Statement.</li>
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
                <h4>🐍 Role 2: Deterministic Python Verification</h4>
                <ul>
                    <li><strong>Task:</strong> Execute all arithmetic, YoY/QoQ growth rates, basis-point margin checks, DSO calculations, and classification rules in pure, unit-tested Python.</li>
                    <li><strong>Zero Hallucinated Math:</strong> LLMs and semantic models never compute or judge numerical discrepancies in ARGUS. Python formulas are displayed alongside every finding so analysts can audit the exact inputs.</li>
                    <li><strong>How False Positives & Missed Findings Are Identified:</strong> Analysts can adjust similarity thresholds below and inspect the confusion matrix on our 12-pair manually labeled evaluation benchmark.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### 🧪 Live Benchmark Evaluation: Concept-Aware Semantic Engine vs. Exact Keyword Baseline")
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        sem_thresh = st.slider("AI / Concept-Aware Semantic Similarity Threshold", min_value=0.10, max_value=0.90, value=0.50, step=0.05)
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
    m_col1.metric("Semantic Precision", f"{sm['precision']*100:.1f}%", f"{(sm['precision'] - km['precision'])*100:+.1f}% vs Keyword")
    m_col2.metric("Semantic Recall", f"{sm['recall']*100:.1f}%", f"{(sm['recall'] - km['recall'])*100:+.1f}% vs Keyword")
    m_col3.metric("Semantic F1 Score", f"{sm['f1']*100:.1f}%", f"{(sm['f1'] - km['f1'])*100:+.1f}% vs Keyword")
    m_col4.metric("Semantic False Positives", f"{sm['fp']} / {bench_results['negative_pairs']}", f"Keyword FP: {km['fp']} / {bench_results['negative_pairs']}")

    comp_table = pd.DataFrame([
        {
            "Method": "ARGUS Concept-Aware Semantic Matcher (Local AI Baseline)",
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
