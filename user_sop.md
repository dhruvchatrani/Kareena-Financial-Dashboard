# Monthly Dashboard SOP
Step-by-step guide for monthly financial review. Follow in order.

### 1. Upload Monthly Reports
- Go to [Monthly Audit → Upload](/audit)
- Select the correct month
- Upload: Settlement CSV (required), Deferred Transactions CSV, Business Report CSV, Ads Report XLSX, Returns XML
- Click Upload & Sync — you will be redirected to the dashboard filtered to that month

### 2. Review Key Metrics on Dashboard
- Check **Net Income** — is it positive? Is it growing MoM?
- Check **Gross Margin %** — should be above 30%
- Check **Net Margin %** — should be above 10%
- Check **Return Rate** — alert if above 5%
- Check **TACOS** — alert if above 15%
- Check **ROI** — should be positive

### 3. Review Period Comparisons
- Is Sales MoM growing? Target: positive trend
- Is Net Income MoM growing? If declining, investigate which cost line increased
- Check YoY — are we ahead of last year same month?
- If TACOS is up YoY, review ad strategy

### 4. Review Advertising Dashboard
- Go to [Advertising](/advertising)
- Check ACOS — should be below 25% for profitable campaigns
- Check ROAS — should be above 3x
- Review top search terms — pause any term with spend but 0 orders
- Identify top converting terms — consider increasing bid

### 5. Run Reconciliation Check
- Go to [Reconciliation](/reconciliation)
- Check discrepancy — should be under ₹100
- If "Check Required": download the Monthly Summary PDF from Amazon and compare Net Proceeds to Amazon-comparable figure shown
- Review any unreimbursed refunded orders — raise a case with Amazon Seller Support if found
- Note deferred amount — this will arrive next month

### 6. Review SKU Insights
- Go to [SKU Insights](/sku-insights)
- Check **Blended Net Profit** per SKU — is it positive?
- Check **Cashflow Healthy** column — if red, that SKU is not covering its own COGS
- Check **Profit Per Unit** — should be above ₹200 (configurable in Settings)
- If any SKU has negative blended profit for 2 consecutive months, consider repricing or discontinuing

### 7. Update IQO Log
- Go to [IQO Log](/iqo)
- For any active "Innovate" entry from last week: add metric_after value and mark outcome
- If outcome is Positive: click "Orchestrate" to bake it into the system
- Log ONE new Innovate entry for this week — one change only
- Examples: change main image, update bullet points, adjust price, test new keyword bid

### 8. Update Accountability Board
- Go to [Board](/board)
- Move completed tasks to Done
- Move in-progress items forward
- Add any new action items identified from the above review steps
- Assign due dates and owners

---
### 🔔 Alert Thresholds (configurable in Admin → Settings)
- **Conversion Rate:** Target ≥ 12%
- **TACOS:** Max 15%
- **Return Rate:** Max 5%
- **Min Profit/Unit:** ₹200
