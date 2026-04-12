import pandas as pd
import datetime
import calendar
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
import models


def clean_numeric(val):
    if pd.isna(val) or val == '':
        return 0.0
    val_str = str(val).replace('₹', '').replace(',', '').strip()
    if val_str.startswith('(') and val_str.endswith(')'):
        val_str = '-' + val_str[1:-1]
    try:
        return float(val_str)
    except ValueError:
        return 0.0


def calculate_monthly_summary(db: Session, start_date=None, end_date=None) -> Dict[str, float]:
    summary = {
        'Sales': 0.0, 'Refunds': 0.0, 'FBA_Fees': 0.0, 'Selling_Fees': 0.0,
        'Reimbursements': 0.0, 'Ads_Cost': 0.0, 'COGS': 0.0, 'OpEx': 0.0,
        'Net_Income': 0.0, 'Owed_Deferred': 0.0, 'Other_Amazon_Fees': 0.0,
        'Disbursements': 0.0, 'Units_Sold': 0, 'Promotions': 0.0,
        'Sessions': 0, 'Page_Views': 0, 'Unit_Session_Pct': 0.0,
        'Total_Returns': 0, 'Return_Pct': 0.0,
        'ACOS': 0.0, 'TACOS': 0.0,
        'Gross_Margin_Pct': 0.0, 'Net_Margin_Pct': 0.0,
        'Revenue_Per_Unit': 0.0, 'Profit_Per_Unit': 0.0,
        'ROI': 0.0,
    }

    # 1. Financial events
    query = db.query(models.FinancialEvent)
    if start_date and end_date:
        query = query.filter(
            models.FinancialEvent.posted_date >= start_date,
            models.FinancialEvent.posted_date <= end_date
        )
    events = query.all()

    for e in events:
        if e.is_deferred:
            summary['Owed_Deferred'] += e.total_amount
            continue

        if e.type == 'Order':
            summary['Sales'] += e.product_sales
            summary['FBA_Fees'] += abs(e.fba_fees)
            summary['Selling_Fees'] += abs(e.selling_fees)
            summary['Units_Sold'] += e.quantity or 0
            # Other fees = what Amazon took beyond known fees
            calc_net = e.product_sales - abs(e.fba_fees) - abs(e.selling_fees)
            other_tx = calc_net - e.total_amount
            summary['Other_Amazon_Fees'] += other_tx
            summary['Promotions'] += abs(e.promotional_rebates)

        elif e.type == 'Refund':
            summary['Refunds'] += abs(e.total_amount)
            summary['Total_Returns'] += 1

        elif e.type == 'Reimbursement':
            summary['Reimbursements'] += abs(e.total_amount)

        elif e.type == 'Transfer':
            if e.total_amount < 0:
                summary['Disbursements'] += abs(e.total_amount)

        elif e.type == 'Other':
            summary['Other_Amazon_Fees'] -= e.total_amount

    # 2. COGS
    active_cogs = db.query(models.COGS).filter(models.COGS.effective_end_date == None).all()
    cogs_map = {c.sku.strip(): c.unit_cost for c in active_cogs}
    for e in events:
        if e.type == 'Order' and e.sku and e.sku in cogs_map:
            summary['COGS'] += cogs_map[e.sku] * (e.quantity or 0)

    # 3. OpEx + Ads
    opex_query = db.query(models.OperatingExpense)
    if start_date and end_date:
        opex_query = opex_query.filter(
            models.OperatingExpense.date_incurred >= start_date,
            models.OperatingExpense.date_incurred <= end_date
        )
    for expense in opex_query.all():
        if expense.category == 'Amazon Ads':
            summary['Ads_Cost'] += expense.amount
        else:
            summary['OpEx'] += expense.amount

    # 4. Business metrics (sessions/conversion)
    biz_query = db.query(models.BusinessMetric)
    if start_date and end_date:
        biz_query = biz_query.filter(
            models.BusinessMetric.report_month >= start_date,
            models.BusinessMetric.report_month <= end_date
        )
    biz_rows = biz_query.all()
    if biz_rows:
        summary['Sessions'] = sum(b.sessions for b in biz_rows)
        summary['Page_Views'] = sum(b.page_views for b in biz_rows)
        total_units_biz = sum(b.units_ordered for b in biz_rows)
        if summary['Sessions'] > 0:
            summary['Unit_Session_Pct'] = round(total_units_biz / summary['Sessions'] * 100, 2)

    # 5. Derived metrics
    # Return rate
    if summary['Units_Sold'] > 0:
        summary['Return_Pct'] = round(summary['Total_Returns'] / summary['Units_Sold'] * 100, 2)

    # ACOS = Ads / Ad-attributed Sales (from AdsMetric table)
    ads_query = db.query(models.AdsMetric)
    if start_date and end_date:
        ads_query = ads_query.filter(
            models.AdsMetric.date >= start_date,
            models.AdsMetric.date <= end_date
        )
    ad_attributed_sales = sum(r.sales_7d for r in ads_query.all())
    if ad_attributed_sales > 0:
        summary['ACOS'] = round(summary['Ads_Cost'] / ad_attributed_sales * 100, 2)

    # TACOS = Total Ad Spend / Total Revenue (Sales only, not reimbursements)
    if summary['Sales'] > 0:
        summary['TACOS'] = round(summary['Ads_Cost'] / summary['Sales'] * 100, 2)

    # Net Income: (Revenue) - (Costs)
    summary['Net_Income'] = (
        summary['Sales'] + summary['Reimbursements']
    ) - (
        summary['Refunds'] + summary['FBA_Fees'] + summary['Selling_Fees'] +
        summary['Ads_Cost'] + summary['COGS'] + summary['OpEx'] +
        summary['Other_Amazon_Fees'] + summary['Promotions']
    )

    # Margins
    if summary['Sales'] > 0:
        gross_profit = (
            summary['Sales'] + summary['Reimbursements']
            - summary['Refunds']
            - summary['COGS']
            - summary['FBA_Fees']
            - summary['Selling_Fees']
            - summary['Promotions']
            - summary['Other_Amazon_Fees']
        )
        summary['Gross_Margin_Pct'] = round(gross_profit / summary['Sales'] * 100, 2)
        summary['Net_Margin_Pct'] = round(summary['Net_Income'] / summary['Sales'] * 100, 2)
        summary['Revenue_Per_Unit'] = round(summary['Sales'] / summary['Units_Sold'], 2) if summary['Units_Sold'] > 0 else 0.0

    if summary['Units_Sold'] > 0:
        summary['Profit_Per_Sale'] = round(summary['Net_Income'] / summary['Units_Sold'], 2)
    else:
        summary['Profit_Per_Sale'] = 0.0

    # ROI = Net Income / COGS (return on inventory investment)
    if summary['COGS'] > 0:
        summary['ROI'] = round(summary['Net_Income'] / summary['COGS'] * 100, 2)

    return summary


