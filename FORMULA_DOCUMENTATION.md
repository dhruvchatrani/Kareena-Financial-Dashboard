# Kareena Financial Dashboard — Formula Documentation

This document details every major financial formula used in this application, the exact variables involved, and the business reasoning behind each calculation. It is intended as a reference guide for understanding how your financial data is being interpreted and presented.

---

## 1. Top-Line & Bottom-Line Metrics

### Net Income
> **The true bottom-line profit after every cost and fee.**

**Formula:**
```
Net Income = (Gross Sales + Reimbursements) - (Refunds + FBA Fees + Selling Fees + Ads Cost + COGS + Operating Expenses + Other Amazon Fees + Promotions)
```

**Variables:**
- `Gross Sales` — Total revenue from all customer orders (before any deductions)
- `Reimbursements` — Payments received from Amazon for lost or damaged inventory in their warehouses
- `Refunds` — Total value of refunds issued back to customers
- `FBA Fees` — Amazon's Fulfilment by Amazon fees, which includes all outbound shipping, weight handling, and return shipping/processing fees
- `Selling Fees` — Amazon's percentage-based referral commission on each sale
- `Ads Cost` — Total amount spent on Sponsored Products campaigns
- `COGS` (Cost of Goods Sold) — The unit purchase cost of all products sold
- `Operating Expenses (OpEx)` — Business overheads such as salaries, software subscriptions, rent, and professional services
- `Other Amazon Fees` — Miscellaneous Amazon charges (e.g., account subscription fees, long-term storage fees, labelling fees)
- `Promotions` — Total value of coupons, deals, and promotional rebates offered to customers

**Business Reasoning:**
Provides a true, conservative bottom-line figure by capturing every single deduction Amazon applies — including the easily-overlooked "Other" fee category — while also adding back reimbursements, which represent real money received. This is the single most important number in the dashboard.

---

### Expected Payout
> **What Amazon should be depositing into the bank account.**

**Formula:**
```
Expected Payout = Net Sales (Orders - Fees) - Refunds Issued + Reimbursements
```

**Business Reasoning:**
This figure represents what Amazon *owes* us based on the settlement data. By comparing it against the actual bank disbursement on the Reconciliation page, we can immediately detect if Amazon has underpaid, short-deposited, or deferred any amounts — allowing us to raise support cases before money is lost. **Note:** This is strictly a cash-flow metric (what Amazon transfers to your bank). It is different from Net Income because Amazon does not deduct your COGS or Operating Expenses before paying you. Mathematically, this is equal to `Net Income + COGS + OpEx`, because Amazon does not pay your supplier or your rent before transferring your funds.

---

## 2. Efficiency & Health Metrics

### Gross Margin %
> **Product profitability before advertising and overhead are applied.**

**Formula:**
```
Gross Margin % = (Sales + Reimbursements - Refunds - COGS - FBA Fees - Selling Fees - Promotions - Other Amazon Fees) / Gross Sales * 100
```

**Variables:**
- `Sales` — Total revenue from all orders
- `Reimbursements` — Payments received from Amazon for lost or damaged inventory
- `Refunds` — Total value refunded to customers
- `COGS` — The unit purchase cost of all items sold
- `FBA Fees` — Amazon fulfilment, shipping, weight handling, and return processing fees
- `Selling Fees` — Amazon's referral commission on each sale
- `Promotions` — Total value of coupon and promotional rebates
- `Other Amazon Fees` — Miscellaneous Amazon charges

**Business Reasoning:**
This metric strips out refunds to give a net revenue figure, then measures how much of that remains after the direct cost of purchasing inventory. A Gross Margin above 30% is the target threshold. If this figure drops, it is a signal to review your supplier costs or selling price — before factoring in advertising or overhead, which are addressed separately. **Gross Margin tells you if the product itself is profitable.** (If Gross Margin is high but Net Margin is low, it means the product is good, but your ad spend or overhead is too high.) For an Amazon business, fulfilment and referral fees are unavoidable direct costs. Subtracting them gives a true picture of the physical product's profitability before Ads and Overhead.

---

### Net Margin %
> **The ultimate health check: how much of each Rupee earned is actually kept.**

**Formula:**
```
Net Margin % = (Net Income / Gross Sales) * 100
```

**Variables:**
- `Net Income` — Fully calculated bottom-line profit (see above)
- `Gross Sales` — Total revenue from all orders

**Business Reasoning:**
After every single expense, fee, and deduction, this tells us what percentage of the total revenue is retained as profit. A target of 10% or above indicates a healthy, sustainable business operation.

---

### Return Rate %
> **A direct measure of product quality and customer satisfaction.**

**Formula:**
```
Return Rate % = (Total Returns / Units Sold) * 100
```

**Variables:**
- `Total Returns` — Number of units returned by customers
- `Units Sold` — Total number of units dispatched to customers

