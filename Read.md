# A Hybrid LLM-Driven Framework for Natural Language-Based Adaptive Pattern Mining in Sales Analytics

> Ask a sales question in plain English. Get an exact, verifiable answer back in plain English.

---

## 1. What is this project? (The idea in plain words)

Retail stores record every sale. Hidden in those records are useful facts, for example:

- *"Customers who buy a red jumbo bag very often buy the pink one too."*
- *"This unusual combination of products is rare, but when it happens it makes a lot of money."*

Computer programs called **pattern mining algorithms** can find such facts. The problem is that
they are hard to use: you must understand technical settings such as *minimum support = 0.02* or
*minimum utility = 500*. A store manager has no way of knowing what values to choose, so they depend
on a data analyst for every question.

Large Language Models (LLMs, such as Claude or ChatGPT) understand plain English very well, but they
**cannot be trusted to count**. If you ask an LLM to find the frequent product combinations in half
a million sales rows, it will produce something that sounds right but is not computed from the data.

**What we are building:** a system where an LLM and the classical mining algorithms each do the
job they are good at.

```
 You type:  "Which products are usually bought together?"
     |
     v
 [ LLM ]   understands the sentence, turns it into a precise, structured request
     |
     v
 [ Validation ]   checks the request makes sense (no contradictions, safe settings)
     |
     v
 [ Mining algorithms ]   Apriori / FP-Growth / rare / EFIM count the real data (exact, never guessed)
     |
     v
 [ LLM ]   turns the raw numbers back into a plain-English business insight
     |
     v
 You read:  "Customers who buy the Jumbo Bag Pink Polkadot also buy the Red Retrospot one
             in 4.5% of baskets. Consider a bundle."
```

**The key design rule:** the LLM never does the mining. It only translates in and out. All counting
is done by real algorithms, so every number in an answer is exact and can be checked.

**Dataset:** UCI *Online Retail*: about 540,000 line items from a UK online retailer
(Dec 2010 to Dec 2011), with invoice number, product, quantity, unit price and timestamp.

---

## 2. Objectives

1. Design a structured **query specification** (a small JSON contract) that can express frequent,
   rare and high-utility mining requests. It is the bridge between English and the algorithms.
2. Build an **LLM module** that turns a sales question in plain English into that specification,
   including inferring sensible thresholds and extracting include/exclude constraints.
3. Integrate established **mining algorithms** as the exact computation backend: Apriori and
   FP-Growth (frequent), a rare-itemset method, and EFIM (high-utility).
4. Build a **validation layer** that catches ambiguous, contradictory or unsafe requests *before*
   anything runs, and asks the user to clarify.
5. Build an **explanation module** that turns raw itemsets into business-readable insights
   (bundling, cross-sell, profitability).
6. Support **adaptive, multi-turn conversation**, so follow-ups such as "now only on Sundays" update the
   previous request instead of starting over.
7. **Evaluate** the system: how often it understands the user correctly, how fast it is compared
   with manual parameter tuning, and how the algorithms compare in runtime.
8. Deliver a **working demo application** (web interface) from question to insight.

---

## 3. What has been done so far

### Step 1: Folder structure and environment

**Goal:** a clean, organised project where each part of the architecture has its own home.

**What we did:**
- Created the folder layout (see section 5), with one folder per layer: `src/mining` (exact
  computation), `src/llm` (language), `src/core` (config and the spec/validation contract).
- Added `requirements.txt` (pandas, openpyxl, mlxtend, pydantic, python-dotenv, fastapi, uvicorn,
  streamlit, anthropic, pytest), `.gitignore`, `.env.example` (for the API key) and this README.
- Added `check_setup.py`, which prints `[ok]` or `[MISSING]` for each library and for Java
  (Java is needed later for the EFIM algorithm).

**Why it matters:** keeping the LLM code and the mining code in separate folders mirrors the
project's central idea, and makes the architecture diagram in the report match the code.

### Step 2: Foundation, which is configuration and data loading/cleaning

**Goal:** turn the raw Excel file into clean, trustworthy baskets that every algorithm can use.