def calculate_sku_metrics(db: Session, start_date=None, end_date=None) -> pd.DataFrame:
    query = db.query(models.FinancialEvent)
    if start_date and end_date:
        query = query.filter(
            models.FinancialEvent.posted_date >= start_date,
            models.FinancialEvent.posted_date <= end_date
        )
    events = query.all()
    if not events:
        return pd.DataFrame()

    df_rows = []
    for e in events:
        if e.is_deferred:
            continue
        # Fix: only compute other_tx_fees for Order type
        other_tx_fees = 0.0
        if e.type == 'Order':
            calc_net = e.product_sales - abs(e.fba_fees) - abs(e.selling_fees)
            other_tx_fees = calc_net - e.total_amount
        # Do NOT add Other type fees here — they are non-SKU level

        df_rows.append({
            'Sku': e.sku,
            'Product Sales': e.product_sales if e.type == 'Order' else 0.0,
            'FBA Fees': abs(e.fba_fees) if e.type == 'Order' else 0.0,
            'Selling Fees': abs(e.selling_fees) if e.type == 'Order' else 0.0,
            'Refunds': abs(e.total_amount) if e.type == 'Refund' else 0.0,
            'Reimbursements': abs(e.total_amount) if e.type == 'Reimbursement' else 0.0,
            'Other Amazon Fees': other_tx_fees,
            'Units Ordered': e.quantity if e.type == 'Order' else 0,
            'Returns Count': 1 if e.type == 'Refund' else 0,
            'Promotions': abs(e.promotional_rebates) if e.type == 'Order' else 0.0
        })

    df = pd.DataFrame(df_rows)
    if df.empty:
        return pd.DataFrame()

    sku_stats = df.groupby('Sku').agg({
        'Product Sales': 'sum', 'FBA Fees': 'sum', 'Selling Fees': 'sum',
        'Refunds': 'sum', 'Reimbursements': 'sum',
        'Other Amazon Fees': 'sum', 'Units Ordered': 'sum', 'Promotions': 'sum',
        'Returns Count': 'sum'
    }).reset_index()

    sku_stats = sku_stats[~sku_stats['Sku'].isin(['SERVICE_FEE', 'UNKNOWN', 'nan'])]

    active_cogs = db.query(models.COGS).filter(models.COGS.effective_end_date == None).all()
    cogs_map = {c.sku.strip(): c.unit_cost for c in active_cogs}

    sku_stats['Unit_COGS'] = sku_stats['Sku'].map(cogs_map).fillna(0)
    sku_stats['Total COGS'] = sku_stats['Unit_COGS'] * sku_stats['Units Ordered']

    sku_stats['Net Profit'] = (
        sku_stats['Product Sales'] + sku_stats['Reimbursements']
    ) - (
        sku_stats['FBA Fees'] + sku_stats['Selling Fees'] +
        sku_stats['Refunds'] + sku_stats['Other Amazon Fees'] + 
        sku_stats['Total COGS'] + sku_stats['Promotions']
    )

    # Profit per sale (Gross Units Sold — returns already burdened into Net Income)
    sku_stats['Profit_Per_Sale'] = sku_stats.apply(
        lambda r: round(r['Net Profit'] / r['Units Ordered'], 2) if r['Units Ordered'] > 0 else 0.0, axis=1
    )

    # Margin %
    sku_stats['Margin_Pct'] = sku_stats.apply(
        lambda r: round(r['Net Profit'] / r['Product Sales'] * 100, 2) if r['Product Sales'] > 0 else 0.0, axis=1
    )

    # ROI
    sku_stats['ROI_Pct'] = sku_stats.apply(
        lambda r: round(r['Net Profit'] / r['Total COGS'] * 100, 2) if r['Total COGS'] > 0 else 0.0, axis=1
    )

    # OpEx allocation
    opex_query = db.query(models.OperatingExpense)
    if start_date and end_date:
        opex_query = opex_query.filter(
            models.OperatingExpense.date_incurred >= start_date,
            models.OperatingExpense.date_incurred <= end_date
        )
    total_opex = sum(
        e.amount for e in opex_query.all() if e.category != 'Amazon Ads'
    )

    total_sales = sku_stats['Product Sales'].sum()
    if total_sales > 0:
        sku_stats['Allocated_OpEx'] = (sku_stats['Product Sales'] / total_sales) * total_opex
    else:
        sku_stats['Allocated_OpEx'] = 0.0

    sku_stats['Blended_Net_Profit'] = sku_stats['Net Profit'] - sku_stats['Allocated_OpEx']
    sku_stats['Blended_Profit_Per_Sale'] = sku_stats.apply(
        lambda r: round(r['Blended_Net_Profit'] / r['Units Ordered'], 2) if r['Units Ordered'] > 0 else 0.0, axis=1
    )

    # Cashflow health: blended profit per unit >= COGS per unit?
    sku_stats['Cashflow_Healthy'] = sku_stats['Blended_Profit_Per_Unit'] >= sku_stats['Unit_COGS']

    return sku_stats