**Business Reasoning:**
A high return rate is a strong signal of product quality issues, misleading listings, or unmet customer expectations. The dashboard alerts when this exceeds **5%**, at which point investigation and corrective action (e.g., updating images, bullet points, or product design) becomes a priority.

---

### True Profit / Sale
> **The realistic average of what every dispatched order earns the business.**

**Formula:**
```
True Profit / Sale = Net Income / Gross Units Sold
```

**Variables:**
- `Net Income` — Fully calculated bottom-line profit
- `Gross Units Sold` — Total number of units dispatched, including units that were subsequently returned

**Business Reasoning:**
By spreading the total net income (which already factors in the financial losses from returns — the refunds and return fees are already deducted in the Net Income calculation) across ALL units shipped, we get a realistic, fully-burdened average of what every dispatched order actually earns the business. This is more accurate than dividing by net units, which would artificially inflate the per-unit figure by excluding the volume of returned orders from the denominator.

---

## 3. Advertising Metrics

### ACOS (Advertising Cost of Sales)
> **The direct efficiency of your Sponsored Products campaigns.**

**Formula:**
```
ACOS = (Ad Spend / Ad-Attributed Sales) * 100
```

**Variables:**
- `Ad Spend` — The total amount of money spent on Amazon ads during the period
- `Ad-Attributed Sales` — Revenue from orders that Amazon tracked as resulting from an ad click (7-day attribution window)

**Business Reasoning:**
ACOS tells us how many Rupees we are spending in ads for every Rupee of sales *directly attributed* to those ads. A target of **under 25%** is recommended for profitable campaigns. A campaign-level ACOS above 35% is flagged as a concern and should be reviewed for keyword pruning or bid adjustments.

---

### TACOS (Total Advertising Cost of Sales)
> **Your ad spend measured against the entire business, not just ad-driven sales.**

**Formula:**
```
TACOS = (Ad Spend / Gross Sales) * 100
```

**Variables:**
- `Ad Spend` — Total money spent on Amazon ads
- `Gross Sales` — Total revenue from *all* orders, including organic (non-ad-driven) sales

**Business Reasoning:**
ACOS can look misleading in isolation. For example, a high ACOS might be *acceptable* if the majority of your sales are organic (customers finding your product naturally). TACOS corrects for this by measuring ad investment against the total business. A TACOS **under 15%** indicates a healthy advertising strategy. If TACOS climbs, it means the business is becoming overly dependent on paid traffic.

---

### ROAS (Return on Ad Spend)
> **How many Rupees your ads generate for every Rupee invested.**

**Formula:**
```
ROAS = Ad-Attributed Sales / Ad Spend
```

**Variables:**
- `Ad-Attributed Sales` — Revenue traced to ad clicks
- `Ad Spend` — Total ad investment

**Business Reasoning:**
ROAS is the inverse of ACOS and is the easiest metric to communicate value. A ROAS of **3x or above** is the minimum healthy threshold — meaning for every ₹1 spent, ₹3 or more is returned in sales. A ROAS below 1.5x means ads are costing more than they are generating in attributed revenue and requires immediate strategic review.

---

## 4. SKU-Level Economics

### Allocated OpEx
> **Each SKU's fair share of the business's overhead costs.**

**Formula:**
```
Allocated OpEx (per SKU) = (SKU Sales / Total Sales) * Total Operating Expenses
```

**Variables:**
- `SKU Sales` — Total revenue attributed to the specific product in the period
- `Total Sales` — Combined revenue across all active SKUs
- `Total Operating Expenses` — Sum of all overhead costs (salaries, software, rent, etc.)

**Business Reasoning:**
Operating expenses such as salaries, software tools, and rent cannot be directly assigned to a single product. Rather than guessing, we use a proportional revenue-based allocation. A SKU that contributes 40% of total sales is logically responsible for 40% of the business's overheads. This creates a fair, defensible, and consistent method for measuring true product-level economics.

---

### True Net Profit (Blended Profit)
> **How much a specific SKU genuinely contributes to the company's bottom line.**

**Formula:**
```
True Net Profit (per SKU) = SKU Net Profit - Allocated OpEx
```

**Variables:**
- `SKU Net Profit` — The product's revenue minus its direct costs (COGS, FBA fees, selling fees, ads, and refunds)
- `Allocated OpEx` — The SKU's proportional share of business overheads (see above)

**Business Reasoning:**
A SKU might appear highly profitable when looking only at its direct costs. However, if its revenue is sustaining a large portion of business overheads, the *true* picture may be very different. By applying the Allocated OpEx deduction, we get an honest answer to **"If this SKU did not exist, what overhead cost would disappear?"** If a SKU's True Net Profit is negative for two consecutive months, it is a signal to reprice, reposition, or discontinue the product.

---

*Document maintained by Kareena Financial Dashboard. For questions on the methodology, contact your account consultant.*
