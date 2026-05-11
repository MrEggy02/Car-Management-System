# backend/routers/reports.py (แก้ไขใหม่)

from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from auth import authenticate_user
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter()


# ========== 8.1 Revenue Report (ตาม DFD: D12, D16, D14, D17, D18) ==========
@router.get("/reports/revenue")
def get_revenue_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    """Get revenue report from D12, D16, D14, D17, D18"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 1. Revenue from D16 (invoices - ยอดรับจริง)
        cursor.execute("""
            SELECT 
                SUM(final_total) as total_revenue,
                SUM(total_discount) as total_discount,
                COUNT(*) as invoice_count,
                SUM(received_amount) as total_received
            FROM invoices
            WHERE DATE(paid_date) BETWEEN %s AND %s
            AND payment_status = 'paid'
        """, (start_date, end_date))
        revenue_from_invoices = cursor.fetchone()
        
        # 2. Cost from D14 (parts_usage - ต้นทุนอะไหล่ที่ใช้จริง)
        cursor.execute("""
            SELECT 
                SUM(pu.qty * pu.cost_price) as total_parts_cost,
                COUNT(DISTINCT pu.part_id) as parts_used_count,
                SUM(pu.qty) as total_parts_qty
            FROM parts_usage pu
            LEFT JOIN repair_orders ro ON pu.repair_id = ro.id
            WHERE DATE(ro.start_date) BETWEEN %s AND %s
        """, (start_date, end_date))
        parts_cost = cursor.fetchone()
        
        # 3. Purchase cost from D17, D18 (purchase_orders + purchase_items)
        cursor.execute("""
            SELECT 
                SUM(po.total_amount) as total_purchase_cost,
                COUNT(DISTINCT po.id) as purchase_count
            FROM purchase_orders po
            WHERE DATE(po.order_date) BETWEEN %s AND %s
            AND po.status = 'received'
        """, (start_date, end_date))
        purchase_cost = cursor.fetchone()
        
        # 4. Revenue by payment method from D16
        cursor.execute("""
            SELECT 
                payment_method,
                SUM(final_total) as amount,
                COUNT(*) as count
            FROM invoices
            WHERE DATE(paid_date) BETWEEN %s AND %s
            AND payment_status = 'paid'
            GROUP BY payment_method
        """, (start_date, end_date))
        payment_methods = cursor.fetchall()
        
        # 5. Daily revenue breakdown
        cursor.execute("""
            SELECT 
                DATE(paid_date) as date,
                SUM(final_total) as daily_revenue,
                COUNT(*) as daily_count
            FROM invoices
            WHERE DATE(paid_date) BETWEEN %s AND %s
            AND payment_status = 'paid'
            GROUP BY DATE(paid_date)
            ORDER BY date DESC
            LIMIT 30
        """, (start_date, end_date))
        daily_revenue = cursor.fetchall()
        
        # Calculate net profit
        total_revenue = revenue_from_invoices.get('total_revenue', 0) or 0
        total_cost = (parts_cost.get('total_parts_cost', 0) or 0) + (purchase_cost.get('total_purchase_cost', 0) or 0)
        
        return {
            "summary": {
                "total_revenue": total_revenue,
                "total_discount": revenue_from_invoices.get('total_discount', 0) or 0,
                "invoice_count": revenue_from_invoices.get('invoice_count', 0) or 0,
                "total_received": revenue_from_invoices.get('total_received', 0) or 0,
                "total_parts_cost": parts_cost.get('total_parts_cost', 0) or 0,
                "total_purchase_cost": purchase_cost.get('total_purchase_cost', 0) or 0,
                "net_profit": total_revenue - total_cost
            },
            "payment_methods": payment_methods,
            "daily_revenue": daily_revenue,
            "period": {"start_date": start_date, "end_date": end_date}
        }
    except Exception as e:
        print(f"Error in revenue report: {e}")
        return {}
    finally:
        cursor.close()
        db.close()


# ========== 8.2 Repair Summary Report (ตาม DFD: D10, D9, D13) ==========
@router.get("/reports/repair-summary")
def get_repair_summary_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    """Get repair summary from D10 (job_orders), D9 (vehicles), D13 (repair_orders)"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Repair orders summary from D13
        cursor.execute("""
            SELECT 
                status,
                COUNT(*) as count
            FROM repair_orders
            WHERE DATE(start_date) BETWEEN %s AND %s
            GROUP BY status
        """, (start_date, end_date))
        status_summary = cursor.fetchall()
        
        # Total repairs and completion rate from D13
        cursor.execute("""
            SELECT 
                COUNT(*) as total_repairs,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_repairs,
                AVG(CASE WHEN status = 'completed' AND end_date IS NOT NULL 
                    THEN TIMESTAMPDIFF(HOUR, start_date, end_date) 
                    ELSE NULL END) as avg_repair_hours
            FROM repair_orders
            WHERE DATE(start_date) BETWEEN %s AND %s
        """, (start_date, end_date))
        repair_stats = cursor.fetchone()
        
        # Repairs by vehicle from D9 (vehicles) and D10 (job_orders)
        cursor.execute("""
            SELECT 
                v.license_plate,
                v.model,
                v.brand,
                COUNT(DISTINCT ro.id) as repair_count,
                SUM(CASE WHEN ro.status = 'completed' THEN 1 ELSE 0 END) as completed_count
            FROM repair_orders ro
            LEFT JOIN job_orders jo ON ro.job_order_id = jo.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            WHERE DATE(ro.start_date) BETWEEN %s AND %s
            GROUP BY v.id, v.license_plate, v.model, v.brand
            ORDER BY repair_count DESC
            LIMIT 10
        """, (start_date, end_date))
        vehicle_stats = cursor.fetchall()
        
        # Repairs by mechanic from D13
        cursor.execute("""
            SELECT 
                u.fullname as mechanic_name,
                COUNT(ro.id) as repair_count,
                SUM(CASE WHEN ro.status = 'completed' THEN 1 ELSE 0 END) as completed_count
            FROM repair_orders ro
            LEFT JOIN users u ON ro.mechanic_id = u.id
            WHERE DATE(ro.start_date) BETWEEN %s AND %s
            GROUP BY ro.mechanic_id, u.fullname
            ORDER BY repair_count DESC
            LIMIT 10
        """, (start_date, end_date))
        mechanic_stats = cursor.fetchall()
        
        # Daily repairs from D13
        cursor.execute("""
            SELECT 
                DATE(start_date) as date,
                COUNT(*) as daily_repairs,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as daily_completed
            FROM repair_orders
            WHERE DATE(start_date) BETWEEN %s AND %s
            GROUP BY DATE(start_date)
            ORDER BY date DESC
            LIMIT 30
        """, (start_date, end_date))
        daily_repairs = cursor.fetchall()
        
        return {
            "status_summary": status_summary,
            "repair_stats": repair_stats,
            "vehicle_stats": vehicle_stats,
            "mechanic_stats": mechanic_stats,
            "daily_repairs": daily_repairs,
            "period": {"start_date": start_date, "end_date": end_date}
        }
    except Exception as e:
        print(f"Error in repair summary report: {e}")
        return {}
    finally:
        cursor.close()
        db.close()