def get_period_summary(db: Session, start_date, end_date) -> Dict:
    """Wrapper to get summary for any period — used for comparisons."""
    return calculate_monthly_summary(db, start_date, end_date)


def get_comparison_data(db: Session, current_start, current_end) -> Dict:
    """
    Returns current period + MoM + YoY comparison summaries.
    """
    current = calculate_monthly_summary(db, current_start, current_end)

    # MoM: same duration, shifted back by number of days
    delta = (current_end - current_start).days + 1
    mom_end = current_start - datetime.timedelta(days=1)
    mom_start = mom_end - datetime.timedelta(days=delta - 1)
    mom = calculate_monthly_summary(db, mom_start, mom_end)

    # YoY: same date range, one year ago (leap-year safe)
    def _safe_date_prev_year(d):
        try:
            return datetime.date(d.year - 1, d.month, d.day)
        except ValueError:
            last_day = calendar.monthrange(d.year - 1, d.month)[1]
            return datetime.date(d.year - 1, d.month, last_day)
    yoy_start = _safe_date_prev_year(current_start)
    yoy_end = _safe_date_prev_year(current_end)
    yoy = calculate_monthly_summary(db, yoy_start, yoy_end)

    def pct_change(current_val, prev_val):
        if prev_val == 0:
            return None
        return round((current_val - prev_val) / abs(prev_val) * 100, 1)

    key_metrics = ['Sales', 'Net_Income', 'COGS', 'Ads_Cost', 'Refunds', 'Units_Sold', 'TACOS', 'Return_Pct']

    comparison = {}
    for k in key_metrics:
        comparison[k] = {
            'current': current.get(k, 0),
            'mom': mom.get(k, 0),
            'yoy': yoy.get(k, 0),
            'mom_pct': pct_change(current.get(k, 0), mom.get(k, 0)),
            'yoy_pct': pct_change(current.get(k, 0), yoy.get(k, 0)),
        }

    return {
        'current': current,
        'mom': mom,
        'yoy': yoy,
        'comparison': comparison,
        'periods': {
            'current': {'start': str(current_start), 'end': str(current_end)},
            'mom': {'start': str(mom_start), 'end': str(mom_end)},
            'yoy': {'start': str(yoy_start), 'end': str(yoy_end)},
        }
    }


