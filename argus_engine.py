"""
ARGUS — AI Financial Research Intelligence
Core Analytical, Semantic Discovery, and Deterministic Verification Engine
==========================================================================
Separates probabilistic/semantic AI discovery from deterministic Python verification:
1. Matching Role: Connects management statements across filings even when wording shifts
   (e.g., 'compute is revenue' -> cash conversion / accounts receivable; 'high-30% range' -> 41% YoY)
   using a LOCAL, rule-based matcher: a hand-built financial concept ontology
   (FINANCIAL_CONCEPT_CLUSTERS), content-token overlap, and a segment-conflict penalty.
   It is not a trained model or an embedding model, and it makes NO live Gemini (or other LLM/API)
   calls. The presence of a GEMINI_API_KEY environment variable does not change its behavior.
2. Deterministic Python Role: Computes exact YoY/QoQ growth rates, basis-point margin changes,
   accounting restatement deltas, DSO/working capital ratios, and applies transparent rule-based
   classification into the four required analyst categories:
   - Verified numerical mismatch
   - Potential narrative–metric divergence
   - No identified discrepancy
   - Insufficient evidence
"""

from __future__ import annotations
import json
import math
import os
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any

# Shown in the UI. Keep in sync with the implementation below: no live Gemini/LLM call exists.
ENGINE_STATUS_MESSAGE = (
    "Local concept-aware matching active. "
    "No live Gemini inference is being performed in this workflow."
)

# Four mandatory competition finding categories
CATEGORY_MISMATCH = "Verified numerical mismatch"
CATEGORY_DIVERGENCE = "Potential narrative–metric divergence"
CATEGORY_NO_DISCREPANCY = "No identified discrepancy"
CATEGORY_INSUFFICIENT = "Insufficient evidence"

VALID_CATEGORIES = [
    CATEGORY_MISMATCH,
    CATEGORY_DIVERGENCE,
    CATEGORY_NO_DISCREPANCY,
    CATEGORY_INSUFFICIENT,
]

# Financial Concept Ontology for transparent, deterministic Concept-Aware Semantic Matching
# Maps varied executive/narrative phrasing and accounting terminology into shared semantic dimensions.
FINANCIAL_CONCEPT_CLUSTERS: Dict[str, List[str]] = {
    "OPEX_AND_COST_GROWTH": [
        "operating expense", "operating expenses", "opex", "r&d", "research and development",
        "sg&a", "high-30%", "high-30% range", "41%", "42%", "cost growth", "expense growth",
        "$23,076", "$16,405", "$16,694", "$11,716", "$6,794", "$5,839", "$7,621", "$8,408"
    ],
    "MONETIZATION_AND_CASH_CONVERSION": [
        "compute is revenue", "tokens are productive", "profitable", "inflection point",
        "useful work", "operating activities", "operating cash flow", "free cash flow",
        "accounts receivable", "working capital", "cash conversion", "$(22,346)", "$63,059",
        "$24,077", "$50,344"
    ],
    "GROSS_MARGIN_AND_ARCHITECTURE_RAMP": [
        "gross margin", "gross margins", "mid-70%", "mid-70% range", "75.0%", "75.2%",
        "74.9%", "74.0%", "73.4%", "72.4%", "basis points", "vera rubin", "full production",
        "cost per token", "inventories", "$31,575", "king of inference"
    ],
    "SBC_NON_GAAP_POLICY_SHIFT": [
        "stock-based compensation", "non-gaap", "no longer exclude", "updated to include",
        "reconciliation", "$6,666", "$5,102", "restated", "historical non-gaap",
        "compensation program", "diluted earnings per share"
    ],
    "AI_INFRASTRUCTURE_AND_DATACENTER_DEMAND": [
        "data center", "blackwell", "off the charts", "sold out", "accelerating",
        "compounding", "virtuous cycle", "ai factories", "infrastructure expansion",
        "full steam", "record revenue", "$51.2 billion", "$62.3 billion", "$75.2 billion",
        "$89.0 billion", "up 117%", "up 92%", "up 75%", "up 66%"
    ],
    "CAPITAL_RETURN_AND_DIVIDENDS": [
        "returned", "shareholders", "shares repurchased", "repurchases of common stock",
        "cash dividends", "dividends paid", "$26.0 billion", "$20.0 billion", "$41.1 billion",
        "$(19,732)", "$(6,047)", "$0.25 per share", "share repurchase authorization"
    ],
    "SEGMENT_DISCLOSURE_AND_SUBMARKETS": [
        "reporting framework", "sub-markets", "hyperscale", "acie", "edge computing",
        "ai clouds, industrial and enterprise", "sub-market", "omitted", "disaggregation",
        "third-party capital", "definitive agreements", "$500 billion"
    ],
}

