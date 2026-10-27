# ARGUS — AI Financial Research Intelligence
**See Beyond the Narrative** | *Independent Prototype Built for the UTD JSOM AI-in-Finance Case Competition (Fall 2026)*

> **Disclaimer:** ARGUS is an independent academic competition prototype designed for the **Investment Research Team at Charles Schwab** (Westlake, TX). It is **not** an official Charles Schwab product, service, or endorsement. **NVIDIA Corporation (NASDAQ: NVDA)** is the initial public equity research subject analyzed, not the customer. ARGUS does not predict stock prices, issue buy/sell recommendations, or accuse management of misleading investors.

---

## 1. Product Concept & Business Value for Charles Schwab

Equity research analysts and portfolio managers at **Charles Schwab** (supporting Schwab Asset Management, Schwab Equity Ratings, and institutional/retail research) must synthesize hundreds of pages of quarterly earnings releases, Form 10-K/10-Q filings, and GAAP-to-Non-GAAP reconciliations under tight post-earnings deadlines.

A critical challenge in fundamental research is **narrative drift and accounting methodology shifts across periods**:
1. Management often describes multi-quarter trajectories using evolving qualitative language (e.g., shifting from *"virtuous cycle of AI"* in Q3 FY26 to *"agentic AI inflection point"* in Q4 FY26 to *"tokens are productive and profitable. Now, compute is revenue"* in Q2 FY27).
2. Accounting definitions and comparative tables change across periods (e.g., NVIDIA's Q1 FY27 decision to stop excluding Stock-Based Compensation from Non-GAAP metrics and restate prior-period Non-GAAP tables).
3. Top-line accrual momentum can diverge from underlying cash-flow and working-capital mechanics (e.g., Q2 FY27 sequential revenue growth of **+17.90% QoQ** coinciding with a **-52.18% QoQ** drop in Operating Cash Flow due to a **+$22,349M** surge in Accounts Receivable).

### The ARGUS Differentiator: The 5-Step Auditable Chain
Unlike generic LLM chatbots that summarize filings without verifying numbers (or hallucinate arithmetic), **ARGUS** enforces a strict separation of responsibilities:

```text
[1. Company Statement] ──► [2. Original Source] ──► [3. Financial Metric] ──► [4. Deterministic Python] ──► [5. Analyst Finding]
  Verbatim CEO/CFO quote     SEC EDGAR / IR URL      Reported GAAP/Non-GAAP     Exact formula & rule          4-tier institutional
  or guidance excerpt        & publication date       figure with units ($M)     verification (zero LLM math)   classification
```

* **AI's Role (Probabilistic / Semantic Discovery):** Connects statements, footnotes, and financial line items across reporting periods even when executive phrasing changes completely.
* **Python's Role (Deterministic Verification):** Executes 100% of percentage growth rates, basis-point margin checks, Days Sales Outstanding (DSO) math, restatement reconciliations, and classification rules.

---

## 2. Core Application Components

1. **A. Executive Dashboard:**
   * Institutional dark charcoal aesthetic (`#0D1117` / `#151B26`) with restrained cyan, emerald, amber, and rose accents.
   * Functional company and reporting-period selectors (`Q1 FY26` through `Q2 FY27`).
   * KPI cards summarizing verified filings reviewed (`6`), auditable comparisons (`7`), and findings by category.
   * Interactive Plotly dual-axis charts comparing Revenue vs. Operating Cash Flow & Accounts Receivable, and Original vs. SBC-Restated Non-GAAP Operating Expenses.
2. **B. Narrative-versus-Metrics Timeline:**
   * Multi-period timeline overlaying verbatim management statements from `Q1 FY26` through `Q2 FY27` alongside reported GAAP and Non-GAAP metrics.
   * Every displayed number includes its exact source ID, clickable URL, reporting period ended date, and units (`$ in millions`, `%`, `$ per diluted share`).
3. **C. Evidence Explorer & Interactive Graph:**
   * Interactive Plotly node-edge Evidence Relationship Graph tracing `Origin Statement → Follow-Up Filing & Metric → Python Verification → Analyst Finding`.
   * Side-by-side inspection of verbatim quotes, source URLs, publication dates, exact Python code/formulas, supporting evidence, contrary/mitigating evidence, alternative explanations, and limitations.
4. **D. Finding Inspector & Live Evidence Ingestion:**
   * Filters findings across the four mandatory categories:
     1. **Verified numerical mismatch** (e.g., `CMP-NVDA-001` FY26 OpEx growth of 40.66% GAAP / 42.49% Non-GAAP vs. Q2 FY26 guidance of *"high-30% range"*; `CMP-NVDA-002` Q4 FY26 Non-GAAP OpEx shifting by +$1,564M / +30.65% between consecutive releases due to SBC restatement).
     2. **Potential narrative–metric divergence** (e.g., `CMP-NVDA-003` Q2 FY27 *"compute is revenue"* narrative vs. -52.18% QoQ Operating Cash Flow drop and +54.90% QoQ Accounts Receivable surge; `CMP-NVDA-004` Vera Rubin full-production ramp vs. -100 bps Q3 FY27 gross margin compression to 74.0%).
     3. **No identified discrepancy** (e.g., `CMP-NVDA-005` Data Center revenue scaling from $41.1B in Q2 FY26 to $89.0B in Q2 FY27, up 117% YoY; `CMP-NVDA-006` Q2 FY27 ~$26.0B shareholder return claim vs. $19,732M buybacks + $6,047M dividends = $25,779M cash flow).
     4. **Insufficient evidence** (e.g., `CMP-NVDA-007` Q1 FY27 commitment to report *Hyperscale* vs. *ACIE* Data Center sub-markets and Q2 FY27 >$500B third-party financing announcement, where dollar sub-market disaggregation is omitted from the earnings release tables).
   * Includes an interactive **Custom Sourced Evidence Form** allowing analysts to paste new excerpts and metrics for live semantic matching and deterministic Python rule evaluation.
5. **E. Responsible AI & Labeled Benchmark Evaluation:**
   * Evaluates ARGUS's **Concept-Aware Financial Semantic Engine** against an **Exact Keyword / Lexical Overlap Baseline** across a 12-pair manually labeled test set (`data/evaluation_dataset.json`).
   * At default thresholds (`0.50` semantic / `0.22` keyword), the Concept-Aware Semantic Engine achieves **100.0% Precision, 100.0% Recall, 100.0% F1, and 0 False Positives**, whereas the Exact Keyword Baseline achieves **33.3% Precision, 12.5% Recall, 18.2% F1, and 2 False Positives** (tricked by boilerplate sentence templates across Automotive, Gaming, and ProViz segments).

---

## 3. Authentic Sources & Financial Integrity (`data/source_manifest.json`)

All figures and verbatim quotes in ARGUS are extracted exclusively from authentic public NVIDIA filings and press releases:
1. **NVIDIA Q2 FY2027 Earnings Release (Aug 26, 2026 — Period Ended July 26, 2026):**
   * [NVIDIA Newsroom Release](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2027/) | [SEC Form 8-K Exhibit 99.1](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000073/q2fy27pr.htm)
2. **NVIDIA Q1 FY2027 Earnings Release (May 20, 2026 — Period Ended April 26, 2026):**
   * [NVIDIA Newsroom Release](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-first-quarter-fiscal-2027) | [NVIDIA Investor Relations](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-First-Quarter-Fiscal-2027/default.aspx)
3. **NVIDIA Q4 & Full-Year FY2026 Earnings Release (Feb 25, 2026 — Period Ended January 25, 2026):**
   * [NVIDIA Investor Relations](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Fourth-Quarter-and-Fiscal-2026/) | [SEC Form 8-K Exhibit 99.1](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000019/q4fy26pr.htm)
4. **NVIDIA FY2026 Form 10-K Annual Report (Filed Feb 25, 2026 — Period Ended January 25, 2026):**
   * [SEC EDGAR Form 10-K (`nvda-20260125.htm`)](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000021/nvda-20260125.htm) | [SEC EDGAR CIK 0001045810](https://www.sec.gov/edgar/browse/?CIK=1045810&owner=exclude)
5. **NVIDIA Q3 FY2026 Earnings Release (Nov 19, 2025 — Period Ended October 26, 2025):**
   * [NVIDIA Newsroom Release](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2026) | [SEC Form 8-K Exhibit 99.1](https://www.sec.gov/Archives/edgar/data/1045810/000104581025000228/q3fy26pr.htm)
6. **NVIDIA Q2 FY2026 Earnings Release (Aug 27, 2025 — Period Ended July 27, 2025):**
   * [NVIDIA Newsroom Release](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2026) | [SEC Form 8-K Exhibit 99.1](https://www.sec.gov/Archives/edgar/data/1045810/000104581025000207/q2fy26pr.htm)

---

## 4. Project Directory Structure

```text
ARGUS/
├── app.py                        # Main Streamlit application (5 interactive tabs + institutional dark UI)
├── argus_engine.py               # Core semantic matcher, keyword baseline, and deterministic Python rule engine
├── requirements.txt              # Python dependencies (streamlit, pandas, plotly, pytest)
├── README.md                     # Setup, architecture, verified sources, and limitations documentation
├── AI_LOG.md                     # Detailed AI deployment log, prompts, verification checks, and corrections
├── DEMO_SCRIPT.md                # Concise 3–5 minute competition video presentation script
├── data/
│   ├── source_manifest.json      # Authentic source manifest (titles, URLs, dates, periods, extracted metrics)
│   ├── financial_metrics.csv     # Verified quarterly GAAP & Non-GAAP metrics (Q1 FY26 – Q2 FY27) with units
│   ├── financial_statements.json # 7 auditable comparisons across all 4 required finding categories
│   └── evaluation_dataset.json   # 12 manually labeled statement pairs for Precision/Recall/FP benchmarking
└── tests/
    └── test_argus.py             # Automated unit & integration tests (pytest & unittest compatible)
```

---

## 5. Setup, Execution & Testing Instructions

### Prerequisites
* Python 3.9+ (no API keys, paid services, or database setup required).

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Automated Tests
You can run the test suite with either `pytest` or Python's built-in `unittest`:
```bash
pytest -v
# OR without pytest installed:
python3 tests/test_argus.py
```

### 3. Launch the Streamlit Application
```bash
streamlit run app.py
```
The app will open in your browser at `http://localhost:8501`.

---

## 6. Assumptions, Risks & Limitations
1. **A Divergence is a Research Lead, Not Proof of Dishonesty:** Variations between forward-looking guidance and realized metrics (or between accrual revenue and operating cash flow) frequently result from shipment linearity, architecture transition yields, or accounting policy updates.
2. **Transparent Local Semantic Engine vs. LLM Embeddings:** To guarantee 100% offline reproducibility without mandatory paid API keys, ARGUS runs a deterministic Concept-Aware Financial Semantic Vector Engine by default and clearly labels its engine mode in the UI.
3. **Granularity of Press Release Tables vs. Full 10-Q Footnotes:** Quarterly press releases summarize high-level segments (Data Center and Edge Computing); granular customer concentration and sub-market splits (*Hyperscale* vs. *ACIE*) require parsing subsequent Form 10-Q footnotes (explicitly flagged under `Insufficient evidence`).