**What we did:**
- `src/core/config.py` holds all paths, column names and constants in one place.
- `src/mining/data_loader.py` loads the raw file (.xlsx or .csv) and cleans it:
  1. Drops rows with missing invoice, product, description or date.
  2. Removes **cancelled orders** (invoice numbers starting with `C`).
  3. **Nets out fully-cancelled purchases.** If the same customer ordered an item and later
     cancelled exactly that quantity, the original order is removed too. Without this, two giant
     orders that were cancelled (80,995 paper-craft birds and 74,215 ceramic jars) would have
     dominated the high-utility results. This was found by checking the real data.
  4. Removes zero/negative quantities and prices, and **fee rows** such as POSTAGE or BANK CHARGES.
  5. Gives each product code **one consistent name** (the raw data has several spellings per code).
  6. **Merges repeated lines** of the same item inside a basket (a basket is a set of items).
  7. Adds a **`utility`** column (quantity x unit price), which high-utility mining needs, and
     time columns (`weekday`, `is_weekend`, `month`, `hour`) so follow-ups like "only Sundays" work later.
- `src/prepare_data.py` runs all of this and writes `data/processed/clean_transactions.csv`.
- `tests/test_data_loader.py` (5 tests) checks every cleaning rule on a small fake dataset.

**Result on the real data:**

| Measure | Value |
|---|---|
| Rows (basket-item lines) | 513,169 |
| Baskets (invoices) | 19,618 |
| Distinct products | 3,773 |
| Total sales value | about 9.8 million |
| Date range | 2010-12-01 to 2011-12-09 |

**Things worth knowing:** the data has **no Saturday orders**, so "weekend" effectively means Sunday.
The typical basket has 15 items, and about 1,500 baskets contain only one item.

### Step 3: Frequent itemset mining (Apriori and FP-Growth)

**Goal:** find product combinations that appear together in many baskets, using exact algorithms.

**Key terms:**
- **Itemset:** a group of products, for example {Jumbo Bag Pink Polkadot, Jumbo Bag Red Retrospot}.
- **Support:** the fraction of baskets that contain the whole itemset. Support 4.5% means 4.5 of
  every 100 baskets contain all of those products.
- **Frequent itemset:** one whose support is at least a chosen minimum (`min_support`).

**What we did:**
- `src/mining/frequent.py` provides one function, `mine_frequent(baskets, min_support, algorithm)`,
  where `algorithm` is `"apriori"` or `"fpgrowth"`. It returns each itemset with its support, basket
  count and size, plus the runtime.
- Single-item baskets are skipped (they cannot contain a pair), so support means "% of the
  18,141 baskets that have 2 or more items".
- `src/demo_frequent.py` lets you try it: `python -m src.demo_frequent 0.01 fpgrowth 10`.
- `tests/test_frequent.py` (6 tests) checks results against a tiny dataset counted by hand.

**Findings from testing on the real data:**
- **Both algorithms return identical itemsets and counts** at every threshold tested (2%, 1%,
  0.7%, 0.5%). Two independent algorithms agreeing is a strong correctness check.
- **Apriori crashed at first** (it tried to use 13.5 GB of memory at 1% support). Switching on its
  low-memory mode fixed it, and it became as fast as FP-Growth.
- **Very low thresholds freeze the system.** At 0.3% support neither algorithm finished in over
  3 minutes. We added a **safety floor of 0.5%** (`MIN_SUPPORT_FLOOR` in `config.py`), and the function
  refuses lower values with a clear message. This protects against a vague request leading the LLM to
  pick a tiny threshold.

| Min support | Itemsets (2+ items) | Apriori | FP-Growth |
|---|---|---|---|
| 2% | 127 | 0.4 s | 1.8 s |
| 1% | 1,601 | 2.1 s | 4.4 s |
| 0.7% | 6,047 | 5.0 s | 7.9 s |
| 0.5% | 22,019 | 15.9 s | 13.3 s |

*(Timings were measured on a cloud sandbox and will differ on your machine, but the pattern holds.)*

Top results at 1% support are sensible: colour variants of the same product bought together, such as
Jumbo Bag Pink Polkadot with Jumbo Bag Red Retrospot (4.5% of baskets) and Green with Roses Regency
Teacup and Saucer (4.1%).

---

## 4. What comes next

### Step 4 (next): Rare itemset mining

**Goal:** find combinations that are **uncommon but meaningful**, for example unusual product pairings
that appear in only a handful of baskets. This is the second of the three pattern types in the project.

**Why it needs its own step:** rare mining is the least standardised of the three types. Simply
lowering `min_support` in the frequent miner does not work, because it hits the explosion problem
described in Step 3. So we need a different approach.