# ========== 8.3 Parts Usage Report (ตาม DFD: D13, D14, D15, D5) ==========
@router.get("/reports/parts-usage")
def get_parts_usage_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    """Get parts usage from D14 (parts_usage), D13 (repair_orders), D15 (stock_movement), D5 (parts)"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Top parts usage from D14 and D5
        cursor.execute("""
            SELECT 
                p.id,
                p.name as part_name,
                p.brand,
                SUM(pu.qty) as total_used,
                SUM(pu.qty * pu.cost_price) as total_cost,
                p.stock_qty as current_stock,
                p.min_stock
            FROM parts_usage pu
            LEFT JOIN parts p ON pu.part_id = p.id
            LEFT JOIN repair_orders ro ON pu.repair_id = ro.id
            WHERE DATE(ro.start_date) BETWEEN %s AND %s
            GROUP BY p.id, p.name, p.brand, p.stock_qty, p.min_stock
            ORDER BY total_used DESC
            LIMIT 50
        """, (start_date, end_date))
        top_parts = cursor.fetchall()
        
        # Stock movement summary from D15
        cursor.execute("""
            SELECT 
                type,
                SUM(qty) as total_qty,
                COUNT(*) as movement_count
            FROM stock_movement
            WHERE DATE(date) BETWEEN %s AND %s
            GROUP BY type
        """, (start_date, end_date))
        stock_movements = cursor.fetchall()
        
        # Low stock alert from D5
        cursor.execute("""
            SELECT 
                id, name, brand, stock_qty, min_stock
            FROM parts
            WHERE stock_qty <= min_stock AND min_stock > 0
            ORDER BY stock_qty ASC
            LIMIT 20
        """)
        low_stock_parts = cursor.fetchall()
        
        # Total stock value from D5
        cursor.execute("""
            SELECT 
                SUM(stock_qty * cost_price) as total_stock_value,
                COUNT(*) as total_parts
            FROM parts
        """)
        stock_value = cursor.fetchone()
        
        return {
            "top_parts": top_parts,
            "stock_movements": stock_movements,
            "low_stock_parts": low_stock_parts,
            "stock_value": stock_value,
            "period": {"start_date": start_date, "end_date": end_date}
        }
    except Exception as e:
        print(f"Error in parts usage report: {e}")
        return {}
    finally:
        cursor.close()
        db.close()


# ========== 8.4 Service/Repair Item Report (ตาม DFD: D16, D10, D4, D11, D12) ==========
@router.get("/reports/service-items")
def get_service_items_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    """Get service performance from D4 (services), D11/D12 (quotations), D10 (job_orders), D16 (invoices)"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Top services from D11/D12 (quotation_items) with actual revenue from D16 (invoices)
        cursor.execute("""
            SELECT 
                s.id,
                s.service_name,
                s.price as unit_price,
                COUNT(qi.id) as usage_count,
                SUM(qi.total_price) as quoted_amount,
                SUM(i.final_total * (qi.total_price / q.total_amount)) as actual_revenue
            FROM quotation_items qi
            LEFT JOIN services s ON qi.ref_id = s.id
            LEFT JOIN quotations q ON qi.quotation_id = q.id
            LEFT JOIN job_orders jo ON q.job_order_id = jo.id
            LEFT JOIN invoices i ON jo.id = i.job_order_id
            WHERE qi.item_type = 'service'
            AND q.status = 'approved'
            AND DATE(q.created_at) BETWEEN %s AND %s
            GROUP BY s.id, s.service_name, s.price
            ORDER BY usage_count DESC
            LIMIT 20
        """, (start_date, end_date))
        top_services = cursor.fetchall()
        
        # Service statistics by vehicle brand from D10 and D4
        cursor.execute("""
            SELECT 
                v.brand,
                s.service_name,
                COUNT(qi.id) as service_count
            FROM quotation_items qi
            LEFT JOIN services s ON qi.ref_id = s.id
            LEFT JOIN quotations q ON qi.quotation_id = q.id
            LEFT JOIN job_orders jo ON q.job_order_id = jo.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            WHERE qi.item_type = 'service'
            AND DATE(q.created_at) BETWEEN %s AND %s
            GROUP BY v.brand, s.service_name
            ORDER BY service_count DESC
            LIMIT 30
        """, (start_date, end_date))
        service_by_brand = cursor.fetchall()
        
        return {
            "top_services": top_services,
            "service_by_brand": service_by_brand,
            "period": {"start_date": start_date, "end_date": end_date}
        }
    except Exception as e:
        print(f"Error in service items report: {e}")
        return {}
    finally:
        cursor.close()
        db.close()


