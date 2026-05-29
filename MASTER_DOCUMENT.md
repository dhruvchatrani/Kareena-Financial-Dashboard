# Kareena Financial Dashboard — Master Document

**Entity:** Unibliss Enterprises  
**Marketplace:** Amazon India (`A21TJRUUN4KGV`)  
**Currency:** INR (₹)  
**Architecture:** Monolithic Python web app (FastAPI + SQLite + TailwindCSS)

---

## 1. What It Is

Kareena is a **self-sovereign ERP and financial auditing tool** purpose-built for Amazon India sellers. It replaces spreadsheets with a locally-hosted web dashboard that:

- Calculates **fully-burdened per-SKU profitability** (direct costs + proportional OpEx allocation)
- Handles **accrual-based accounting** for Amazon's deferred transactions
- Performs **reconciliation auditing** (expected payout vs. actual disbursement)
- Tracks **advertising performance** (ACOS, TACOS, ROAS, search terms)
- Provides **period comparisons** (WoW, MoM, YoY)
- Runs entirely **offline** on a local SQLite database — no data leaves the machine

---

## 2. Directory Map

```
kareena/
├── main.py                     # FastAPI application — 519 lines, 14 routes
├── processor.py                # CSV/XML/XLSX ingestion — 364 lines
├── data_processor.py           # Financial calculations — 553 lines
├── models.py                   # SQLAlchemy ORM — 10 tables, 151 lines
├── database.py                 # SQLite engine/session — 23 lines
├── auditor.py                  # Health check against thresholds — 43 lines
├── config.json                 # 4 alert thresholds
├── .env                        # Amazon SP-API credentials (live)
├── .env.example                # Env var template
├── requirements.txt            # 31 pinned Python packages
├── .gitignore                  # 62 entries
├── README.md                   # Project documentation
├── user_sop.md                 # 8-step monthly operating procedure
├── Start_Dashboard.bat         # Windows one-click launcher
├── kareena_erp.db              # SQLite database (live, 335 KB)
├── FORMULA_DOCUMENTATION.md     # Formula reference (placeholder)
├── templates/                  # 9 Jinja2 HTML templates
│   ├── index.html              # Main dashboard
│   ├── audit.html              # Upload form
│   ├── sku_insights.html       # Per-SKU profitability
│   ├── advertising.html        # Ads dashboard
│   ├── reconciliation.html     # Payout reconciliation
│   ├── promotions.html         # Coupons/deals tracker
│   ├── admin.html              # Admin panel
│   ├── docs.html               # Rendered SOP
│   └── audit_report.html       # Standalone report (unwired)
├── archive/
│   └── api_connector.py        # Archived SP-API client (220 lines, unused)
├── static/                     # Static files (empty)
├── uploads/                    # Temp file staging (ignored)
└── __pycache__/                # Python bytecode
```

---

## 3. Database Schema (SQLAlchemy ORM)

All tables live in `models.py`, backed by `kareena_erp.db` (SQLite).

### financial_events
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| amazon_order_id | String | Indexed; for transfers uses settlement ID |
| posted_date | Date | Transaction date |
| sku | String | Indexed; `SERVICE_FEE` for non-SKU rows |
| type | String | Order, Refund, Reimbursement, Transfer, ShippingService, Other |
| description | String | |
| quantity | Integer | Units ordered |
| product_sales | Float | Gross sales amount |
| fba_fees | Float | FBA fulfillment fees |
| selling_fees | Float | Selling/commission fees |
| refunds | Float | Refund amount |
| total_amount | Float | Net transaction amount |
| promotional_rebates | Float | Coupon/discount costs |
| is_deferred | Boolean | Deferred transaction flag |

### cogs_history
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| sku | String | Indexed |
| unit_cost | Float | Cost per unit |
| effective_start_date | Date | When this cost became active |
| effective_end_date | Date | NULL = currently active |
| gst_inclusive | Boolean | Default true |

### inventory
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| sku | String | Unique, indexed |
| product_name | String | |
| local_stock | Integer | Warehouse stock |
| fbm_stock | Integer | FBM stock |
| fba_stock | Integer | FBA stock |
| lead_time_days | Integer | Default 7 |
| is_manufactured | Boolean | |

### operating_expenses
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| date_incurred | Date | |
| category | String | e.g. 'Rent', 'Salaries', 'Amazon Ads' |
| amount | Float | |
| description | String | |