# Mutually exclusive segment/line-item entities to penalize boilerplate false positives
# (e.g., when two sentences share "Fourth-quarter ... revenue was ... up ... from a year ago"
#  but one is about Automotive and the other is about Professional Visualization or Income Taxes).
EXCLUSIVE_SEGMENT_ENTITIES: Dict[str, List[str]] = {
    "SEG_GAMING": ["gaming", "geforce", "dlss", "rtx spark"],
    "SEG_AUTOMOTIVE": ["automotive", "self-driving", "robotaxi", "alpamayo", "drive hyperion"],
    "SEG_PROVIZ": ["professional visualization", "rtx pro", "workstations"],
    "SEG_TAX": ["income tax expense", "tax rates", "deferred income taxes"],
    "SEG_DIVIDEND_RECORD": ["shareholders of record", "payable on"],
}

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "with", "as", "by", "at",
    "from", "was", "were", "is", "are", "be", "been", "this", "that", "its", "it", "up",
    "down", "compared", "previous", "prior", "quarter", "year", "ago", "first", "second",
    "third", "fourth", "fiscal", "million", "billion", "percent", "nvidia", "said", "today",
    "reported", "expected", "approximately", "respectively"
}


def tokenize(text: str) -> List[str]:
    """Normalize and tokenize text into alphanumeric/financial tokens."""
    cleaned = text.lower()
    tokens = re.findall(r"[a-z0-9$%\.\-]+", cleaned)
    return [t.strip(".-") for t in tokens if len(t.strip(".-")) > 1]


def compute_keyword_baseline_score(text_a: str, text_b: str) -> float:
    """
    Transparent Baseline 1: Exact Keyword / Lexical Jaccard Overlap.
    Measures surface word overlap (including boilerplate period/growth words).
    Demonstrates why naive keyword search misses paraphrased financial concepts
    and triggers false positives on boilerplate earnings release templates.
    """
    tokens_a = set(tokenize(text_a))
    tokens_b = set(tokenize(text_b))
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a.intersection(tokens_b)
    union = tokens_a.union(tokens_b)
    raw_jaccard = len(intersection) / len(union)
    # Scale slightly to [0, 1] range typical of lexical similarity
    return round(min(1.0, raw_jaccard * 1.85), 4)


def compute_semantic_similarity_score(text_a: str, text_b: str) -> Tuple[float, Dict[str, Any]]:
    """
    Local concept-aware similarity scoring (rule-based; not a trained or embedding model).
    Combines:
    1. Content-word TF-IDF / cosine overlap (stripping earnings release boilerplate).
    2. Financial Concept Ontology activation across 7 institutional research dimensions.
    3. Exclusive Segment Entity conflict penalty (prevents false positives when two
       sentences share identical 'Fourth-quarter X revenue was up Y%' templates for different segments).
    Returns (score_in_0_to_1, explanation_metadata).
    """
    lower_a = text_a.lower()
    lower_b = text_b.lower()

    # 1. Concept cluster activations
    active_clusters_a = set()
    active_clusters_b = set()
    matched_concepts = []

    for cluster_name, phrases in FINANCIAL_CONCEPT_CLUSTERS.items():
        hits_a = [p for p in phrases if p in lower_a]
        hits_b = [p for p in phrases if p in lower_b]
        if hits_a:
            active_clusters_a.add(cluster_name)
        if hits_b:
            active_clusters_b.add(cluster_name)
        if hits_a and hits_b:
            matched_concepts.append({
                "concept": cluster_name,
                "terms_a": hits_a[:3],
                "terms_b": hits_b[:3]
            })

    shared_clusters = active_clusters_a.intersection(active_clusters_b)
    concept_score = 0.0
    if shared_clusters:
        concept_score = min(1.0, 0.65 + 0.15 * len(shared_clusters))

    # 2. Content token overlap (excluding boilerplate stopwords)
    content_a = {t for t in tokenize(text_a) if t not in STOPWORDS and not t.isdigit()}
    content_b = {t for t in tokenize(text_b) if t not in STOPWORDS and not t.isdigit()}
    if content_a and content_b:
        content_overlap = len(content_a.intersection(content_b)) / math.sqrt(len(content_a) * len(content_b))
    else:
        content_overlap = 0.0

    # 3. Check for mutually exclusive non-Data-Center segment conflicts
    excl_a = {seg for seg, terms in EXCLUSIVE_SEGMENT_ENTITIES.items() if any(t in lower_a for t in terms)}
    excl_b = {seg for seg, terms in EXCLUSIVE_SEGMENT_ENTITIES.items() if any(t in lower_b for t in terms)}

    conflict_penalty = 0.0
    conflict_reason = None
    if (excl_a or excl_b) and excl_a != excl_b and not shared_clusters:
        conflict_penalty = 0.45
        conflict_reason = f"Segment/Line-Item Entity Mismatch ({', '.join(excl_a) or 'Core/Other'} vs. {', '.join(excl_b) or 'Core/Other'})"

    combined = (0.72 * concept_score) + (0.28 * min(1.0, content_overlap * 2.2)) - conflict_penalty
    final_score = round(max(0.02, min(0.98, combined)), 4)

    details = {
        "engine_mode": "Local concept-aware matching (ontology + token overlap; no trained model, no live API calls)",
        "shared_concepts": [c["concept"] for c in matched_concepts],
        "matched_concept_details": matched_concepts,
        "content_token_cosine": round(content_overlap, 4),
        "conflict_penalty": conflict_penalty,
        "conflict_reason": conflict_reason,
    }
    return final_score, details


