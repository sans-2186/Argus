"""
ARGUS Research Lab — pure-Python helpers (no Streamlit / Plotly dependency).

Everything here operates on the records already loaded from data/financial_statements.json
(plus any user-entered comparisons in the session). Nothing is retrieved from the web and no
LLM is called; "running a review" means filtering/ranking preloaded records.
"""

from __future__ import annotations

import html
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

import argus_engine as ae

PROTOTYPE_NOTICE = (
    "Prototype notice: this review filters preloaded project data only. It does not retrieve "
    "new filings and does not call an LLM."
)

# ---- research questions -------------------------------------------------------------------
Q_NARRATIVE = "narrative_vs_metric"
Q_GUIDANCE = "guidance_vs_actual"
Q_ACCOUNTING = "accounting_methodology"
Q_GAPS = "evidence_gaps"
Q_ALL = "all_leads"

RESEARCH_QUESTIONS: Dict[str, str] = {
    Q_NARRATIVE: "Narrative-versus-metric analysis",
    Q_GUIDANCE: "Guidance-versus-actual comparisons",
    Q_ACCOUNTING: "Accounting methodology changes",
    Q_GAPS: "Evidence gaps",
    Q_ALL: "All research leads",
}

QUESTION_RULES: Dict[str, str] = {
    Q_NARRATIVE: "Records classified as 'Potential narrative–metric divergence' or 'No identified discrepancy' "
                 "(management narrative checked against a metric trajectory).",
    Q_GUIDANCE: "Records whose original excerpt or title refers to guidance / outlook / expected values "
                "(keywords: guidance, outlook, expected to, guided).",
    Q_ACCOUNTING: "Records whose title or recorded rule refers to a methodology change or restatement "
                  "(keywords: methodology, restat, reclassif, accounting policy).",
    Q_GAPS: "Records classified 'Insufficient evidence', with a missing numeric input, or with an empty "
            "evidence list in the record (missing RECORDED evidence, not proof that none exists).",
    Q_ALL: "Every record in the project data.",
}

# ---- challenge views ----------------------------------------------------------------------
CH_SUPPORT = "supporting"
CH_CONTRARY = "contrary"
CH_ALT = "alternatives"
CH_UNCERTAINTY = "uncertainty"
CH_CALC = "calculation"

CHALLENGES: Dict[str, str] = {
    CH_SUPPORT: "Supporting evidence",
    CH_CONTRARY: "Contrary evidence",
    CH_ALT: "Alternative explanations",
    CH_UNCERTAINTY: "Uncertainty",
    CH_CALC: "Calculation details",
}

_GUIDANCE_TERMS = ("guidance", "outlook", "expected to", "guided")
_ACCOUNTING_TERMS = ("methodology", "restat", "reclassif", "accounting policy")

CATEGORY_COLORS = {
    ae.CATEGORY_MISMATCH: "#EF4444",
    ae.CATEGORY_DIVERGENCE: "#F59E0B",
    ae.CATEGORY_NO_DISCREPANCY: "#10B981",
    ae.CATEGORY_INSUFFICIENT: "#94A3B8",
}


# ---- safe math ----------------------------------------------------------------------------
def safe_pct_change(baseline: Optional[float], reported: Optional[float]) -> Optional[float]:
    """Percent change, or None when it cannot be computed (missing input or zero baseline)."""
    if baseline is None or reported is None or baseline == 0:
        return None
    return ae.calculate_pct_change(baseline, reported)


def format_pct(value: Optional[float]) -> str:
    return "n/a (missing input or zero baseline)" if value is None else f"{value:+.2f}%"


# ---- filtering ----------------------------------------------------------------------------
def _text(c: Dict[str, Any], *paths: Tuple[str, ...]) -> str:
    parts: List[str] = []
    for path in paths:
        cur: Any = c
        for key in path:
            cur = cur.get(key, "") if isinstance(cur, dict) else ""
        parts.append(str(cur))
    return " ".join(parts).lower()