### ads_metrics
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| report_month | Date | |
| date | Date | |
| campaign_name | String | |
| search_term | String | Customer search term |
| impressions | Integer | |
| clicks | Integer | |
| ctr | Float | Click-through rate |
| spend | Float | Ad spend |
| sales_7d | Float | 7-day attributed sales |
| acos | Float | ACOS % |
| roas | Float | ROAS |
| orders_7d | Integer | |
| units_7d | Integer | |
| cvr | Float | Conversion rate |
| sku | String | Extracted via heuristic |
| brand | String | Extracted via heuristic |

### business_metrics
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| report_month | Date | |
| sku | String | |
| asin | String | |
| title | String | |
| sessions | Integer | |
| page_views | Integer | |
| units_ordered | Integer | |
| unit_session_pct | Float | Conversion % |
| ordered_product_sales | Float | |

### iqo_log
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| week_start | Date | |
| stage | String | Innovate, Quantify, Orchestrate |
| title | String | |
| description | String | |
| metric_before | Float | |
| metric_after | Float | |
| metric_label | String | |
| target_sku | String | |
| outcome | String | Positive, Neutral, Negative |
| orchestrated | Boolean | Baked into system? |
| created_at | DateTime | |

### kanban_cards
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| title | String | |
| description | String | |
| column_name | String | To Do, In Progress, Review, Done |
| assignee | String | |
| due_date | Date | |
| priority | String | Low, Medium, High |
| position | Integer | Ordering |
| created_at | DateTime | |

### sync_logs
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| timestamp | DateTime | |
| status | String | Success / Error |
| details | String | Upload summary |

### promotions
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| name | String | |
| promo_type | String | Coupon, Deal, Lightning Deal, Promotion |
| sku | String | |
| start_date | Date | |
| end_date | Date | |
| discount_pct | Float | |
| discount_amount | Float | |
| total_cost | Float | |
| units_sold | Integer | |
| revenue_generated | Float | |
| notes | String | |
| created_at | DateTime | |

---

## 4. Routes (main.py)

| Route | Method | Template | Purpose |
|-------|--------|----------|---------|
| `/` | GET | index.html | Main dashboard: KPI cards, MoM/YoY comparison, Plotly daily sales & disbursement charts |
| `/sku-insights` | GET | sku_insights.html | Per-SKU profitability with WoW/MoM/YoY sales deltas, cashflow health badges |
| `/advertising` | GET | advertising.html | Ads KPIs, daily trend charts, top 20 search terms by CVR |
| `/reconciliation` | GET | reconciliation.html | Expected vs. actual payout check, deep-dive per-disbursement breakdown |
| `/promotions` | GET | promotions.html | List all promotions |
| `/promotions/add` | POST | redirect | Add a promotion record |
| `/promotions/delete/{id}` | POST | redirect | Delete a promotion |
| `/docs` | GET | docs.html | Render FORMULA_DOCUMENTATION.md as HTML |
| `/admin` | GET | admin.html | Inventory management, COGS versioning, expense logging, DB backup/reset |
| `/admin/backup` | GET | — | Download kareena_erp.db |
| `/admin/inventory` | POST | redirect | Update local stock count for a SKU |
| `/admin/cogs` | POST | redirect | Add/update versioned COGS for a SKU |
| `/admin/expense` | POST | redirect | Log an operating expense |
| `/admin/reset-db` | POST | redirect | DELETE all records from 7 tables |
| `/admin/import-whatsapp` | POST | redirect | Bulk import from WhatsApp Chat folder |
| `/settings` | GET | — | Return config.json |
| `/settings` | POST | — | Update config.json |
| `/audit` | GET | audit.html | Upload form |
| `/upload-manual` | POST | redirect | Accept 5 file types, process via processor.py |

**All pages accept optional `start_date`/`end_date` query params** — default window is last 180 days.

---

## 5. Financial Formulas

### Net Income
```
Net_Income = Sales + Reimbursements - (Refunds + FBA_Fees + Selling_Fees + Ads_Cost + COGS + OpEx + Other_Amazon_Fees + Promotions)
```

### Gross Margin %
```
Gross_Margin_% = (Sales + Reimbursements - Refunds - COGS - FBA_Fees - Selling_Fees - Promotions - Other_Fees) / Sales
```

### Net Margin %
```
Net_Margin_% = Net_Income / Sales
```

