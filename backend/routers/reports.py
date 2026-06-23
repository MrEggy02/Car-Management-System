# backend/routers/reports.py (Final Version 2 - ตาม DFD 8.1 - 8.5)
from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from auth import authenticate_user
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter()


# ========== 8.1 Revenue Report (ລາຍງານລາຍຮັບ) ==========
# ตาม DFD: D12, D16, D14, D17, D18
@router.get("/reports/revenue")
def get_revenue_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    """
    Process 8.1: Revenue Report - Report of income and expenses
    ລາຍງານລາຍຮັບ - ສະແດງລາຍຮັບ, ຄ່າໃຊ້ຈ່າຍ, ແລະ ກຳໄລສຸດທິ
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 1. Revenue from D16 (invoices - real income)
        cursor.execute("""
            SELECT 
                SUM(final_total) as total_revenue,
                SUM(total_discount) as total_discount_given,
                COUNT(*) as invoice_count,
                SUM(received_amount) as total_received,
                SUM(change_amount) as total_change
            FROM invoices
            WHERE DATE(paid_date) BETWEEN %s AND %s
            AND payment_status = 'paid'
        """, (start_date, end_date))
        revenue_data = cursor.fetchone()
        
        # 2. Cost of parts used from D14 (parts_usage - actual parts cost)
        cursor.execute("""
            SELECT 
                SUM(pu.qty * pu.cost_price) as total_parts_cost,
                COUNT(DISTINCT pu.part_id) as distinct_parts_used,
                SUM(pu.qty) as total_parts_quantity
            FROM parts_usage pu
            LEFT JOIN repair_orders ro ON pu.repair_id = ro.id
            LEFT JOIN job_orders jo ON ro.job_order_id = jo.id
            WHERE DATE(ro.start_date) BETWEEN %s AND %s
        """, (start_date, end_date))
        parts_cost_data = cursor.fetchone()
        
        # 3. Purchase cost from D17 + D18 (purchase orders)
        cursor.execute("""
            SELECT 
                SUM(po.total_amount) as total_purchase_cost,
                COUNT(DISTINCT po.id) as purchase_order_count,
                COUNT(pi.id) as purchased_items_count
            FROM purchase_orders po
            LEFT JOIN purchase_items pi ON po.id = pi.purchase_id
            WHERE DATE(po.order_date) BETWEEN %s AND %s
            AND po.status IN ('ordering', 'partial', 'completed')
        """, (start_date, end_date))
        purchase_cost_data = cursor.fetchone()
        
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
                COUNT(*) as daily_invoice_count
            FROM invoices
            WHERE DATE(paid_date) BETWEEN %s AND %s
            AND payment_status = 'paid'
            GROUP BY DATE(paid_date)
            ORDER BY date DESC
            LIMIT 30
        """, (start_date, end_date))
        daily_revenue = cursor.fetchall()
        
        # Calculate totals
        total_revenue = revenue_data.get('total_revenue', 0) or 0
        total_parts_cost = parts_cost_data.get('total_parts_cost', 0) or 0
        total_purchase_cost = purchase_cost_data.get('total_purchase_cost', 0) or 0
        total_cost = total_parts_cost + total_purchase_cost
        net_profit = total_revenue - total_cost
        
        return {
            "summary": {
                "total_revenue": float(total_revenue),
                "total_discount_given": float(revenue_data.get('total_discount_given', 0) or 0),
                "invoice_count": revenue_data.get('invoice_count', 0) or 0,
                "total_received": float(revenue_data.get('total_received', 0) or 0),
                "total_parts_cost": float(total_parts_cost),
                "total_purchase_cost": float(total_purchase_cost),
                "total_cost": float(total_cost),
                "net_profit": float(net_profit),
                "profit_margin": (net_profit / total_revenue * 100) if total_revenue > 0 else 0
            },
            "payment_methods": payment_methods,
            "daily_revenue": daily_revenue,
            "period": {"start_date": start_date, "end_date": end_date}
        }
    except Exception as e:
        print(f"Error in revenue report: {e}")
        import traceback
        traceback.print_exc()
        return {}
    finally:
        cursor.close()
        db.close()