def get_ads_summary(db: Session, start_date=None, end_date=None, sku_filter=None, brand_filter=None) -> Dict:
    """Aggregate ads metrics for advertising dashboard."""
    query = db.query(models.AdsMetric)
    if start_date and end_date:
        query = query.filter(
            models.AdsMetric.date >= start_date,
            models.AdsMetric.date <= end_date
        )
    if sku_filter:
        query = query.filter(models.AdsMetric.sku.ilike(f"%{sku_filter}%"))
    if brand_filter:
        query = query.filter(models.AdsMetric.brand.ilike(f"%{brand_filter}%"))
        
    rows = query.all()
    if not rows:
        return {}

    total_impressions = sum(r.impressions for r in rows)
    total_clicks = sum(r.clicks for r in rows)
    total_spend = sum(r.spend for r in rows)
    total_sales = sum(r.sales_7d for r in rows)
    total_orders = sum(r.orders_7d for r in rows)
    total_units = sum(r.units_7d for r in rows)

    acos = round(total_spend / total_sales * 100, 2) if total_sales > 0 else 0.0
    ctr = round(total_clicks / total_impressions * 100, 2) if total_impressions > 0 else 0.0
    cvr = round(total_orders / total_clicks * 100, 2) if total_clicks > 0 else 0.0
    cpc = round(total_spend / total_clicks, 2) if total_clicks > 0 else 0.0
    roas = round(total_sales / total_spend, 2) if total_spend > 0 else 0.0

    # Daily trend
    daily = {}
    for r in rows:
        d = str(r.date)
        if d not in daily:
            daily[d] = {'date': d, 'spend': 0.0, 'sales': 0.0, 'impressions': 0, 'clicks': 0, 'orders': 0}
        daily[d]['spend'] += r.spend
        daily[d]['sales'] += r.sales_7d
        daily[d]['impressions'] += r.impressions
        daily[d]['clicks'] += r.clicks
        daily[d]['orders'] += r.orders_7d
    daily_trend = sorted(daily.values(), key=lambda x: x['date'])

    # Top search terms by spend
    term_map = {}
    for r in rows:
        t = r.search_term or 'Unknown'
        if t not in term_map:
            term_map[t] = {'term': t, 'spend': 0.0, 'sales': 0.0, 'impressions': 0, 'clicks': 0, 'orders': 0}
        term_map[t]['spend'] += r.spend
        term_map[t]['sales'] += r.sales_7d
        term_map[t]['impressions'] += r.impressions
        term_map[t]['clicks'] += r.clicks
        term_map[t]['orders'] += r.orders_7d

    for t in term_map.values():
        t['acos'] = round(t['spend'] / t['sales'] * 100, 2) if t['sales'] > 0 else 0.0
        t['cvr'] = round(t['orders'] / t['clicks'] * 100, 2) if t['clicks'] > 0 else 0.0

    top_terms = sorted(term_map.values(), key=lambda x: x['cvr'], reverse=True)[:20]

    return {
        'total_impressions': total_impressions,
        'total_clicks': total_clicks,
        'total_spend': round(total_spend, 2),
        'total_sales': round(total_sales, 2),
        'total_orders': total_orders,
        'total_units': total_units,
        'acos': acos,
        'ctr': ctr,
        'cvr': cvr,
        'cpc': cpc,
        'roas': roas,
        'daily_trend': daily_trend,
        'top_terms': top_terms,
    }


def get_disbursements(db: Session, start_date=None, end_date=None) -> List[Dict]:
    """Get all Transfer (disbursement) events for the period."""
    query = db.query(models.FinancialEvent).filter(
        models.FinancialEvent.type == 'Transfer'
    )
    if start_date and end_date:
        query = query.filter(
            models.FinancialEvent.posted_date >= start_date,
            models.FinancialEvent.posted_date <= end_date
        )
    rows = query.order_by(models.FinancialEvent.posted_date).all()
    return [
        {
            'date': str(r.posted_date),
            'amount': abs(r.total_amount),
            'description': r.description or ''
        }
        for r in rows
    ]