### ACOS (Advertising Cost of Sales)
```
ACOS = Ad_Spend / Ad_Attributed_Sales
```
*Uses `sales_7d` from `AdsMetric` table — actual attributed sales from Amazon Ads, not total revenue.*

### TACOS (Total Advertising Cost of Sales)
```
TACOS = Total_Ad_Spend / Gross_Sales
```
*Aggregate: all ad spend burdened against total revenue.*

### ROI
```
ROI = Net_Income / Total_COGS
```

### Revenue Per Unit
```
Revenue_Per_Unit = Sales / Units_Sold
```

### Profit Per Unit
```
Profit_Per_Unit = Net_Income / Units_Sold
```

### Per-SKU True Net Profit (Fully Burdened)
```
SKU_Net_Profit = SKU_Sales + SKU_Reimbursements - (FBA_Fees + Selling_Fees + Refunds + Other_Amazon_Fees + Total_COGS + Promotions)

Allocated_OpEx = (SKU_Sales / Total_Sales) * Total_OpEx

Blended_Net_Profit = SKU_Net_Profit - Allocated_OpEx
```

### Cashflow Health
```
Cashflow_Healthy = Blended_Profit_Per_Unit >= Unit_COGS
```

### Return Rate
```
Return_Pct = Total_Returns / Units_Sold
```

### Reconciliation (Expected Payout)
```
Expected_Payout = Gross_Sales - Refunds + Reimbursements - Other_Fees
Should_Have_Disbursed = Expected_Payout - Reserve_Balance - Total_Deferred
Discrepancy = Should_Have_Disbursed - Actual_Disbursed
Status = 'OK' if |discrepancy| < ₹100, else 'CHECK_REQUIRED'
```

---

## 6. Data Ingestion (processor.py)

### sync_settlement_csv()
- **Auto-detects CSV format**: inspects header rows for "date/time" (detailed format) vs. "date" (transaction view)
- **Detailed format**: columns include SKU, type, product sales, FBA fees, selling fees, quantity, promotional rebates, total
- **Transaction view**: columns include total product charges, amazon fees, other, total (INR); SKU defaults to 'UNKNOWN'
- **Scoped delete**: before inserting, removes existing records matching the same month + deferred flag
- **Event type mapping**: raw type string → Order/Refund/Reimbursement/Transfer/ShippingService/Other
- **Transfer rows**: use settlement ID as `amazon_order_id`; total_amount is the disbursement

### sync_ads_report()
- Accepts XLSX or CSV
- Auto-finds spend column by searching for "spend" in column names (excludes "acos")
- **Per-campaign rows** stored in `AdsMetric` table
- **SKU/Brand extraction heuristic**: splits campaign name on " - "; looks for `B0`-prefixed 10-char ASIN; otherwise uses first segment as brand
- **Total spend upserted** as `OperatingExpense` category 'Amazon Ads'

### sync_business_csv()
- Parses Amazon Business Report CSV
- Extracts per-SKU sessions, page views, units ordered, unit session percentage
- Returns aggregate `{units_ordered, sessions, page_views, conversion_pct}`

### sync_returns_xml()
- Parses Returns XML (tries multiple schemas: `return_quantity`, `returnquantity`, `quantity`)
- Falls back to counting `<Message>` elements
- Returns total return count (used only for display, not stored in a table)

---

## 7. Business Thresholds (config.json)

```json
{
  "target_unit_session_pct": 12.0,
  "max_tacos_pct": 15.0,
  "max_return_pct": 5.0,
  "min_net_profit_per_unit": 200.0
}
```

The **auditor.py** compares actual metrics against these thresholds and generates:
- `CONV_LOW` — unit session % below 12%
- `TACOS_HIGH` — TACOS above 15%
- `REFUND_HIGH` — return rate above 5%

---

## 8. Key Design Decisions

### SQLite + `check_same_thread=False`
FastAPI uses async threads; SQLite requires this flag to allow cross-thread access.

### Scoped Delete on Upload
Before inserting data for a month, existing records for the same month+deferred flag are deleted. This supports clean re-uploads.

### Deferred Transaction Handling
Amazon holds back payments for orders still within the return window. Kareena marks these as `is_deferred=True`:
- **Excluded** from current-period Net Income
- **Tracked separately** as `Owed_Deferred` — shown as money Amazon will pay next period
- When deferred CSV is uploaded, those records are marked `is_deferred=True`