# ========== 8.2 Repair Summary Report (ລາຍງານການສ້ອມແປງ) ==========
# ตาม DFD: D10, D9, D13
@router.get("/reports/repair-summary")
def get_repair_summary_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    """
    Process 8.2: Repair Summary Report - Overview of repair work
    ລາຍງານການສ້ອມແປງ - ສະຖານະງານສ້ອມ ແລະ ປະສິດທິພາບຊ່າງ
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 1. Repair order status summary from D13
        cursor.execute("""
            SELECT 
                status,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM repair_orders), 1) as percentage
            FROM repair_orders
            WHERE DATE(start_date) BETWEEN %s AND %s
            GROUP BY status
        """, (start_date, end_date))
        status_summary = cursor.fetchall()
        
        # 2. Overall repair statistics from D13
        cursor.execute("""
            SELECT 
                COUNT(*) as total_repairs,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_repairs,
                SUM(CASE WHEN status = 'working' THEN 1 ELSE 0 END) as working_repairs,
                SUM(CASE WHEN status = 'waiting' THEN 1 ELSE 0 END) as waiting_repairs,
                SUM(CASE WHEN status = 'paused' THEN 1 ELSE 0 END) as paused_repairs,
                ROUND(AVG(CASE WHEN status = 'completed' AND end_date IS NOT NULL 
                    THEN TIMESTAMPDIFF(HOUR, start_date, end_date) 
                    ELSE NULL END), 1) as avg_repair_hours
            FROM repair_orders
            WHERE DATE(start_date) BETWEEN %s AND %s
        """, (start_date, end_date))
        repair_stats = cursor.fetchone()
        
        # 3. Repairs by vehicle brand from D9 (vehicles) + D10 + D13
        cursor.execute("""
            SELECT 
                COALESCE(b.name, 'ບໍ່ລະບຸ') as brand,
                COUNT(DISTINCT ro.id) as repair_count,
                SUM(CASE WHEN ro.status = 'completed' THEN 1 ELSE 0 END) as completed_count,
                ROUND(AVG(CASE WHEN ro.status = 'completed' AND ro.end_date IS NOT NULL 
                    THEN TIMESTAMPDIFF(HOUR, ro.start_date, ro.end_date) 
                    ELSE NULL END), 1) as avg_hours
            FROM repair_orders ro
            LEFT JOIN job_orders jo ON ro.job_order_id = jo.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            WHERE DATE(ro.start_date) BETWEEN %s AND %s
            GROUP BY b.id, b.name
            ORDER BY repair_count DESC
            LIMIT 10
        """, (start_date, end_date))
        vehicle_stats = cursor.fetchall()
        
        # 4. Repairs by mechanic from D13
        cursor.execute("""
            SELECT 
                COALESCE(e.name, 'ບໍ່ມີຊ່າງ') as mechanic_name,
                COUNT(ro.id) as repair_count,
                SUM(CASE WHEN ro.status = 'completed' THEN 1 ELSE 0 END) as completed_count,
                ROUND(AVG(CASE WHEN ro.status = 'completed' AND ro.end_date IS NOT NULL 
                    THEN TIMESTAMPDIFF(HOUR, ro.start_date, ro.end_date) 
                    ELSE NULL END), 1) as avg_hours_per_repair
            FROM repair_orders ro
            LEFT JOIN Employees e ON ro.mechanic_id = e.id
            WHERE DATE(ro.start_date) BETWEEN %s AND %s
            GROUP BY ro.mechanic_id, e.name
            ORDER BY repair_count DESC
            LIMIT 10
        """, (start_date, end_date))
        mechanic_stats = cursor.fetchall()
        
        # 5. Daily repair trends
        cursor.execute("""
            SELECT 
                DATE(start_date) as date,
                COUNT(*) as daily_repairs,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as daily_completed,
                SUM(CASE WHEN status = 'working' THEN 1 ELSE 0 END) as daily_in_progress
            FROM repair_orders
            WHERE DATE(start_date) BETWEEN %s AND %s
            GROUP BY DATE(start_date)
            ORDER BY date DESC
            LIMIT 30
        """, (start_date, end_date))
        daily_repairs = cursor.fetchall()
        
        # Calculate completion rate
        completion_rate = 0
        if repair_stats.get('total_repairs', 0) > 0:
            completion_rate = (repair_stats.get('completed_repairs', 0) / repair_stats.get('total_repairs', 1)) * 100
        
        return {
            "status_summary": status_summary,
            "repair_stats": {
                "total_repairs": repair_stats.get('total_repairs', 0) or 0,
                "completed_repairs": repair_stats.get('completed_repairs', 0) or 0,
                "working_repairs": repair_stats.get('working_repairs', 0) or 0,
                "waiting_repairs": repair_stats.get('waiting_repairs', 0) or 0,
                "paused_repairs": repair_stats.get('paused_repairs', 0) or 0,
                "completion_rate": round(completion_rate, 1),
                "avg_repair_hours": float(repair_stats.get('avg_repair_hours', 0) or 0)
            },
            "vehicle_stats": vehicle_stats,
            "mechanic_stats": mechanic_stats,
            "daily_repairs": daily_repairs,
            "period": {"start_date": start_date, "end_date": end_date}
        }
    except Exception as e:
        print(f"Error in repair summary report: {e}")
        import traceback
        traceback.print_exc()
        return {}
    finally:
        cursor.close()
        db.close()


# ========== 8.3 Parts Usage Report (ລາຍງານຍອດນຳໃຊ້ອາໄຫຼ່) ==========
# ตาม DFD: D14, D15, D5
@router.get("/reports/parts-usage")
def get_parts_usage_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    """
    Process 8.3: Parts Usage Report - Parts consumption and inventory turnover
    ລາຍງານຍອດນຳໃຊ້ອາໄຫຼ່ - ການນຳໃຊ້ອາໄຫຼ່ ແລະ ການໝູນວຽນສາງ
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 1. Top parts usage from D14 (parts_usage)
        cursor.execute("""
            SELECT 
                p.id,
                p.name as part_name,
                COALESCE(c.name, 'ບໍ່ມີປະເພດ') as category_name,
                u.name as unit_name,
                SUM(pu.qty) as total_quantity_used,
                SUM(pu.qty * pu.cost_price) as total_cost,
                p.stock_qty as current_stock,
                p.min_stock,
                CASE 
                    WHEN p.stock_qty <= p.min_stock THEN 'ສະຕ໋ອກຕ່ຳ'
                    WHEN p.stock_qty <= p.min_stock * 2 THEN 'ສະຕ໋ອກກຳລັງຈະໝົດ'
                    ELSE 'ສະຕ໋ອກປົກກະຕິ'
                END as stock_status
            FROM parts_usage pu
            LEFT JOIN parts p ON pu.part_id = p.id
            LEFT JOIN Part_Categories c ON p.category_id = c.id
            LEFT JOIN Units u ON p.unit_id = u.id
            LEFT JOIN repair_orders ro ON pu.repair_id = ro.id
            WHERE DATE(ro.start_date) BETWEEN %s AND %s
            GROUP BY p.id, p.name, c.name, u.name, p.stock_qty, p.min_stock
            ORDER BY total_quantity_used DESC
            LIMIT 50
        """, (start_date, end_date))
        top_parts = cursor.fetchall()
        
        # 2. Stock movement summary from D15
        cursor.execute("""
            SELECT 
                type,
                SUM(qty) as total_quantity,
                COUNT(*) as movement_count
            FROM stock_movement
            WHERE DATE(date) BETWEEN %s AND %s
            GROUP BY type
        """, (start_date, end_date))
        stock_movements = cursor.fetchall()
        
        # 3. Low stock alert from D5 (parts)
        cursor.execute("""
            SELECT 
                p.id, 
                p.name, 
                p.stock_qty, 
                p.min_stock,
                COALESCE(c.name, 'ບໍ່ມີປະເພດ') as category_name,
                u.name as unit_name,
                CASE 
                    WHEN p.stock_qty = 0 THEN 'ສະຕ໋ອກໝົດ'
                    ELSE 'ສະຕ໋ອກຕ່ຳ'
                END as alert_level
            FROM parts p
            LEFT JOIN Part_Categories c ON p.category_id = c.id
            LEFT JOIN Units u ON p.unit_id = u.id
            WHERE p.stock_qty <= p.min_stock AND p.min_stock > 0
            ORDER BY (p.stock_qty / p.min_stock) ASC
            LIMIT 30
        """)
        low_stock_parts = cursor.fetchall()
        
        # 4. Total stock value from D5
        cursor.execute("""
            SELECT 
                SUM(stock_qty * cost_price) as total_stock_value,
                COUNT(*) as total_part_types,
                SUM(stock_qty) as total_stock_quantity,
                AVG(cost_price) as avg_cost_price
            FROM parts
        """)
        stock_value = cursor.fetchone()
        
        # 5. Category-wise stock summary
        cursor.execute("""
            SELECT 
                COALESCE(c.name, 'ບໍ່ມີປະເພດ') as category_name,
                COUNT(p.id) as part_count,
                SUM(p.stock_qty) as total_quantity,
                SUM(p.stock_qty * p.cost_price) as total_value
            FROM parts p
            LEFT JOIN Part_Categories c ON p.category_id = c.id
            GROUP BY c.id, c.name
            ORDER BY total_value DESC
        """)
        category_stock = cursor.fetchall()
        
        return {
            "top_parts": top_parts,
            "stock_movements": stock_movements,
            "low_stock_parts": low_stock_parts,
            "stock_value": {
                "total_stock_value": float(stock_value.get('total_stock_value', 0) or 0),
                "total_part_types": stock_value.get('total_part_types', 0) or 0,
                "total_stock_quantity": stock_value.get('total_stock_quantity', 0) or 0,
                "avg_cost_price": float(stock_value.get('avg_cost_price', 0) or 0)
            },
            "category_stock": category_stock,
            "period": {"start_date": start_date, "end_date": end_date}
        }
    except Exception as e:
        print(f"Error in parts usage report: {e}")
        import traceback
        traceback.print_exc()
        return {}
    finally:
        cursor.close()
        db.close()