def get_reconciliation_check(db: Session, start_date=None, end_date=None) -> Dict:
    """
    Check: Does Amazon owe me money?
    - Count refund events that have no matching reimbursement
    - Sum deferred amounts still pending
    - Check disbursements vs net expected payout
    """
    query = db.query(models.FinancialEvent)
    if start_date and end_date:
        query = query.filter(
            models.FinancialEvent.posted_date >= start_date,
            models.FinancialEvent.posted_date <= end_date
        )
    events = query.all()

    total_sales_net = sum(e.total_amount for e in events if e.type == 'Order' and not e.is_deferred)
    total_refunds = sum(abs(e.total_amount) for e in events if e.type == 'Refund')
    total_reimbursements = sum(abs(e.total_amount) for e in events if e.type == 'Reimbursement')
    total_disbursed = sum(abs(e.total_amount) for e in events if e.type == 'Transfer')
    total_deferred = sum(e.total_amount for e in events if e.is_deferred)
    other_fees = sum(abs(e.total_amount) for e in events if e.type in ('ShippingService', 'Other'))

    expected_payout = total_sales_net - total_refunds + total_reimbursements - other_fees
    discrepancy = expected_payout - total_disbursed

    # Simplified "Amazon Owes Me" logic
    # We want to know if the money paid to bank matches (Sales - Fees - Refunds + Reimbursements)
    
    # Order IDs that were refunded — check if reimbursed
    refunded_orders = {e.amazon_order_id for e in events if e.type == 'Refund'}
    reimbursed_orders = {e.amazon_order_id for e in events if e.type == 'Reimbursement'}
    potentially_unreimbursed = refunded_orders - reimbursed_orders

    return {
        'total_sales_net': round(total_sales_net, 2),
        'total_refunds': round(total_refunds, 2),
        'total_reimbursements': round(total_reimbursements, 2),
        'total_disbursed': round(total_disbursed, 2),
        'total_deferred': round(total_deferred, 2),
        'expected_payout': round(expected_payout, 2),
        'discrepancy': round(discrepancy, 2),
        'potentially_unreimbursed_count': len(potentially_unreimbursed),
        'potentially_unreimbursed_orders': list(potentially_unreimbursed)[:20],
        'status': 'OK' if abs(discrepancy) < 100 else 'CHECK_REQUIRED',
    }


def get_disbursement_deep_dive(db: Session, start_date=None, end_date=None) -> List[Dict]:
    """Granular data on disbursements (Amazon Payouts)."""
    # Fetch all Transfer events
    transfers = db.query(models.FinancialEvent).filter(
        models.FinancialEvent.type == 'Transfer'
    )
    if start_date and end_date:
        transfers = transfers.filter(
            models.FinancialEvent.posted_date >= start_date,
            models.FinancialEvent.posted_date <= end_date
        )
    transfers = transfers.order_by(models.FinancialEvent.posted_date.desc()).all()

    deep_dive = []
    for t in transfers:
        # For each transfer, we try to find the "window" of events it covers.
        # This is a heuristic: events posted on or before the transfer date, 
        # but after the previous transfer date.
        
        prev_t = db.query(models.FinancialEvent).filter(
            models.FinancialEvent.type == 'Transfer',
            models.FinancialEvent.posted_date < t.posted_date
        ).order_by(models.FinancialEvent.posted_date.desc()).first()
        
        start_win = prev_t.posted_date if prev_t else datetime.date(2000, 1, 1)
        end_win = t.posted_date
        
        # Get all non-transfer events in this window
        window_events = db.query(models.FinancialEvent).filter(
            models.FinancialEvent.posted_date > start_win,
            models.FinancialEvent.posted_date <= end_win,
            models.FinancialEvent.type != 'Transfer'
        ).all()
        
        gross_sales = sum(e.product_sales for e in window_events if e.type == 'Order')
        fees = sum(abs(e.fba_fees) + abs(e.selling_fees) for e in window_events)
        refunds = sum(abs(e.total_amount) for e in window_events if e.type == 'Refund')
        reimb = sum(abs(e.total_amount) for e in window_events if e.type == 'Reimbursement')
        promos = sum(abs(e.promotional_rebates) for e in window_events)
        
        deep_dive.append({
            'settlement_id': t.amazon_order_id,
            'date': str(t.posted_date),
            'amount': abs(t.total_amount),
            'gross_sales': round(gross_sales, 2),
            'fees': round(fees, 2),
            'refunds': round(refunds, 2),
            'reimbursements': round(reimb, 2),
            'promotions': round(promos, 2),
            'net_calculated': round(gross_sales - fees - refunds + reimb - promos, 2)
        })
        
    return deep_dive