def _evidence_gap_reasons(c: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []
    if c.get("category") == ae.CATEGORY_INSUFFICIENT:
        reasons.append("Classified 'Insufficient evidence'")
    mv = c.get("metric_verification", {})
    if mv.get("baseline_value") is None or mv.get("reported_value") is None:
        reasons.append("Baseline or reported numeric value is missing in the record")
    ea = c.get("evidence_assessment", {})
    for key, label in (
        ("supporting_evidence", "supporting"),
        ("contrary_evidence", "contrary"),
        ("alternative_explanations", "alternative-explanation"),
    ):
        if not ea.get(key):
            reasons.append(f"No {label} evidence is recorded (a gap in the record, not proof none exists)")
    return reasons


def match_reasons(c: Dict[str, Any], question: str) -> List[str]:
    """Return the reasons a record matches the question; an empty list means no match."""
    if question == Q_ALL:
        return ["Included in 'all research leads'"]
    if question == Q_NARRATIVE:
        if c.get("category") in (ae.CATEGORY_DIVERGENCE, ae.CATEGORY_NO_DISCREPANCY):
            return [f"Narrative compared with metric trajectory; classified '{c['category']}'"]
        return []
    if question == Q_GUIDANCE:
        text = _text(c, ("title",), ("statement_origin", "exact_excerpt"))
        hits = [t for t in _GUIDANCE_TERMS if t in text]
        return [f"Guidance language found: {', '.join(hits)}"] if hits else []
    if question == Q_ACCOUNTING:
        text = _text(c, ("title",), ("metric_verification", "rule_triggered"))
        hits = [t for t in _ACCOUNTING_TERMS if t in text]
        return [f"Methodology language found: {', '.join(hits)}"] if hits else []
    if question == Q_GAPS:
        return _evidence_gap_reasons(c)
    return []


def run_research_review(comparisons: List[Dict[str, Any]], question: str) -> List[Dict[str, Any]]:
    """Filter preloaded records. Returns [{'finding': record, 'reasons': [...]}, ...]."""
    if question not in RESEARCH_QUESTIONS:
        raise ValueError(f"Unknown research question: {question!r}")
    out = []
    for c in comparisons:
        reasons = match_reasons(c, question)
        if reasons:
            out.append({"finding": c, "reasons": reasons})
    return out


# ---- challenge view -----------------------------------------------------------------------
def _list_or_missing(items: List[str], what: str) -> Tuple[List[str], Optional[str]]:
    if items:
        return list(items), None
    return [], (
        f"No {what} is recorded for this finding in the project data. This reflects missing "
        "recorded evidence, not proof that none exists."
    )


def challenge_view(c: Dict[str, Any], challenge: str) -> Dict[str, Any]:
    """Return {'heading', 'items', 'note', 'code'} for the analyst-challenge selector."""
    ea = c.get("evidence_assessment", {})
    mv = c.get("metric_verification", {})
    if challenge == CH_SUPPORT:
        items, note = _list_or_missing(ea.get("supporting_evidence", []), "supporting evidence")
        return {"heading": CHALLENGES[challenge], "items": items, "note": note, "code": None}
    if challenge == CH_CONTRARY:
        items, note = _list_or_missing(ea.get("contrary_evidence", []), "contrary evidence")
        return {"heading": CHALLENGES[challenge], "items": items, "note": note, "code": None}
    if challenge == CH_ALT:
        items, note = _list_or_missing(ea.get("alternative_explanations", []), "alternative explanation")
        return {"heading": CHALLENGES[challenge], "items": items, "note": note, "code": None}
    if challenge == CH_UNCERTAINTY:
        text = ea.get("limitations_and_uncertainty", "")
        items = [text] if text else []
        note = None if text else (
            "No limitations or uncertainty statement is recorded for this finding. "
            "This is a gap in the record, not evidence of certainty."
        )
        return {"heading": CHALLENGES[challenge], "items": items, "note": note, "code": None}
    if challenge == CH_CALC:
        items = [
            f"Metric: {mv.get('metric_name', 'n/a')}",
            f"Units: {mv.get('units', 'n/a')}",
            f"Baseline / claimed: {mv.get('baseline_label', 'n/a')}",
            f"Reported / target: {mv.get('reported_label', 'n/a')}",
            f"Calculated delta: {mv.get('calculated_delta', 'n/a')}",
            f"Rule triggered: {mv.get('rule_triggered', 'n/a')}",
        ]
        recomputed = safe_pct_change(mv.get("baseline_value"), mv.get("reported_value"))
        note = (
            "Recomputed percent change from the stored baseline_value/reported_value: "
            f"{format_pct(recomputed)}. Stored values may be growth rates or dollar amounts depending "
            "on the record, so compare with the units above."
        )
        return {"heading": CHALLENGES[challenge], "items": items, "note": note,
                "code": mv.get("python_formula") or None}
    raise ValueError(f"Unknown challenge: {challenge!r}")


# ---- Markdown brief -----------------------------------------------------------------------
def _bullets(items: List[str], missing_note: Optional[str]) -> str:
    if items:
        return "\n".join(f"- {i}" for i in items)
    return f"- _{missing_note}_"


def _source_block(label: str, s: Dict[str, Any]) -> str:
    return (
        f"### {label}\n"
        f"- **Document:** {s.get('document_title', 'n/a')} ({s.get('source_id', 'n/a')})\n"
        f"- **Reporting period:** {s.get('reporting_period', 'n/a')}\n"
        f"- **Publication date:** {s.get('publication_date', 'n/a')}\n"
        f"- **Speaker / section:** {s.get('speaker', 'n/a')}\n"
        f"- **Source URL:** {s.get('source_url') or 'not recorded'}\n\n"
        f"> {s.get('exact_excerpt', 'not recorded')}\n"
    )


def build_research_brief(
    c: Dict[str, Any],
    question: str,
    challenge: str,
    reasons: Optional[List[str]] = None,
    generated_on: Optional[str] = None,
) -> str:
    """Markdown brief for one finding. Built only from the record's own fields."""
    mv = c.get("metric_verification", {})
    ea = c.get("evidence_assessment", {})
    sup, sup_note = _list_or_missing(ea.get("supporting_evidence", []), "supporting evidence")
    con, con_note = _list_or_missing(ea.get("contrary_evidence", []), "contrary evidence")
    alt, alt_note = _list_or_missing(ea.get("alternative_explanations", []), "alternative explanation")
    focus = challenge_view(c, challenge)
    origin_url = c.get("statement_origin", {}).get("source_url")
    follow_url = c.get("follow_up_statement", {}).get("source_url")
    urls = [u for u in (origin_url, follow_url) if u]
    user_entered = c.get("severity") == "User-Submitted Verification"

    lines = [
        f"# ARGUS Research Brief: {c.get('comparison_id')} — {c.get('title')}",
        "",
        f"- **Generated:** {generated_on or date.today().isoformat()}",
        f"- **Research question:** {RESEARCH_QUESTIONS.get(question, question)}",
        f"- **Analyst challenge in focus:** {CHALLENGES.get(challenge, challenge)}",
        f"- **Classification:** {c.get('category')}",
        f"- **Periods compared:** {c.get('baseline_period')} → {c.get('target_period')}",
    ]
    if reasons:
        lines.append(f"- **Why it matched this question:** {'; '.join(reasons)}")
    if user_entered:
        lines.append("- **Data origin:** User-entered in this session (not from the preloaded project dataset)")
    lines += [
        "",
        _source_block("Original statement", c.get("statement_origin", {})),
        _source_block("Follow-up statement", c.get("follow_up_statement", {})),
        "## Metric and calculation",
        f"- **Metric:** {mv.get('metric_name', 'n/a')}",
        f"- **Units:** {mv.get('units', 'n/a')}",
        f"- **Baseline / claimed:** {mv.get('baseline_label', 'n/a')}",
        f"- **Reported / target:** {mv.get('reported_label', 'n/a')}",
        f"- **Calculated delta:** {mv.get('calculated_delta', 'n/a')}",
        f"- **Rule triggered:** {mv.get('rule_triggered', 'n/a')}",
        "",
        "```python",
        mv.get("python_formula") or "# no formula recorded",
        "```",
        "",
        "## Evidence",
        "### Supporting evidence",
        _bullets(sup, sup_note),
        "",
        "### Contrary evidence",
        _bullets(con, con_note),
        "",
        "### Alternative explanations",
        _bullets(alt, alt_note),
        "",
        f"## Analyst challenge: {focus['heading']}",
        _bullets(focus["items"], focus["note"] if not focus["items"] else None),
    ]
    if focus["items"] and focus["note"]:
        lines += ["", focus["note"]]
    lines += [
        "",
        "## Source URLs",
        "\n".join(f"- {u}" for u in urls) if urls else "- No source URL recorded.",
        "",
        "## Limitations",
        f"- {ea.get('limitations_and_uncertainty') or 'No limitations statement recorded for this finding.'}",
        f"- {PROTOTYPE_NOTICE}",
        "- Matching scores come from a local rule-based concept matcher; they are not model confidence.",
        "- A divergence is a research lead for an analyst, not an accusation about management.",
        "- Empty evidence lists indicate missing recorded evidence, not proof that none exists.",
        "",
    ]
    return "\n".join(lines)


def brief_filename(c: Dict[str, Any]) -> str:
    cid = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(c.get("comparison_id", "finding")))
    return f"argus_brief_{cid}.md"


# ---- display escaping (Streamlit renders $...$ as LaTeX) ------------------------------------
def md_safe(text: Any) -> str:
    """Escape dollar signs so Streamlit markdown does not treat '$...$' as math."""
    return str(text).replace("$", "\\$")


def html_safe(text: Any) -> str:
    """Escape text for embedding in raw HTML passed to st.markdown(unsafe_allow_html=True)."""
    return html.escape(str(text), quote=False).replace("$", "&#36;")


def safe_link(url: Any, label: str) -> str:
    """HTML anchor for http(s) URLs only; otherwise plain text. Label is escaped."""
    u = str(url or "")
    if u.startswith(("https://", "http://")):
        return f'<a href="{html.escape(u, quote=True)}" target="_blank" style="color:#38BDF8;">{html_safe(label)}</a>'
    return html_safe(label) + " (no valid URL recorded)"