# ========== 8.5 Promotion Usage Report (ตาม DFD: D6, D11, D12, D16) ==========
@router.get("/reports/promotion-usage")
def get_promotion_usage_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    """Get promotion usage from D6 (promotions), D11/D12 (quotations), D16 (invoices)"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Promotion usage summary from D16 (invoices) with D6 (promotions)
        cursor.execute("""
            SELECT 
                p.id,
                p.name as promotion_name,
                p.discount_type,
                p.discount_value,
                COUNT(i.id) as usage_count,
                SUM(i.total_discount) as total_discount_given,
                SUM(i.final_total) as total_revenue
            FROM invoices i
            LEFT JOIN promotions p ON i.promotion_id = p.id
            WHERE DATE(i.paid_date) BETWEEN %s AND %s
            AND i.promotion_id IS NOT NULL
            GROUP BY p.id, p.name, p.discount_type, p.discount_value
            ORDER BY usage_count DESC
        """, (start_date, end_date))
        promotion_usage = cursor.fetchall()
        
        # Promotion usage at quotation stage from D11/D12
        cursor.execute("""
            SELECT 
                p.name as promotion_name,
                COUNT(q.id) as quoted_count,
                SUM(q.total_discount) as quoted_discount
            FROM quotations q
            LEFT JOIN promotions p ON q.promotion_id = p.id
            WHERE DATE(q.created_at) BETWEEN %s AND %s
            AND q.promotion_id IS NOT NULL
            GROUP BY p.name
            ORDER BY quoted_count DESC
        """, (start_date, end_date))
        promotion_quoted = cursor.fetchall()
        
        # Overall promotion summary from D16
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT promotion_id) as total_promotions_used,
                SUM(total_discount) as total_discount_given,
                COUNT(*) as total_invoices_with_promotion
            FROM invoices
            WHERE DATE(paid_date) BETWEEN %s AND %s
            AND promotion_id IS NOT NULL
        """, (start_date, end_date))
        summary = cursor.fetchone()
        
        return {
            "promotion_usage": promotion_usage,
            "promotion_quoted": promotion_quoted,
            "summary": summary,
            "period": {"start_date": start_date, "end_date": end_date}
        }
    except Exception as e:
        print(f"Error in promotion usage report: {e}")
        return {}
    finally:
        cursor.close()
        db.close()