**Planned approach (to be confirmed when we build it):**
- Define "rare" with **two limits**: a ceiling (support at most some small value, so it is
  uncommon) and a floor (appears in at least a minimum number of baskets, so it is not just noise
  from one odd order).
- Count the combinations directly (pairs first, then triples) with exact counting instead of
  enumerating everything, which stays fast on 3,700+ products.
- Return the same result format as `mine_frequent`, so later steps can treat both the same way.
- Add tests with a hand-counted dataset, and check results against the real data.

**Checkpoint at the end of Step 4:** `mine_rare(...)` returns rare-but-meaningful itemsets from the
real data, with passing tests.

### Remaining roadmap

| # | Step | Status |
|---|---|---|
| 1 | Folder structure and environment | Done |
| 2 | Foundation: config, data loading and cleaning | Done |
| 3 | Frequent itemset mining (Apriori, FP-Growth) | Done |
| 4 | Rare itemset mining | **Next** |
| 5 | High-utility mining (EFIM via SPMF) | To do |
| 6 | Unified mining engine: one `run_mining(spec)` | To do |
| 7 | Spec schema and validation | To do |
| 8 | LLM parser (English to spec) | To do |
| 9 | Explanation layer (results to plain English) | To do |
| 10 | Conversation memory (follow-up questions) | To do |
| 11 | Backend API (FastAPI) | To do |
| 12 | User interface (chat-style web page) | To do |
| 13 | Evaluation (accuracy and timing for the report) | To do |
| 14 | Packaging and demo | To do |

---

## 5. Project structure: what each folder and file does

```
pattern-mining-app/
├── README.md               This file
├── requirements.txt        Python libraries the project needs
├── check_setup.py          Checks that libraries and Java are installed
├── .env.example            Template for your API key (copy to .env and fill in)
├── .gitignore              Files git should not track (venv, .env, data files)
│
├── data/
│   ├── raw/                The original downloaded dataset (online_retail.xlsx)
│   └── processed/          Cleaned output (clean_transactions.csv), created by prepare_data
│
├── src/                    All application code
│   ├── core/               THE CONTRACT: shared settings and rules between layers
│   │   └── config.py           Paths, column names, safety limits (e.g. MIN_SUPPORT_FLOOR)
│   │                           (Later: spec schema and validation, Step 7)
│   ├── mining/             THE CALCULATOR: exact algorithms, no LLM involved
│   │   ├── data_loader.py      Loads and cleans the dataset, builds baskets
│   │   └── frequent.py         Apriori / FP-Growth behind mine_frequent()
│   │                           (Later: rare mining, EFIM, unified engine)
│   ├── llm/                THE TRANSLATOR: language layer (empty until Step 8)
│   │                           (Later: English-to-spec parser, result explainer, prompts)
│   ├── prepare_data.py     Run once: cleans the raw data and saves it
│   └── demo_frequent.py    Try frequent mining from the command line
│
├── tests/                  Automated tests (run with: python -m pytest -q)
│   ├── test_data_loader.py     5 tests for the cleaning rules
│   └── test_frequent.py        6 tests for the frequent miner
│
├── api/                    Backend server (empty until Step 11)
├── ui/                     Chat-style web interface (empty until Step 12)
├── evaluation/             Test prompts and benchmark results (empty until Step 13)
└── tools/                  External tools, such as the SPMF jar for EFIM (empty until Step 5)
```

**How the folders map to the architecture:**

| Layer in the report | Folder |
|---|---|
| Language layer (LLM understands and explains) | `src/llm/` |
| Validation layer and the spec contract | `src/core/` |
| Computation layer (exact algorithms) | `src/mining/` |
| Interface | `api/` and `ui/` |
| Evaluation | `evaluation/` |

---

## 6. How to run what exists today

```bash
# 1. Create and activate a virtual environment (Python 3.10 or newer)
python -m venv venv
# Windows: venv\Scripts\activate        Mac/Linux: source venv/bin/activate

# 2. Install libraries and check the setup
pip install -r requirements.txt
python check_setup.py

# 3. Put the dataset at data/raw/online_retail.xlsx, then clean it (takes about a minute)
python -m src.prepare_data

# 4. Run the tests (expect 11 passed)
python -m pytest -q

# 5. Try frequent mining on the real data
python -m src.demo_frequent 0.01 fpgrowth 10
```

Java 11 or newer is needed from Step 5 (EFIM). The LLM steps will need an API key in a `.env` file
(copy `.env.example`).
