# Kareena Dashboard: Manual Document Processor User Guide

This guide is the definitive instruction sheet for managing the manual data processing engine. It is designed for Kareena and future finance hires to ensure 100% accuracy in financial reporting.

---

## 1. The "Select-All" Upload Workflow
The system features an automated **File Sniffing** engine. You NO LONGER need to rename files before uploading.

**Instructions:**
1. Download your reports from Amazon Seller Central (Settlement, Deferred, Business, Ads, Returns).
2. Go to the **Upload Data** section in the Dashboard.
3. Select ALL the relevant files at once (or drag and drop them).
4. The system will automatically scan the internal headers (e.g., searching for `settlement id` or `Sessions - Total`) to identify and map the data correctly.

---

## 2. The Accrual Bridge (Settled vs. Deferred)
Amazon often holds funds for orders that haven't been delivered yet (Deferred Transactions). Our system uses an **Accrual Bridge** to ensure your profit numbers reflect the actual work done this month.

- **How it works:** The system combines your standard **Settlement Report** with the **Deferred Transactions** report.
- **Why this matters:** It prevents "invisible" revenue. Your dashboard will show sales as they happen, not just when Amazon finally pays them out, giving you a real-time view of your business health.

---

## 3. Health Check Legend
The AI Auditor uses your custom settings to flag the health of your store.

- **✅ Healthy (On-Track):** All metrics (Conversion, TACOS, Returns) are within your defined goal ranges.
- **⚠️ Warning (Broken):** One or more metrics have crossed your safety limits.
  - **CONV_LOW:** Your conversion rate is below your target (e.g., < 10%).
  - **TACOS_HIGH:** Your ad spend is eating too much of your total revenue (e.g., > 15%).
  - **REFUND_HIGH:** Returns are higher than your acceptable limit (e.g., > 5%).
- **🚫 Data Gap Detected:** You uploaded an incomplete set of files (e.g., forgot the Ads report). Results are calculated based only on available data.

---

## 4. Actionable Insights
At the top of every report, you will find the **AI Auditor Summary**.

- **What to look for:** A concise 2-sentence breakdown of your month.
- **The "Single Step":** If a rule is violated, the AI will suggest exactly ONE operational priority (e.g., "Check listing images for SKU-X" or "Lower bids on high-TACOS campaigns").
- **Tip:** Do not ignore the "Red Flags" section at the bottom of the audit card; these are specific data-driven warnings.

---

## 5. PDF Archiving & Record Keeping
To ensure you have a permanent record of every audit:

1. After uploading and viewing the report, click the **"Download PDF report"** button.
2. The system is optimized for printing; it will automatically hide dashboard buttons and format the data into a clean, professional document.
3. Save this PDF in your monthly finance folder for long-term tracking and tax preparation.

---

**Support Note:** If the system returns an error during upload, ensure you are uploading the raw CSV/XML files directly as downloaded from Amazon.