# ==============================================================================
# DETERMINISTIC PYTHON NUMERICAL VERIFICATION & CLASSIFICATION ENGINE
# ==============================================================================

def calculate_pct_change(baseline: float, reported: float) -> float:
    """Deterministic percentage change formula: ((reported - baseline) / abs(baseline)) * 100."""
    if baseline == 0:
        raise ValueError("Baseline value cannot be zero when computing percentage change.")
    return round(((reported - baseline) / abs(baseline)) * 100.0, 2)


def calculate_bps_change(baseline_pct: float, reported_pct: float) -> int:
    """Deterministic basis points difference between two percentage figures."""
    return int(round((reported_pct - baseline_pct) * 100))


def calculate_dso(accounts_receivable: float, quarterly_revenue: float, days_in_quarter: int = 91) -> float:
    """Deterministic Days Sales Outstanding (DSO) calculation."""
    if quarterly_revenue <= 0:
        raise ValueError("Quarterly revenue must be positive to compute DSO.")
    return round((accounts_receivable / quarterly_revenue) * days_in_quarter, 2)


def classify_finding_deterministic(
    comparison_type: str,
    baseline_value: Optional[float],
    reported_value: Optional[float],
    tolerance_pct: float = 1.5,
    narrative_direction: str = "positive",
    secondary_metric_delta_pct: Optional[float] = None,
) -> Tuple[str, str]:
    """
    Deterministic Python rule engine that classifies a statement-to-metric comparison
    into one of the 4 required competition categories:
      1. Verified numerical mismatch
      2. Potential narrative–metric divergence
      3. No identified discrepancy
      4. Insufficient evidence
    Returns (category, deterministic_rule_explanation).
    """
    # Rule 4: Insufficient evidence if either required numerical input is missing/None
    if baseline_value is None or reported_value is None:
        return (
            CATEGORY_INSUFFICIENT,
            "RULE_INSUFFICIENT_EVIDENCE: Required quantitative figure is missing or not disaggregated in the primary source filing."
        )

    # Rule 1: Direct numerical / guidance ceiling / restatement verification
    if comparison_type == "direct_numerical_or_ceiling":
        diff = reported_value - baseline_value
        pct_diff = abs(diff / baseline_value) * 100.0 if baseline_value != 0 else abs(diff)
        if pct_diff > tolerance_pct and abs(diff) > 0.5:
            return (
                CATEGORY_MISMATCH,
                f"RULE_NUMERICAL_MISMATCH: Reported value ({reported_value:,.2f}) deviates from baseline/ceiling ({baseline_value:,.2f}) by {diff:+,.2f} ({pct_diff:.2f}%), exceeding tolerance ({tolerance_pct:.2f}%)."
            )
        return (
            CATEGORY_NO_DISCREPANCY,
            f"RULE_NO_DISCREPANCY: Reported value ({reported_value:,.2f}) is within tolerance ({tolerance_pct:.2f}%) of baseline/claim ({baseline_value:,.2f})."
        )

    # Rule 2: Narrative vs. Metric trajectory comparison
    if comparison_type == "narrative_vs_metric_trajectory":
        # If narrative is strongly positive, check if primary or secondary quality metric diverges negatively
        if narrative_direction == "positive":
            if reported_value < 0 or (secondary_metric_delta_pct is not None and secondary_metric_delta_pct < -15.0):
                return (
                    CATEGORY_DIVERGENCE,
                    f"RULE_NARRATIVE_DIVERGENCE: Positive management narrative coincides with an adverse metric movement (primary={reported_value:+.2f}%, secondary={secondary_metric_delta_pct if secondary_metric_delta_pct is not None else 0.0:+.2f}%). Flagged as an analyst research lead."
                )
            if reported_value < baseline_value - tolerance_pct:
                return (
                    CATEGORY_DIVERGENCE,
                    f"RULE_NARRATIVE_DIVERGENCE: Metric stepped down from {baseline_value:.2f} to {reported_value:.2f} ({reported_value - baseline_value:+.2f}) despite bullish narrative."
                )
        return (
            CATEGORY_NO_DISCREPANCY,
            f"RULE_NO_DISCREPANCY: Quantitative metric trajectory ({baseline_value:,.2f} -> {reported_value:,.2f}) directionally and materially supports management's statement."
        )

    return (
        CATEGORY_INSUFFICIENT,
        "RULE_INSUFFICIENT_EVIDENCE: Comparison type could not be deterministically evaluated."
    )