# ========== Dashboard Summary ==========
@router.get("/reports/dashboard-summary")
def get_dashboard_summary(user: dict = Depends(authenticate_user)):
    """Get quick summary for dashboard"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        this_month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        
        # Today's revenue
        cursor.execute("""
            SELECT SUM(final_total) as today_revenue, COUNT(*) as today_invoices
            FROM invoices
            WHERE DATE(paid_date) = %s AND payment_status = 'paid'
        """, (today,))
        today_stats = cursor.fetchone()
        
        # This month revenue
        cursor.execute("""
            SELECT SUM(final_total) as month_revenue, COUNT(*) as month_invoices
            FROM invoices
            WHERE DATE(paid_date) >= %s AND payment_status = 'paid'
        """, (this_month_start,))
        month_stats = cursor.fetchone()
        
        # Repair statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_repairs,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_repairs,
                SUM(CASE WHEN status = 'working' THEN 1 ELSE 0 END) as working_repairs,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_repairs
            FROM repair_orders
        """)
        repair_stats = cursor.fetchone()
        
        # Low stock count
        cursor.execute("""
            SELECT COUNT(*) as low_stock_count
            FROM parts
            WHERE stock_qty <= min_stock AND min_stock > 0
        """)
        low_stock = cursor.fetchone()
        
        # Pending job orders
        cursor.execute("""
            SELECT COUNT(*) as pending_jobs
            FROM job_orders
            WHERE status = 'pending'
        """)
        pending_jobs = cursor.fetchone()
        
        return {
            "today_revenue": today_stats.get('today_revenue', 0) or 0,
            "today_invoices": today_stats.get('today_invoices', 0) or 0,
            "month_revenue": month_stats.get('month_revenue', 0) or 0,
            "month_invoices": month_stats.get('month_invoices', 0) or 0,
            "total_repairs": repair_stats.get('total_repairs', 0) or 0,
            "pending_repairs": repair_stats.get('pending_repairs', 0) or 0,
            "working_repairs": repair_stats.get('working_repairs', 0) or 0,
            "completed_repairs": repair_stats.get('completed_repairs', 0) or 0,
            "low_stock_count": low_stock.get('low_stock_count', 0) or 0,
            "pending_jobs": pending_jobs.get('pending_jobs', 0) or 0
        }
    except Exception as e:
        print(f"Error in dashboard summary: {e}")
        return {}
    finally:
        cursor.close()
        db.close()