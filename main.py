from fastapi import FastAPI, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
import datetime
import calendar
import pandas as pd
import data_processor as dp
from database import engine, get_db
import models
import logging
import shutil
from dotenv import load_dotenv
import processor
import auditor
import json
from pydantic import BaseModel
from typing import Optional
import markdown

load_dotenv()

class SettingsUpdate(BaseModel):
    target_unit_session_pct: float
    max_tacos_pct: float
    max_return_pct: float
    min_net_profit_per_unit: float

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kareena Fin Dashboard")

os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
templates.env.globals.update(datetime=datetime)

logging.basicConfig(level=logging.INFO)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_dates(start_date, end_date):
    if not start_date or not end_date:
        today = datetime.date.today()
        start_date = (today - datetime.timedelta(days=179)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    parsed_start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    parsed_end   = datetime.datetime.strptime(end_date,   "%Y-%m-%d").date()
    return start_date, end_date, parsed_start, parsed_end


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    start_date, end_date, parsed_start, parsed_end = _parse_dates(start_date, end_date)

    summary = dp.calculate_monthly_summary(db, parsed_start, parsed_end)
    comparison = dp.get_comparison_data(db, parsed_start, parsed_end)
    disbursements = dp.get_disbursements(db, parsed_start, parsed_end)

    # Daily time-series
    daily_data = []
    events = db.query(models.FinancialEvent).filter(
        models.FinancialEvent.posted_date >= parsed_start,
        models.FinancialEvent.posted_date <= parsed_end,
        models.FinancialEvent.is_deferred == False
    ).all()

    if events:
        df = pd.DataFrame([{
            "day": e.posted_date.strftime('%Y-%m-%d'),
            "sales": e.product_sales if e.type == 'Order' else 0.0,
            "net_profit": e.total_amount if e.type == 'Order' else 0.0
        } for e in events])
        daily_stats = df.groupby('day').agg({'sales': 'sum', 'net_profit': 'sum'}).reset_index()
        daily_data = daily_stats.to_dict(orient='records')

    return templates.TemplateResponse("index.html", {
        "request": request,
        "summary": summary,
        "comparison": comparison,
        "daily_data": daily_data,
        "disbursements": disbursements,
        "start_date": start_date,
        "end_date": end_date,
    })


# ── SKU Insights ──────────────────────────────────────────────────────────────

@app.get("/sku-insights", response_class=HTMLResponse)
async def sku_insights(request: Request, start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    start_date, end_date, parsed_start, parsed_end = _parse_dates(start_date, end_date)
    sku_df = dp.calculate_sku_metrics(db, parsed_start, parsed_end)
    sku_metrics = sku_df.to_dict(orient='records') if not sku_df.empty else []

    # Business metrics per SKU for unit session %
    biz = db.query(models.BusinessMetric).filter(
        models.BusinessMetric.report_month >= parsed_start,
        models.BusinessMetric.report_month <= parsed_end
    ).all()
    biz_map = {b.sku: {'sessions': b.sessions, 'unit_session_pct': b.unit_session_pct} for b in biz}

    for row in sku_metrics:
        b = biz_map.get(row['Sku'], {})
        row['Sessions'] = b.get('sessions', 0)
        row['Unit_Session_Pct'] = b.get('unit_session_pct', 0.0)

    return templates.TemplateResponse("sku_insights.html", {
        "request": request,
        "sku_metrics": sku_metrics,
        "start_date": start_date,
        "end_date": end_date,
    })


# ── Advertising Dashboard ─────────────────────────────────────────────────────

@app.get("/advertising", response_class=HTMLResponse)
async def advertising(request: Request, start_date: str = None, end_date: str = None, sku: str = None, brand: str = None, db: Session = Depends(get_db)):
    start_date, end_date, parsed_start, parsed_end = _parse_dates(start_date, end_date)
    ads = dp.get_ads_summary(db, parsed_start, parsed_end, sku_filter=sku, brand_filter=brand)
    return templates.TemplateResponse("advertising.html", {
        "request": request,
        "ads": ads,
        "start_date": start_date,
        "end_date": end_date,
        "sku": sku,
        "brand": brand,
    })


# ── Reconciliation ────────────────────────────────────────────────────────────

@app.get("/reconciliation", response_class=HTMLResponse)
async def reconciliation(request: Request, start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    start_date, end_date, parsed_start, parsed_end = _parse_dates(start_date, end_date)
    recon = dp.get_reconciliation_check(db, parsed_start, parsed_end)
    summary = dp.calculate_monthly_summary(db, parsed_start, parsed_end)
    deep_dive = dp.get_disbursement_deep_dive(db, parsed_start, parsed_end)
    return templates.TemplateResponse("reconciliation.html", {
        "request": request,
        "recon": recon,
        "summary": summary,
        "deep_dive": deep_dive,
        "start_date": start_date,
        "end_date": end_date,
    })


# ── IQO Log ───────────────────────────────────────────────────────────────────

@app.get("/iqo", response_class=HTMLResponse)
async def iqo_page(request: Request, db: Session = Depends(get_db)):
    entries = db.query(models.IQOLog).order_by(models.IQOLog.week_start.desc()).all()
    return templates.TemplateResponse("iqo.html", {
        "request": request,
        "entries": entries,
    })

@app.post("/iqo/add")
async def iqo_add(
    week_start: str = Form(...),
    stage: str = Form(...),
    title: str = Form(...),
    description: str = Form(None),
    metric_before: float = Form(None),
    metric_after: float = Form(None),
    metric_label: str = Form(None),
    target_sku: str = Form(None),
    outcome: str = Form(None),
    db: Session = Depends(get_db)
):
    entry = models.IQOLog(
        week_start=datetime.datetime.strptime(week_start, "%Y-%m-%d").date(),
        stage=stage, title=title, description=description,
        metric_before=metric_before, metric_after=metric_after,
        metric_label=metric_label, target_sku=target_sku, outcome=outcome
    )
    db.add(entry)
    db.commit()
    return RedirectResponse(url="/iqo", status_code=303)

@app.post("/iqo/orchestrate/{entry_id}")
async def iqo_orchestrate(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(models.IQOLog).filter(models.IQOLog.id == entry_id).first()
    if entry:
        entry.orchestrated = True
        entry.stage = 'Orchestrate'
        db.commit()
    return RedirectResponse(url="/iqo", status_code=303)

@app.post("/iqo/delete/{entry_id}")
async def iqo_delete(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(models.IQOLog).filter(models.IQOLog.id == entry_id).first()
    if entry:
        db.delete(entry)
        db.commit()
    return RedirectResponse(url="/iqo", status_code=303)


@app.get("/api/fetch-metric")
async def fetch_metric(metric_label: str, week_start: str, target_sku: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        ws = datetime.datetime.strptime(week_start, "%Y-%m-%d").date()
    except ValueError:
        return JSONResponse({"error": "Invalid date format"}, status_code=400)

    before_start = ws - datetime.timedelta(days=7)
    before_end = ws - datetime.timedelta(days=1)
    after_start = ws
    after_end = ws + datetime.timedelta(days=6)

    def get_val(start, end):
        label_norm = metric_label.lower()
        if 'sales' in label_norm:
            q = db.query(models.FinancialEvent).filter(
                models.FinancialEvent.posted_date >= start,
                models.FinancialEvent.posted_date <= end,
                models.FinancialEvent.type == 'Order'
            )
            if target_sku:
                q = q.filter(models.FinancialEvent.sku == target_sku)
            return round(sum(e.product_sales for e in q.all()), 2)
        elif 'cvr' in label_norm or 'conversion' in label_norm:
            q = db.query(models.AdsMetric).filter(
                models.AdsMetric.date >= start,
                models.AdsMetric.date <= end
            )
            if target_sku:
                q = q.filter(models.AdsMetric.sku == target_sku)
            rows = q.all()
            clicks = sum(r.clicks for r in rows)
            orders = sum(r.orders_7d for r in rows)
            return round(orders / clicks * 100, 2) if clicks > 0 else 0.0
        return 0.0

    return {
        "before": get_val(before_start, before_end),
        "after": get_val(after_start, after_end)
    }


# ── Kanban Board ──────────────────────────────────────────────────────────────

@app.get("/board", response_class=HTMLResponse)
async def board(request: Request, db: Session = Depends(get_db)):
    columns = ['To Do', 'In Progress', 'Review', 'Done']
    cards_by_col = {}
    for col in columns:
        cards_by_col[col] = db.query(models.KanbanCard).filter(
            models.KanbanCard.column_name == col
        ).order_by(models.KanbanCard.position).all()
    return templates.TemplateResponse("board.html", {
        "request": request,
        "columns": columns,
        "cards_by_col": cards_by_col,
    })

@app.post("/board/add")
async def board_add(
    title: str = Form(...),
    description: str = Form(None),
    column_name: str = Form('To Do'),
    assignee: str = Form(None),
    due_date: str = Form(None),
    priority: str = Form('Medium'),
    db: Session = Depends(get_db)
):
    due = datetime.datetime.strptime(due_date, "%Y-%m-%d").date() if due_date else None
    card = models.KanbanCard(
        title=title, description=description, column_name=column_name,
        assignee=assignee, due_date=due, priority=priority
    )
    db.add(card)
    db.commit()
    return RedirectResponse(url="/board", status_code=303)

@app.post("/board/move/{card_id}")
async def board_move(request: Request, card_id: int, db: Session = Depends(get_db)):
    column_name = None
    if "application/json" in request.headers.get("content-type", ""):
        data = await request.json()
        column_name = data.get("column_name")
    else:
        form = await request.form()
        column_name = form.get("column_name")

    if not column_name:
        return JSONResponse({"error": "Missing column_name"}, status_code=400)

    card = db.query(models.KanbanCard).filter(models.KanbanCard.id == card_id).first()
    if card:
        card.column_name = column_name
        db.commit()

    if "application/json" in request.headers.get("accept", ""):
        return {"status": "success"}
    return RedirectResponse(url="/board", status_code=303)

@app.post("/board/delete/{card_id}")
async def board_delete(card_id: int, db: Session = Depends(get_db)):
    card = db.query(models.KanbanCard).filter(models.KanbanCard.id == card_id).first()
    if card:
        db.delete(card)
        db.commit()
    return RedirectResponse(url="/board", status_code=303)


# ── Promotions ────────────────────────────────────────────────────────────────

@app.get("/promotions", response_class=HTMLResponse)
async def promotions_page(request: Request, db: Session = Depends(get_db)):
    promos = db.query(models.Promotion).order_by(models.Promotion.start_date.desc()).all()
    inventory = db.query(models.Inventory).all()
    return templates.TemplateResponse("promotions.html", {
        "request": request,
        "promos": promos,
        "inventory": inventory,
    })

@app.post("/promotions/add")
async def promotions_add(
    name: str = Form(...),
    promo_type: str = Form(...),
    sku: str = Form(None),
    start_date: str = Form(...),
    end_date: str = Form(None),
    discount_pct: float = Form(None),
    discount_amount: float = Form(None),
    total_cost: float = Form(0.0),
    units_sold: int = Form(0),
    revenue_generated: float = Form(0.0),
    notes: str = Form(None),
    db: Session = Depends(get_db)
):
    promo = models.Promotion(
        name=name, promo_type=promo_type, sku=sku,
        start_date=datetime.datetime.strptime(start_date, "%Y-%m-%d").date(),
        end_date=datetime.datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None,
        discount_pct=discount_pct, discount_amount=discount_amount,
        total_cost=total_cost, units_sold=units_sold,
        revenue_generated=revenue_generated, notes=notes
    )
    db.add(promo)
    db.commit()
    return RedirectResponse(url="/promotions", status_code=303)

@app.post("/promotions/delete/{promo_id}")
async def promotions_delete(promo_id: int, db: Session = Depends(get_db)):
    promo = db.query(models.Promotion).filter(models.Promotion.id == promo_id).first()
    if promo:
        db.delete(promo)
        db.commit()
    return RedirectResponse(url="/promotions", status_code=303)


# ── SOP ───────────────────────────────────────────────────────────────────────

@app.get("/sop", response_class=HTMLResponse)
async def sop_page(request: Request):
    sop_file = "user_sop.md"
    if not os.path.exists(sop_file):
        with open(sop_file, "w") as f:
            f.write("# Standard Operating Procedure\nEdit this content from the UI.")
    
    with open(sop_file, "r") as f:
        content_md = f.read()
    
    content_html = markdown.markdown(content_md, extensions=['extra', 'nl2br', 'sane_lists'])
    
    return templates.TemplateResponse("sop.html", {
        "request": request, 
        "content_html": content_html,
        "content_md": content_md
    })

@app.post("/sop/update")
async def sop_update(content: str = Form(...)):
    with open("user_sop.md", "w") as f:
        f.write(content)
    return RedirectResponse(url="/sop", status_code=303)


# ── Admin ─────────────────────────────────────────────────────────────────────

@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request, db: Session = Depends(get_db)):
    inventory = db.query(models.Inventory).all()
    active_cogs = db.query(models.COGS).filter(models.COGS.effective_end_date == None).all()
    recent_expenses = db.query(models.OperatingExpense).order_by(
        models.OperatingExpense.date_incurred.desc()).limit(20).all()
    last_sync = db.query(models.SyncLog).order_by(models.SyncLog.id.desc()).first()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "inventory": inventory,
        "active_cogs": active_cogs,
        "expenses": recent_expenses,
        "last_sync": last_sync,
        "datetime": datetime,
    })

@app.get("/admin/backup")
async def backup_database():
    db_path = os.path.join(os.getcwd(), "kareena_erp.db")
    if os.path.exists(db_path):
        return FileResponse(path=db_path, filename="kareena_erp.db", media_type="application/x-sqlite3")
    return {"error": "Database file not found"}

@app.post("/admin/inventory")
async def update_inventory(sku: str = Form(...), local_stock: int = Form(...), db: Session = Depends(get_db)):
    item = db.query(models.Inventory).filter(models.Inventory.sku == sku).first()
    if item:
        item.local_stock = local_stock
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/cogs")
async def add_cogs(sku: str = Form(...), unit_cost: float = Form(...), db: Session = Depends(get_db)):
    today = datetime.date.today()
    existing = db.query(models.COGS).filter(
        models.COGS.sku == sku, models.COGS.effective_end_date == None).first()
    if existing:
        existing.effective_end_date = today
    db.add(models.COGS(sku=sku, unit_cost=unit_cost, effective_start_date=today))
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/expense")
async def add_expense(
    category: str = Form(...), amount: float = Form(...),
    date: str = Form(...), description: str = Form(None),
    db: Session = Depends(get_db)
):
    try:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        date_obj = datetime.date.today()
    db.add(models.OperatingExpense(
        category=category, amount=amount, date_incurred=date_obj, description=description))
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/reset-db")
async def reset_db(request: Request, db: Session = Depends(get_db)):
    try:
        for model in [models.FinancialEvent, models.Inventory, models.COGS,
                      models.OperatingExpense, models.SyncLog, models.AdsMetric,
                      models.BusinessMetric]:
            db.query(model).delete()
        db.commit()
        return RedirectResponse(url="/admin?msg=Database+Reset+Successful", status_code=303)
    except Exception as e:
        logging.error(f"DB Reset failed: {e}")
        return HTMLResponse(content=f"Error resetting database: {e}", status_code=500)

@app.post("/admin/import-whatsapp")
async def import_whatsapp(db: Session = Depends(get_db)):
    whatsapp_dir = "WhatsApp Chat with Fin dashboard brief"
    if not os.path.exists(whatsapp_dir):
        return HTMLResponse(content="WhatsApp folder not found", status_code=404)

    files = os.listdir(whatsapp_dir)
    results = []
    
    # Try to extract date from filename
    def guess_date(filename):
        # Look for Feb 2026, Oct 2025 etc.
        months = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        for m_name, m_num in months.items():
            if m_name in filename:
                # Look for year
                import re
                year_match = re.search(r'20\d{2}', filename)
                if year_match:
                    year = int(year_match.group())
                    last_day = calendar.monthrange(year, m_num)[1]
                    return datetime.date(year, m_num, 1), datetime.date(year, m_num, last_day)
        return None, None

    try:
        for f in files:
            path = os.path.join(whatsapp_dir, f)
            m_start, m_end = guess_date(f)
            if not m_start:
                # Fallback to current month if no date found
                today = datetime.date.today()
                m_start = datetime.date(today.year, today.month, 1)
                m_end = today
            
            f_lower = f.lower()
            if 'settlement' in f_lower or ('transaction' in f_lower and 'all transactions' in f_lower):
                if 'deffered' in f_lower: # Note: spelling from file name
                    count = processor.sync_settlement_csv(path, db, month_start=m_start, month_end=m_end, is_deferred=True)
                    results.append(f"Deferred ({f}): {count} records")
                else:
                    count = processor.sync_settlement_csv(path, db, month_start=m_start, month_end=m_end, is_deferred=False)
                    results.append(f"Settlement ({f}): {count} records")
            
            elif 'businessreport' in f_lower:
                biz = processor.sync_business_csv(path, db_session=db, month_start=m_start)
                results.append(f"Business ({f}): {biz['sessions']} sessions")
            
            elif 'searchterm' in f_lower:
                spend = processor.sync_ads_report(path, db, month_start=m_start)
                results.append(f"Ads ({f}): ₹{spend:,.2f} spend")
            
            elif 'returnreport' in f_lower:
                ret_count = processor.sync_returns_xml(path, db_session=db, month_start=m_start)
                results.append(f"Returns ({f}): {ret_count} found")

        db.add(models.SyncLog(
            status="Success",
            details="WhatsApp Bulk Import: " + "; ".join(results[:50]) # cap length
        ))
        db.commit()
        return RedirectResponse(url="/admin?msg=WhatsApp+Import+Successful", status_code=303)

    except Exception as e:
        logging.error(f"WhatsApp import failed: {e}", exc_info=True)
        return HTMLResponse(content=f"Error importing WhatsApp data: {e}", status_code=500)


@app.get("/settings")
async def get_settings():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "Config file not found"}

@app.post("/settings")
async def update_settings(settings: SettingsUpdate):
    with open('config.json', 'w') as f:
        json.dump(settings.dict(), f, indent=2)
    return {"status": "success"}


# ── Audit / Upload ────────────────────────────────────────────────────────────

@app.get("/audit", response_class=HTMLResponse)
async def audit_page(request: Request):
    return templates.TemplateResponse("audit.html", {"request": request})

@app.post("/upload-manual")
async def upload_manual(
    request: Request,
    month: str = Form(...),
    settlement: UploadFile = File(None),
    deferred: UploadFile = File(None),
    business: UploadFile = File(None),
    ads: UploadFile = File(None),
    returns: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    results = []

    year, mo = map(int, month.split('-'))
    last_day = calendar.monthrange(year, mo)[1]
    month_start = datetime.date(year, mo, 1)
    month_end   = datetime.date(year, mo, last_day)

    try:
        async def save_file(uf: UploadFile) -> str:
            path = os.path.join(upload_dir, uf.filename)
            with open(path, "wb") as f:
                f.write(await uf.read())
            return path

        saved = []

        if settlement and settlement.filename:
            path = await save_file(settlement)
            saved.append(path)
            count = processor.sync_settlement_csv(
                path, db, month_start=month_start, month_end=month_end, is_deferred=False)
            results.append(f"Settlement: {count} records synced")

        if deferred and deferred.filename:
            path = await save_file(deferred)
            saved.append(path)
            count = processor.sync_settlement_csv(
                path, db, month_start=month_start, month_end=month_end, is_deferred=True)
            results.append(f"Deferred: {count} records synced")

        if business and business.filename:
            path = await save_file(business)
            saved.append(path)
            biz = processor.sync_business_csv(path, db_session=db, month_start=month_start)
            results.append(f"Business: {biz['sessions']} sessions, {biz['conversion_pct']}% conversion")

        if ads and ads.filename:
            path = await save_file(ads)
            saved.append(path)
            spend = processor.sync_ads_report(path, db, month_start=month_start)
            results.append(f"Ads: ₹{spend:,.2f} total spend")

        if returns and returns.filename:
            path = await save_file(returns)
            saved.append(path)
            ret_count = processor.sync_returns_xml(path, db_session=db, month_start=month_start)
            results.append(f"Returns: {ret_count} returns found")

        db.add(models.SyncLog(
            status="Success",
            details=f"Monthly upload for {month}: " + "; ".join(results)
        ))
        db.commit()

        for p in saved:
            if os.path.exists(p):
                os.remove(p)

        return RedirectResponse(
            url=f"/?start_date={month_start}&end_date={month_end}",
            status_code=303
        )

    except Exception as e:
        logging.error(f"Upload failed: {e}", exc_info=True)
        return HTMLResponse(
            content=f"<h2>Upload Error</h2><p>{e}</p><a href='/audit'>← Try again</a>",
            status_code=500
        )