### Proportional OpEx Allocation
Operating expenses (rent, salaries, software) are allocated to SKUs proportionally by revenue: `SKU_Sales / Total_Sales * Total_OpEx`. This gives a "fully-burdened" true profit per SKU.

### Version-Controlled COGS
When a new unit cost is set for a SKU:
1. The existing active record (where `effective_end_date IS NULL`) gets its `effective_end_date` set to today
2. A new record is inserted with `effective_start_date = today` and `effective_end_date = NULL`

### Reconciliation Audit
The system reconstructs Amazon's expected payout from raw transaction data and compares it to actual disbursements. Order IDs that were refunded but never reimbursed are flagged for Seller Support cases.

### CSV Format Detection
Two settlement CSV formats are auto-detected by scanning header rows:
- **Detailed** format: has "date/time" column, per-SKU breakdown with types
- **Transaction View** format: has "date" column, aggregated amounts, no SKU granularity

---

## 9. Archived Component: SP-API Client

`archive/api_connector.py` contains a complete but **unused** Amazon Selling Partner API client:
- **SPAPIClient**: OAuth2 token refresh, `get_financial_events()` with pagination and rate limiting (0.5 req/s), `get_fba_inventory()` for live stock levels
- **AmazonAdsClient**: Stub class (raises `NotImplementedError`)

The app migrated to a **file-upload workflow** instead of live API integration. This file is kept as reference.

---

## 10. Monthly Workflow (user_sop.md)

1. **Upload reports** — Settlement CSV (required), Deferred CSV, Business CSV, Ads XLSX, Returns XML
2. **Review KPIs** — Net Income, Gross Margin %, Net Margin %, Return Rate, TACOS, ROI
3. **Period comparisons** — Sales MoM, Net Income MoM, YoY trends
4. **Advertising dashboard** — ACOS ≤ 25%, ROAS ≥ 3x, pause zero-order search terms
5. **Reconciliation check** — Discrepancy < ₹100, file Seller Support cases for unreimbursed refunds
6. **SKU insights** — Blended profit positive?, Cashflow Healthy?, Profit/Unit ≥ ₹200
7. **IQO Log** — Close last week's experiments, log one new experiment
8. **Accountability Board** — Update Kanban board

---

## 11. Dependencies (requirements.txt)

| Package | Version |
|---------|---------|
| fastapi | 0.115.3 |
| uvicorn | 0.31.1 |
| sqlalchemy | 2.0.36 |
| pandas | 2.2.3 |
| jinja2 | 3.1.4 |
| python-multipart | 0.0.14 |
| openpyxl | 3.1.5 |
| markdown | 3.7 |
| python-dotenv | 1.0.1 |
| pydantic | 2.10.1 |
| requests | 2.32.3 |
| ruff | 0.7.3 |

Python >= 3.10 required.

---

## 12. Running the App

### Windows
Double-click `Start_Dashboard.bat` (auto-creates venv, installs deps, starts server).

### Manual (any OS)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

### Tests
**None.** The repository has no test files, no test framework configured, and no automated tests.

---

## 13. Security Notes

- **No authentication** — any local user who can reach `127.0.0.1:8000` has full access, including DB reset
- **Live credentials in `.env`** — Amazon SP-API client ID, secret, and refresh token are stored in plaintext (`.gitignore` prevents accidental commit)
- **No input sanitization** beyond Pandas parsing — uploaded CSV/XML/XLSX files are processed directly
- **No rate limiting** on upload endpoints

---

## 14. Known Issues / Technical Debt

- `clean_numeric()` is **duplicated** in both `processor.py` and `data_processor.py`
- `Blended_Profit_Per_Unit` column reference in `data_processor.py:268` (`sku_stats['Cashflow_Healthy'] = sku_stats['Blended_Profit_Per_Unit'] >= sku_stats['Unit_COGS']`) references a column name that doesn't exist (only `Blended_Profit_Per_Sale` is computed)
- `FORMULA_DOCUMENTATION.md` does not exist — the `/docs` route creates a placeholder if missing
- `audit_report.html` template is not wired to any route
- `archive/api_connector.py` is unused legacy code
- No automated tests
- Date extraction heuristic in WhatsApp import (`guess_date()`) is fragile
- All templates load TailwindCSS and Plotly.js from CDN — requires internet on first load