# ========== 8.4 Service Items Report (ລາຍງານລາຍການສ້ອມແປງ) ==========
# ตาม DFD: D16, D10, D4, D11, D12
@router.get("/reports/service-items")
def get_service_items_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    """
    Process 8.4: Service Items Report - Analysis of repair services
    ລາຍງານລາຍການສ້ອມແປງ - ວິເຄາະປະເພດການສ້ອມແປງທີ່ພົບຫຼາຍທີ່ສຸດ
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 1. Top services from D11/D12 (quotation_items) with revenue from D16
        cursor.execute("""
            SELECT 
                s.id,
                s.name as service_name,
                s.price as unit_price,
                COUNT(qi.id) as service_count,
                SUM(qi.qty) as total_quantity,
                SUM(qi.total) as quoted_amount,
                AVG(qi.unit_price) as avg_price
            FROM quotation_items qi
            LEFT JOIN services s ON qi.service_id = s.id
            LEFT JOIN quotations q ON qi.quotation_id = q.id
            WHERE qi.service_id IS NOT NULL
            AND q.status = 'approved'
            AND DATE(q.created_at) BETWEEN %s AND %s
            GROUP BY s.id, s.name, s.price
            ORDER BY service_count DESC
            LIMIT 20
        """, (start_date, end_date))
        top_services = cursor.fetchall()
        
        # 2. Service statistics by vehicle brand
        cursor.execute("""
            SELECT 
                COALESCE(b.name, 'ບໍ່ລະບຸ') as brand,
                s.name as service_name,
                COUNT(qi.id) as service_count,
                SUM(qi.total) as total_revenue
            FROM quotation_items qi
            LEFT JOIN services s ON qi.service_id = s.id
            LEFT JOIN quotations q ON qi.quotation_id = q.id
            LEFT JOIN job_orders jo ON q.job_order_id = jo.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            WHERE qi.service_id IS NOT NULL
            AND q.status = 'approved'
            AND DATE(q.created_at) BETWEEN %s AND %s
            GROUP BY b.id, b.name, s.id, s.name
            ORDER BY service_count DESC
            LIMIT 30
        """, (start_date, end_date))
        service_by_brand = cursor.fetchall()
        
        # 3. Monthly service trends
        cursor.execute("""
            SELECT 
                DATE_FORMAT(q.created_at, '%%Y-%%m') as month,
                COUNT(DISTINCT qi.id) as service_count,
                SUM(qi.total) as monthly_revenue
            FROM quotation_items qi
            LEFT JOIN quotations q ON qi.quotation_id = q.id
            WHERE qi.service_id IS NOT NULL
            AND q.status = 'approved'
            AND DATE(q.created_at) BETWEEN %s AND %s
            GROUP BY DATE_FORMAT(q.created_at, '%%Y-%%m')
            ORDER BY month DESC
            LIMIT 12
        """, (start_date, end_date))
        monthly_service_trends = cursor.fetchall()
        
        # Convert decimal to float
        for service in top_services:
            if service.get('unit_price'):
                service['unit_price'] = float(service['unit_price'])
            if service.get('quoted_amount'):
                service['quoted_amount'] = float(service['quoted_amount'])
            if service.get('avg_price'):
                service['avg_price'] = float(service['avg_price'])
        
        return {
            "top_services": top_services,
            "service_by_brand": service_by_brand,
            "monthly_service_trends": monthly_service_trends,
            "period": {"start_date": start_date, "end_date": end_date}
        }
    except Exception as e:
        print(f"Error in service items report: {e}")
        import traceback
        traceback.print_exc()
        return {}
    finally:
        cursor.close()
        db.close()


# ========== 8.5 Promotion Usage Report (ລາຍງານການນຳໃຊ້ໂປຣໂມຊັນ) ==========
# ตาม DFD: D6, D11, D12, D16
@router.get("/reports/promotion-usage")
def get_promotion_usage_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    """
    Process 8.5: Promotion Usage Report - Effectiveness of marketing campaigns
    ລາຍງານການນຳໃຊ້ໂປຣໂມຊັນ - ປະເມີນປະສິດທິພາບຂອງໂປຣໂມຊັນ
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 1. Promotion usage from invoices (D16)
        cursor.execute("""
            SELECT 
                p.id,
                p.name as promotion_name,
                p.discount_type,
                p.value as discount_value,
                p.value,
                COUNT(i.id) as usage_count,
                SUM(i.total_discount) as total_discount_given,
                SUM(i.final_total) as total_revenue,
                SUM(i.final_total) as total_revenue_with_promotion,
                AVG(i.total_discount) as avg_discount_per_use
            FROM invoices i
            INNER JOIN job_orders jo ON i.job_order_id = jo.id
            INNER JOIN quotations q ON q.job_order_id = jo.id AND q.status = 'approved'
            LEFT JOIN promotions p ON q.promotion_id = p.id
            WHERE DATE(i.paid_date) BETWEEN %s AND %s
            AND q.promotion_id IS NOT NULL
            AND i.payment_status = 'paid'
            GROUP BY p.id, p.name, p.discount_type, p.value
            ORDER BY usage_count DESC
        """, (start_date, end_date))
        promotion_usage = cursor.fetchall()
        
        # 2. Promotions quoted but not yet used (D11/D12)
        cursor.execute("""
            SELECT 
                p.name as promotion_name,
                COUNT(DISTINCT q.id) as quoted_count,
                SUM(q.discount_amount) as total_quoted_discount,
                SUM(q.discount_amount) as quoted_discount
            FROM quotations q
            LEFT JOIN promotions p ON q.promotion_id = p.id
            WHERE DATE(q.created_at) BETWEEN %s AND %s
            AND q.promotion_id IS NOT NULL
            AND q.status = 'approved'
            GROUP BY p.id, p.name
            ORDER BY quoted_count DESC
        """, (start_date, end_date))
        promotion_quoted = cursor.fetchall()
        
        # 3. Overall promotion summary
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT q.promotion_id) as total_promotions_used,
                SUM(i.total_discount) as total_discount_given,
                COUNT(*) as total_invoices_with_promotion,
                SUM(i.final_total) as total_revenue_from_promo_invoices,
                AVG(i.total_discount) as avg_discount_per_invoice
            FROM invoices i
            INNER JOIN job_orders jo ON i.job_order_id = jo.id
            INNER JOIN quotations q ON q.job_order_id = jo.id AND q.status = 'approved'
            WHERE DATE(i.paid_date) BETWEEN %s AND %s
            AND q.promotion_id IS NOT NULL
            AND i.payment_status = 'paid'
        """, (start_date, end_date))
        summary = cursor.fetchone()
        
        # 4. Compare revenue with vs without promotion
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN q.promotion_id IS NOT NULL THEN 'With Promotion'
                    ELSE 'Without Promotion'
                END as promo_status,
                COUNT(*) as invoice_count,
                SUM(i.final_total) as total_revenue,
                AVG(i.final_total) as avg_invoice_value
            FROM invoices i
            LEFT JOIN job_orders jo ON i.job_order_id = jo.id
            LEFT JOIN quotations q ON q.job_order_id = jo.id AND q.status = 'approved'
            WHERE DATE(i.paid_date) BETWEEN %s AND %s
            AND i.payment_status = 'paid'
            GROUP BY CASE WHEN q.promotion_id IS NOT NULL THEN 'With Promotion' ELSE 'Without Promotion' END
        """, (start_date, end_date))
        comparison = cursor.fetchall()
        
        # Convert decimal to float
        for promo in promotion_usage:
            if promo.get('value'):
                promo['value'] = float(promo['value'])
            if promo.get('discount_value'):
                promo['discount_value'] = float(promo['discount_value'])
            if promo.get('total_discount_given'):
                promo['total_discount_given'] = float(promo['total_discount_given'])
            if promo.get('total_revenue_with_promotion'):
                promo['total_revenue_with_promotion'] = float(promo['total_revenue_with_promotion'])
            if promo.get('total_revenue'):
                promo['total_revenue'] = float(promo['total_revenue'])
            if promo.get('avg_discount_per_use'):
                promo['avg_discount_per_use'] = float(promo['avg_discount_per_use'])
                
        for promo in promotion_quoted:
            if promo.get('total_quoted_discount'):
                promo['total_quoted_discount'] = float(promo['total_quoted_discount'])
            if promo.get('quoted_discount'):
                promo['quoted_discount'] = float(promo['quoted_discount'])
        
        return {
            "promotion_usage": promotion_usage,
            "promotion_quoted": promotion_quoted,
            "summary": {
                "total_promotions_used": summary.get('total_promotions_used', 0) or 0,
                "total_discount_given": float(summary.get('total_discount_given', 0) or 0),
                "total_invoices_with_promotion": summary.get('total_invoices_with_promotion', 0) or 0,
                "total_revenue_from_promo_invoices": float(summary.get('total_revenue_from_promo_invoices', 0) or 0),
                "avg_discount_per_invoice": float(summary.get('avg_discount_per_invoice', 0) or 0)
            },
            "comparison": comparison,
            "period": {"start_date": start_date, "end_date": end_date}
        }
    except Exception as e:
        print(f"Error in promotion usage report: {e}")
        import traceback
        traceback.print_exc()
        return {}
    finally:
        cursor.close()
        db.close()