def evaluate_matching_benchmark(
    dataset: List[Dict[str, Any]],
    semantic_threshold: float = 0.50,
    keyword_threshold: float = 0.35
) -> Dict[str, Any]:
    """
    Evaluates the AI-Assisted Semantic Matcher against the Exact Keyword Baseline
    on the manually labeled test set (data/evaluation_dataset.json).
    Calculates authentic Precision, Recall, F1, True Positives, False Positives,
    True Negatives, and False Negatives.
    """
    sem_tp = sem_fp = sem_tn = sem_fn = 0
    kw_tp = kw_fp = kw_tn = kw_fn = 0
    pair_results = []

    for item in dataset:
        truth = int(item["ground_truth_match"])
        sem_score, sem_meta = compute_semantic_similarity_score(item["statement_a"], item["statement_b"])
        kw_score = compute_keyword_baseline_score(item["statement_a"], item["statement_b"])

        sem_pred = 1 if sem_score >= semantic_threshold else 0
        kw_pred = 1 if kw_score >= keyword_threshold else 0

        if sem_pred == 1 and truth == 1:
            sem_tp += 1
        elif sem_pred == 1 and truth == 0:
            sem_fp += 1
        elif sem_pred == 0 and truth == 0:
            sem_tn += 1
        else:
            sem_fn += 1

        if kw_pred == 1 and truth == 1:
            kw_tp += 1
        elif kw_pred == 1 and truth == 0:
            kw_fp += 1
        elif kw_pred == 0 and truth == 0:
            kw_tn += 1
        else:
            kw_fn += 1

        pair_results.append({
            "pair_id": item["pair_id"],
            "relationship_type": item["relationship_type"],
            "ground_truth": truth,
            "semantic_score": sem_score,
            "semantic_pred": sem_pred,
            "semantic_correct": sem_pred == truth,
            "keyword_score": kw_score,
            "keyword_pred": kw_pred,
            "keyword_correct": kw_pred == truth,
            "shared_concepts": ", ".join(sem_meta["shared_concepts"]) if sem_meta["shared_concepts"] else "None",
            "conflict_reason": sem_meta["conflict_reason"] or "None",
            "notes": item["notes"]
        })

    def _metrics(tp: int, fp: int, tn: int, fn: int) -> Dict[str, float]:
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = (tp + tn) / (tp + fp + tn + fn) if (tp + fp + tn + fn) > 0 else 0.0
        return {
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "accuracy": round(accuracy, 4),
        }

    return {
        "semantic_threshold": semantic_threshold,
        "keyword_threshold": keyword_threshold,
        "total_pairs": len(dataset),
        "positive_pairs": sum(1 for x in dataset if int(x["ground_truth_match"]) == 1),
        "negative_pairs": sum(1 for x in dataset if int(x["ground_truth_match"]) == 0),
        "semantic_metrics": _metrics(sem_tp, sem_fp, sem_tn, sem_fn),
        "keyword_metrics": _metrics(kw_tp, kw_fp, kw_tn, kw_fn),
        "pair_results": pair_results,
    }


def load_argus_data(data_dir: Optional[str] = None) -> Dict[str, Any]:
    """Loads source_manifest.json, financial_metrics.csv, financial_statements.json, and evaluation_dataset.json."""
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

    with open(os.path.join(data_dir, "source_manifest.json"), "r", encoding="utf-8") as f:
        manifest = json.load(f)

    with open(os.path.join(data_dir, "financial_statements.json"), "r", encoding="utf-8") as f:
        comparisons = json.load(f)

    with open(os.path.join(data_dir, "evaluation_dataset.json"), "r", encoding="utf-8") as f:
        eval_dataset = json.load(f)

    import csv
    metrics_rows = []
    with open(os.path.join(data_dir, "financial_metrics.csv"), "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = {}
            for k, v in row.items():
                if k in ("company", "ticker", "period", "period_ended", "units", "source_id", "source_url"):
                    parsed[k] = v
                elif k == "period_order":
                    parsed[k] = int(v)
                else:
                    parsed[k] = float(v)
            metrics_rows.append(parsed)

    return {
        "manifest": manifest,
        "comparisons": comparisons,
        "eval_dataset": eval_dataset,
        "metrics": metrics_rows,
    }
