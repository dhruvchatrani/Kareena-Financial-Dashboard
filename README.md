# Kareena Financial Dashboard

> A custom, self-sovereign ERP and financial auditing tool built for Amazon India sellers.

Kareena is a privately-hosted web application that replaces generic spreadsheets with a purpose-built financial intelligence platform. It is designed to give Amazon sellers a clear, accurate, and fully-burdened view of their business — from gross revenue down to true per-SKU profitability — without sharing sensitive data with any third-party SaaS tool.

---

##  Key Features

###  Accrual-Based Financial Processing
Amazon settlements are notoriously complex. Kareena correctly handles **deferred transactions** (orders still within the return window that are held back from the current settlement) to ensure your Net Income figure reflects the actual period it belongs to — not just when Amazon happened to include it in a payout.

###  Fully-Burdened SKU Profitability
Every SKU's **True Net Profit** is calculated by:
1. Deducting all direct costs: COGS, FBA fees, selling fees, refunds, and promotions.
2. Allocating a proportional share of **Operating Expenses** (salaries, software, rent) based on revenue contribution.

This means no SKU can hide behind blended averages — you see exactly which products are genuinely profitable for the company.

###  IQO Experimental Tracking (Innovate → Quantify → Orchestrate)
A structured framework for running one change at a time (image, price, keyword, listing copy) and measuring its impact using real before/after metrics fetched directly from your data. Successful experiments are flagged for **Orchestration** — permanently baking the winning change into your strategy.

###  Reconciliation Auditing
Kareena calculates the **Expected Payout** (what Amazon *should* be depositing) and compares it against the actual disbursement. Any discrepancy is surfaced immediately, allowing you to raise Amazon Seller Support cases before money is lost or written off.

###  Advertising Intelligence
Tracks ACOS, TACOS, ROAS, CVR, CPC, and daily Spend vs. Sales trends with clean, honest single-axis Plotly charts — no misleading dual-axis distortions.

###  Complete Audit Trail
All uploaded financial data is persisted in a local SQLite database. Month-on-month and year-on-year period comparisons are computed automatically, so you can track trajectory without manually updating any formulas.

---

##  Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+, FastAPI |
| **Data Processing** | Pandas |
| **Database** | SQLite (via SQLAlchemy) |
| **Frontend** | TailwindCSS (CDN), Plotly.js |
| **Templating** | Jinja2 |
| **SOP Engine** | Python-Markdown |

---

##  Installation & Setup (Windows)

### Prerequisites

1. **Install Python 3.10 or higher**
   - Download from [python.org/downloads](https://www.python.org/downloads/)
   -  **Critical**: On the first installer screen, check **"Add Python to PATH"** before clicking Install.
   - After installation, verify by opening Command Prompt and typing: `python --version`

---

### Step 1: Download the Repository

**Option A — Git (recommended):**
```bash
git clone https://github.com/your-username/kareena.git
cd kareena
```

**Option B — Manual download:**
- Click the green **Code** button on GitHub → **Download ZIP**
- Extract the ZIP to a folder of your choice (e.g., `C:\Users\YourName\kareena`)

---

### Step 2: Start the Dashboard

Inside the project folder, **double-click** the file:

```
Start_Dashboard.bat
```

This script will:
1. Automatically create a Python virtual environment (`venv/`) on first run.
2. Install all required dependencies from `requirements.txt`.
3. Start the local web server.
4. Open the dashboard in your default browser at **http://127.0.0.1:8000**.

> **Note:** On subsequent launches, the setup steps are skipped and the server starts immediately.

---

##  Monthly Workflow

### Uploading Your Data

Navigate to **Upload** in the navigation bar (or go to `/audit`). Each month, upload the following reports exported from your Amazon Seller Central account:

| Report | Source in Seller Central | Required? |
|---|---|---|
| **Settlement CSV** | Payments → Transaction View → "All Transactions" → Download Detailed Report |  Required |
| **Deferred Transactions CSV** | Payments → Transaction View → "Deferred Transactions" | Optional |
| **Business Report CSV** | Reports → Business Reports → Detail Page Sales & Traffic | Optional |
| **Advertising Report (XLSX)** | Campaign Manager → Download → Sponsored Products Search Term Report | Optional |
| **Returns Report (XML)** | Reports → Fulfillment → Returns | Optional |

Select the correct **Audit Month**, attach your files, and click **Upload & Sync**. The dashboard will update automatically.

---

### Monthly Review Checklist

Follow the 8-step SOP (available in the **SOP** tab) after each upload:

1. Upload monthly reports
2. Review key KPIs on the Dashboard
3. Check period comparisons (MoM, YoY)
4. Review the Advertising Dashboard
5. Run the Reconciliation check
6. Analyse SKU Insights
7. Log and review IQO experiments
8. Update the Accountability Board

---

##  Project Structure

```
kareena/
 main.py                  # FastAPI routes and application entrypoint
 models.py                # SQLAlchemy database models
 data_processor.py        # Core financial calculation engine
 processor.py             # Raw data parsing (CSV, XML, XLSX ingestion)
 database.py              # Database session configuration
 config.json              # Business configuration (alert thresholds, OpEx targets)
 user_sop.md              # Editable Standard Operating Procedure
 FORMULA_DOCUMENTATION.md # Complete formula reference for all metrics
 requirements.txt         # Python dependencies
 Start_Dashboard.bat      # One-click launcher for Windows
 templates/               # Jinja2 HTML templates
 uploads/                 # Temporary file staging (git-ignored)
```

---

##  Formula Reference

All financial formulas used in this application — including the exact variables, business reasoning, and calculation methodology — are documented in **[FORMULA_DOCUMENTATION.md](./FORMULA_DOCUMENTATION.md)**.

Key metrics include Net Income, Gross Margin %, ACOS, TACOS, True Profit / Sale, and per-SKU Allocated OpEx.

---

##  Data & Privacy

All data is stored **locally** on your machine in a SQLite database file (`kareena.db`). No data is transmitted to any external server or cloud service. The application runs entirely offline after initial dependency installation.

---

##  Disclaimer

This tool is purpose-built for a specific Amazon India seller account. Formula thresholds, fee assumptions, and currency formatting (₹) reflect that configuration. Adjustments for different marketplaces or account structures may require modifying `data_processor.py` and `config.json`.