# ========== Dashboard Summary (Quick Overview) ==========
@router.get("/reports/dashboard-summary")
def get_dashboard_summary(user: dict = Depends(authenticate_user)):
    """
    Dashboard Summary - Quick statistics for main dashboard
    ສະຫຼຸບຂໍ້ມູນດ່ວນສຳລັບໜ້າ Dashboard
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        this_month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        
        # Today's revenue from D16
        cursor.execute("""
            SELECT 
                COALESCE(SUM(final_total), 0) as today_revenue,
                COUNT(*) as today_invoices
            FROM invoices
            WHERE DATE(paid_date) = %s AND payment_status = 'paid'
        """, (today,))
        today_stats = cursor.fetchone()
        
        # This month revenue from D16
        cursor.execute("""
            SELECT 
                COALESCE(SUM(final_total), 0) as month_revenue,
                COUNT(*) as month_invoices
            FROM invoices
            WHERE DATE(paid_date) >= %s AND payment_status = 'paid'
        """, (this_month_start,))
        month_stats = cursor.fetchone()
        
        # Repair statistics from D13
        cursor.execute("""
            SELECT 
                COUNT(*) as total_repairs,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_repairs,
                SUM(CASE WHEN status = 'working' THEN 1 ELSE 0 END) as working_repairs,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_repairs,
                SUM(CASE WHEN status = 'waiting' THEN 1 ELSE 0 END) as waiting_repairs
            FROM repair_orders
        """)
        repair_stats = cursor.fetchone()
        
        # Low stock count from D5
        cursor.execute("""
            SELECT COUNT(*) as low_stock_count
            FROM parts
            WHERE stock_qty <= min_stock AND min_stock > 0
        """)
        low_stock = cursor.fetchone()
        
        # Pending job orders from D10
        cursor.execute("""
            SELECT COUNT(*) as pending_jobs
            FROM job_orders
            WHERE status = 'pending'
        """)
        pending_jobs = cursor.fetchone()
        
        # Today's pending jobs (received today not started)
        cursor.execute("""
            SELECT COUNT(*) as today_pending_jobs
            FROM job_orders
            WHERE DATE(receive_date) = %s AND status = 'pending'
        """, (today,))
        today_pending = cursor.fetchone()
        
        return {
            "today_revenue": float(today_stats.get('today_revenue', 0) or 0),
            "today_invoices": today_stats.get('today_invoices', 0) or 0,
            "month_revenue": float(month_stats.get('month_revenue', 0) or 0),
            "month_invoices": month_stats.get('month_invoices', 0) or 0,
            "total_repairs": repair_stats.get('total_repairs', 0) or 0,
            "pending_repairs": repair_stats.get('pending_repairs', 0) or 0,
            "working_repairs": repair_stats.get('working_repairs', 0) or 0,
            "completed_repairs": repair_stats.get('completed_repairs', 0) or 0,
            "waiting_repairs": repair_stats.get('waiting_repairs', 0) or 0,
            "low_stock_count": low_stock.get('low_stock_count', 0) or 0,
            "pending_jobs": pending_jobs.get('pending_jobs', 0) or 0,
            "today_pending_jobs": today_pending.get('today_pending_jobs', 0) or 0
        }
    except Exception as e:
        print(f"Error in dashboard summary: {e}")
        import traceback
        traceback.print_exc()
        return {}
    finally:
        cursor.close()
        db.close()


# ========== Services and Spare Parts Sales Report (ລາຍງານຍອດຂາຍບໍລິການ ແລະ ອາໄຫຼ່) ==========
@router.get("/reports/parts-service-sales")
def get_parts_service_sales_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
        # 1. Services Sales Breakdown from approved quotations
        cursor.execute("""
            SELECT 
                COALESCE(s.name, qi.custom_name) as service_name,
                SUM(qi.qty) as quantity_sold,
                AVG(qi.unit_price) as avg_unit_price,
                SUM(qi.total) as total_sales_amount
            FROM quotation_items qi
            LEFT JOIN services s ON qi.service_id = s.id
            LEFT JOIN quotations q ON qi.quotation_id = q.id
            WHERE (qi.service_id IS NOT NULL OR (qi.service_id IS NULL AND qi.part_id IS NULL AND qi.custom_name IS NOT NULL))
            AND q.status = 'approved'
            AND DATE(q.created_at) BETWEEN %s AND %s
            GROUP BY qi.service_id, qi.custom_name, s.name
            ORDER BY total_sales_amount DESC
        """, (start_date, end_date))
        service_sales = cursor.fetchall()
        
        # 2. Spare Parts Sales Breakdown from approved quotations
        cursor.execute("""
            SELECT 
                p.name as part_name,
                COALESCE(c.name, 'ບໍ່ມີປະເພດ') as category_name,
                p.stock_qty as current_stock,
                u.name as unit_name,
                SUM(qi.qty) as quantity_sold,
                AVG(qi.unit_price) as avg_unit_price,
                SUM(qi.total) as total_sales_amount,
                SUM(qi.qty * p.cost_price) as total_cost_amount,
                SUM(qi.total - (qi.qty * p.cost_price)) as profit
            FROM quotation_items qi
            LEFT JOIN parts p ON qi.part_id = p.id
            LEFT JOIN Part_Categories c ON p.category_id = c.id
            LEFT JOIN Units u ON p.unit_id = u.id
            LEFT JOIN quotations q ON qi.quotation_id = q.id
            WHERE qi.part_id IS NOT NULL AND q.status = 'approved'
            AND DATE(q.created_at) BETWEEN %s AND %s
            GROUP BY p.id, p.name, c.name, u.name, p.stock_qty
            ORDER BY total_sales_amount DESC
        """, (start_date, end_date))
        parts_sales = cursor.fetchall()
        
        # Calculate summary totals
        total_service_sales = sum([float(x['total_sales_amount'] or 0) for x in service_sales])
        total_parts_sales = sum([float(x['total_sales_amount'] or 0) for x in parts_sales])
        total_parts_cost = sum([float(x['total_cost_amount'] or 0) for x in parts_sales])
        total_parts_profit = sum([float(x['profit'] or 0) for x in parts_sales])
        
        # Convert decimal/float types to avoid serialization issues
        for s in service_sales:
            s['avg_unit_price'] = float(s['avg_unit_price'] or 0)
            s['total_sales_amount'] = float(s['total_sales_amount'] or 0)
            s['quantity_sold'] = int(s['quantity_sold'] or 0)
            
        for p in parts_sales:
            p['avg_unit_price'] = float(p['avg_unit_price'] or 0)
            p['total_sales_amount'] = float(p['total_sales_amount'] or 0)
            p['total_cost_amount'] = float(p['total_cost_amount'] or 0)
            p['profit'] = float(p['profit'] or 0)
            p['quantity_sold'] = int(p['quantity_sold'] or 0)
            p['current_stock'] = int(p['current_stock'] or 0)
            
        return {
            "summary": {
                "total_service_sales": total_service_sales,
                "total_parts_sales": total_parts_sales,
                "total_parts_cost": total_parts_cost,
                "total_parts_profit": total_parts_profit,
                "combined_sales": total_service_sales + total_parts_sales
            },
            "service_sales": service_sales,
            "parts_sales": parts_sales,
            "period": {"start_date": start_date, "end_date": end_date}
        }
    except Exception as e:
        print(f"Error in parts service sales report: {e}")
        import traceback
        traceback.print_exc()
        return {}
    finally:
        cursor.close()
        db.close()


# ========== Mechanic Performance Report (ລາຍງານປະສິດທິພາບຂອງຊ່າງ) ==========
@router.get("/reports/mechanic-performance")
def get_mechanic_performance_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
        cursor.execute("""
            SELECT 
                e.id as mechanic_id,
                e.name as mechanic_name,
                e.phone as mechanic_phone,
                e.status as mechanic_status,
                COUNT(ro.id) as total_assigned,
                SUM(CASE WHEN ro.status = 'completed' THEN 1 ELSE 0 END) as completed_count,
                SUM(CASE WHEN ro.status = 'working' THEN 1 ELSE 0 END) as working_count,
                SUM(CASE WHEN ro.status = 'paused' THEN 1 ELSE 0 END) as paused_count,
                SUM(CASE WHEN ro.status = 'waiting' THEN 1 ELSE 0 END) as waiting_count,
                ROUND(AVG(CASE WHEN ro.status = 'completed' AND ro.end_date IS NOT NULL 
                    THEN TIMESTAMPDIFF(HOUR, ro.start_date, ro.end_date) 
                    ELSE NULL END), 1) as avg_hours
            FROM Employees e
            LEFT JOIN repair_orders ro ON e.id = ro.mechanic_id AND DATE(ro.start_date) BETWEEN %s AND %s
            WHERE e.role = 'mechanic' AND e.status = 'active'
            GROUP BY e.id, e.name, e.phone, e.status
            ORDER BY completed_count DESC
        """, (start_date, end_date))
        mechanic_stats = cursor.fetchall()
        
        # Calculate totals
        total_assigned = 0
        total_completed = 0
        total_working = 0
        total_paused = 0
        total_waiting = 0
        valid_durations = []
        
        for m in mechanic_stats:
            m['total_assigned'] = int(m['total_assigned'] or 0)
            m['completed_count'] = int(m['completed_count'] or 0)
            m['working_count'] = int(m['working_count'] or 0)
            m['paused_count'] = int(m['paused_count'] or 0)
            m['waiting_count'] = int(m['waiting_count'] or 0)
            m['avg_hours'] = float(m['avg_hours'] or 0) if m['avg_hours'] is not None else None
            
            # Efficiency
            assigned = m['total_assigned']
            m['efficiency'] = round((m['completed_count'] / assigned * 100), 1) if assigned > 0 else 0
            
            total_assigned += m['total_assigned']
            total_completed += m['completed_count']
            total_working += m['working_count']
            total_paused += m['paused_count']
            total_waiting += m['waiting_count']
            if m['avg_hours'] is not None and m['avg_hours'] > 0:
                valid_durations.append(m['avg_hours'])
                
        avg_workshop_hours = round(sum(valid_durations) / len(valid_durations), 1) if valid_durations else 0
        
        return {
            "summary": {
                "total_mechanics": len(mechanic_stats),
                "total_assigned": total_assigned,
                "total_completed": total_completed,
                "total_working": total_working,
                "total_paused": total_paused,
                "total_waiting": total_waiting,
                "avg_workshop_hours": avg_workshop_hours
            },
            "mechanic_stats": mechanic_stats,
            "period": {"start_date": start_date, "end_date": end_date}
        }
    except Exception as e:
        print(f"Error in mechanic performance report: {e}")
        import traceback
        traceback.print_exc()
        return {}
    finally:
        cursor.close()
        db.close()


# ========== 5 SPECIALIZED REPORTS PDF STREAMING ENDPOINTS ==========

from fastapi import Response
from utils_pdf import (
    generate_revenue_report_pdf,
    generate_repair_summary_pdf,
    generate_parts_service_sales_pdf,
    generate_mechanic_performance_pdf,
    generate_promotion_usage_pdf
)

@router.get("/reports/revenue/pdf")
def get_revenue_report_pdf(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    try:
        pdf_bytes = generate_revenue_report_pdf(start_date, end_date)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=revenue_report_{start_date}_to_{end_date}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/repair-summary/pdf")
def get_repair_summary_report_pdf(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    try:
        pdf_bytes = generate_repair_summary_pdf(start_date, end_date)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=repair_summary_report_{start_date}_to_{end_date}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/parts-service-sales/pdf")
def get_parts_service_sales_report_pdf(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    try:
        pdf_bytes = generate_parts_service_sales_pdf(start_date, end_date)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=parts_service_sales_report_{start_date}_to_{end_date}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/mechanic-performance/pdf")
def get_mechanic_performance_report_pdf(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    try:
        pdf_bytes = generate_mechanic_performance_pdf(start_date, end_date)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=mechanic_performance_report_{start_date}_to_{end_date}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/promotion-usage/pdf")
def get_promotion_usage_report_pdf(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    try:
        pdf_bytes = generate_promotion_usage_pdf(start_date, end_date)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=promotion_usage_report_{start_date}_to_{end_date}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))