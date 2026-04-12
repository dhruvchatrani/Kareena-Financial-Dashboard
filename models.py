from sqlalchemy import Column, Integer, String, Float, Date, Boolean, DateTime, UniqueConstraint
from database import Base
import datetime

class Inventory(Base):
    """3-Tier Inventory Tracking"""
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    product_name = Column(String, nullable=True)
    local_stock = Column(Integer, default=0)
    fbm_stock = Column(Integer, default=0)
    fba_stock = Column(Integer, default=0)
    lead_time_days = Column(Integer, default=7)
    is_manufactured = Column(Boolean, default=False)

class COGS(Base):
    """Version-Controlled Cost of Goods Sold"""
    __tablename__ = "cogs_history"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, index=True, nullable=False)
    unit_cost = Column(Float, nullable=False)
    effective_start_date = Column(Date, nullable=False, default=datetime.date.today)
    effective_end_date = Column(Date, nullable=True)
    gst_inclusive = Column(Boolean, default=True)

class OperatingExpense(Base):
    """Global Business Expenses"""
    __tablename__ = "operating_expenses"

    id = Column(Integer, primary_key=True, index=True)
    date_incurred = Column(Date, nullable=False, default=datetime.date.today)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)

class FinancialEvent(Base):
    """Amazon Transactional Data"""
    __tablename__ = "financial_events"

    id = Column(Integer, primary_key=True, index=True)
    amazon_order_id = Column(String, index=True, nullable=False)
    posted_date = Column(Date, nullable=False)
    sku = Column(String, index=True)
    type = Column(String)  # 'Order','Refund','Reimbursement','Transfer','ShippingService','Other'
    description = Column(String, nullable=True)
    quantity = Column(Integer, default=1)
    product_sales = Column(Float, default=0.0)
    fba_fees = Column(Float, default=0.0)
    selling_fees = Column(Float, default=0.0)
    refunds = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    promotional_rebates = Column(Float, default=0.0)
    is_deferred = Column(Boolean, default=False)

class SyncLog(Base):
    """Log of Data Syncs"""
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    status = Column(String)
    details = Column(String)

class AdsMetric(Base):
    """Per-row Sponsored Products search term report data"""
    __tablename__ = "ads_metrics"

    id = Column(Integer, primary_key=True, index=True)
    report_month = Column(Date, nullable=False, index=True)
    date = Column(Date, nullable=False)
    campaign_name = Column(String, nullable=True)
    search_term = Column(String, nullable=True)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)
    spend = Column(Float, default=0.0)
    sales_7d = Column(Float, default=0.0)
    acos = Column(Float, default=0.0)
    roas = Column(Float, default=0.0)
    orders_7d = Column(Integer, default=0)
    units_7d = Column(Integer, default=0)
    cvr = Column(Float, default=0.0)
    sku = Column(String, nullable=True)
    brand = Column(String, nullable=True)

class BusinessMetric(Base):
    """Per-SKU Business Report data"""
    __tablename__ = "business_metrics"

    id = Column(Integer, primary_key=True, index=True)
    report_month = Column(Date, nullable=False, index=True)
    sku = Column(String, index=True)
    asin = Column(String, nullable=True)
    title = Column(String, nullable=True)
    sessions = Column(Integer, default=0)
    page_views = Column(Integer, default=0)
    units_ordered = Column(Integer, default=0)
    unit_session_pct = Column(Float, default=0.0)
    ordered_product_sales = Column(Float, default=0.0)

class IQOLog(Base):
    """Innovate-Quantify-Orchestrate weekly business development log"""
    __tablename__ = "iqo_log"

    id = Column(Integer, primary_key=True, index=True)
    week_start = Column(Date, nullable=False)
    stage = Column(String, nullable=False)  # 'Innovate','Quantify','Orchestrate'
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    metric_before = Column(Float, nullable=True)
    metric_after = Column(Float, nullable=True)
    metric_label = Column(String, nullable=True)
    target_sku = Column(String, nullable=True)
    outcome = Column(String, nullable=True)  # 'Positive','Neutral','Negative'
    orchestrated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now)

class KanbanCard(Base):
    """Kanban board cards"""
    __tablename__ = "kanban_cards"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    column_name = Column(String, nullable=False, default='To Do')  # 'To Do','In Progress','Review','Done'
    assignee = Column(String, nullable=True)
    due_date = Column(Date, nullable=True)
    priority = Column(String, default='Medium')  # 'Low','Medium','High'
    position = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.now)

class Promotion(Base):
    """Coupons, deals, and promotions tracker"""
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    promo_type = Column(String, nullable=False)  # 'Coupon','Deal','Lightning Deal','Promotion'
    sku = Column(String, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    discount_pct = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)
    total_cost = Column(Float, default=0.0)
    units_sold = Column(Integer, default=0)
    revenue_generated = Column(Float, default=0.0)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
