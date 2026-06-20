# backend/utils_pdf.py
import os
import io
from fastapi import HTTPException
from database import get_db

# ReportLab imports
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# Find and register Phetsarath font for Lao script support
FONT_NAME = 'Phetsarath'
base_dir = os.path.dirname(os.path.abspath(__file__))
font_paths = [
    os.path.join(base_dir, "assets", "fonts", "Phetsarath.ttf"),
    os.path.join(base_dir, "..", "frontend", "assets", "fonts", "Phetsarath.ttf"),
    os.path.join(base_dir, "routers", "..", "assets", "fonts", "Phetsarath.ttf"),
    "assets/fonts/Phetsarath.ttf",
    "../assets/fonts/Phetsarath.ttf"
]

font_path = None
for path in font_paths:
    if os.path.exists(path):
        font_path = path
        break

if font_path:
    try:
        pdfmetrics.registerFont(TTFont(FONT_NAME, font_path))
        print(f"DEBUG: Registered Lao font Phetsarath successfully from {font_path}")
    except Exception as e:
        print(f"ERROR: Failed to register font Phetsarath: {e}")
        FONT_NAME = 'Helvetica'
else:
    print("WARNING: Phetsarath.ttf not found. Falling back to Helvetica.")
    FONT_NAME = 'Helvetica'


class NumberedCanvas(canvas.Canvas):
    """Canvas subclass to handle bottom header lines and two-pass page numbering (Page X of Y)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont(FONT_NAME, 8)
        self.setFillColor(colors.HexColor('#64748B'))
        
        # Draw a thin horizontal divider line just above the page footer
        self.setStrokeColor(colors.HexColor('#CBD5E1'))
        self.setLineWidth(0.5)
        self.line(36, 35, 559, 35)
        
        # Right aligned page number in Lao
        page_text = f"ໜ້າ {self._pageNumber} / {page_count}"
        self.drawRightString(559, 22, page_text)
        
        # Left aligned document info in Lao
        self.drawString(36, 22, "J&P Auto Maxing — ໃບສັ່ງງານຊ່ອມແປງ (Repair Work Order)")
        self.restoreState()


def generate_repair_work_order_pdf(repair_id: int) -> bytes:
    """Queries repair order information and generates an A4 PDF work order for mechanics."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # 1. Fetch repair order details and associated job order, customer, vehicle, brand, and mechanic
        cursor.execute("""
            SELECT ro.*, 
                   jo.job_no, jo.problem_description, jo.mileage, jo.fuel_level,
                   c.name as customer_name, c.phone as customer_phone, c.address as customer_address,
                   v.plate_number, b.name as brand, v.model, v.year, v.color,
                   e.name as mechanic_name
            FROM repair_orders ro
            LEFT JOIN job_orders jo ON ro.job_order_id = jo.id
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            LEFT JOIN Employees e ON ro.mechanic_id = e.id
            WHERE ro.id = %s
        """, (repair_id,))
        repair = cursor.fetchone()
        
        if not repair:
            raise HTTPException(status_code=404, detail=f"Repair order ID {repair_id} not found")

        # 2. Fetch shop information
        cursor.execute("SELECT name, address, phone FROM Shop LIMIT 1")
        shop = cursor.fetchone()
        if not shop:
            shop = {
                "name": "J&P Auto Maxing",
                "address": "ນະຄອນຫຼວງວຽງຈັນ (Vientiane, Laos)",
                "phone": "020 22224444"
            }

        # 3. Fetch approved quotation for this job order
        cursor.execute("""
            SELECT id FROM quotations 
            WHERE job_order_id = %s AND status = 'approved' 
            LIMIT 1
        """, (repair["job_order_id"],))
        quotation = cursor.fetchone()
        
        quotation_items = []
        if quotation:
            cursor.execute("""
                SELECT qi.id, qi.quotation_id, qi.part_id, qi.service_id, qi.qty, qi.unit_price, qi.discount_amount, qi.total,
                       CASE
                           WHEN qi.part_id IS NOT NULL THEN 'part'
                           WHEN qi.service_id IS NOT NULL THEN 'service'
                           ELSE 'custom'
                       END AS item_type,
                       COALESCE(p.name, s.name, qi.custom_name) AS name,
                       u.name as unit_name
                FROM quotation_items qi
                LEFT JOIN parts p ON qi.part_id = p.id
                LEFT JOIN units u ON p.unit_id = u.id
                LEFT JOIN services s ON qi.service_id = s.id
                WHERE qi.quotation_id = %s
                ORDER BY qi.id
            """, (quotation["id"],))
            quotation_items = cursor.fetchall()

        # 4. Fetch actual parts withdrawn (parts_usage)
        cursor.execute("""
            SELECT pu.*, p.name as part_name, u.name as unit_name
            FROM parts_usage pu
            LEFT JOIN parts p ON pu.part_id = p.id
            LEFT JOIN units u ON p.unit_id = u.id
            WHERE pu.repair_id = %s
            ORDER BY pu.id
        """, (repair_id,))
        parts_usage = cursor.fetchall()

    except Exception as ex:
        print(f"Error querying data for PDF: {ex}")
        raise HTTPException(status_code=500, detail=f"Database query error: {str(ex)}")
    finally:
        cursor.close()
        db.close()

    # 5. Build ReportLab PDF flowables
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=54 # extra space at bottom for footer canvas
    )

    # Styles
    styles = getSampleStyleSheet()
    
    # Modify default style to support Phetsarath font
    normal_style = styles['Normal']
    normal_style.fontName = FONT_NAME
    normal_style.fontSize = 10
    normal_style.leading = 14

    title_style = ParagraphStyle(
        'DocTitle',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=18,
        leading=22,
        alignment=2, # Right aligned
        textColor=colors.HexColor('#0D47A1')
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=9,
        leading=11,
        alignment=2, # Right aligned
        textColor=colors.HexColor('#64748B')
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0D47A1'),
        spaceBefore=12,
        spaceAfter=4,
        keepWithNext=True
    )

    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#475569')
    )

    meta_value_style = ParagraphStyle(
        'MetaValue',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=1 # Center
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    table_cell_center_style = ParagraphStyle(
        'TableCellCenter',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155'),
        alignment=1 # Center
    )

    story = []

    # A. PDF Header Table (Company info on left, document metadata on right)
    shop_name = shop.get('name', 'J&P Auto Maxing')
    shop_address = shop.get('address', '')
    shop_phone = shop.get('phone', '')

    ro_no = f"R{repair.get('id', 0):04d}"
    created_date = repair.get('start_date')
    if created_date:
        if isinstance(created_date, str):
            if len(created_date) > 10:
                created_date = created_date[:10]
        else:
            try:
                created_date = created_date.strftime("%Y-%m-%d")
            except:
                created_date = str(created_date)[:10]
    else:
        created_date = '-'
    job_no = repair.get('job_no', '-')
    status = repair.get('status', 'waiting')
    
    status_translations = {
        "waiting": "ລໍຖ້າຊ່ອມ (Waiting)",
        "working": "ກຳລັງສ້ອມແປງ (Working)",
        "paused": "ຢຸດຊົ່ວຄາວ (Paused)",
        "completed": "ສຳເລັດແລ້ວ (Completed)"
    }
    status_text = status_translations.get(status, status)

    meta_box_data = [
        [Paragraph("<b>ເລກທີໃບສັ່ງຊ່ອມ / RO No:</b>", meta_label_style), Paragraph(f"<b>{ro_no}</b>", meta_value_style)],
        [Paragraph("<b>ວັນທີ / Date:</b>", meta_label_style), Paragraph(created_date, meta_value_style)],
        [Paragraph("<b>ເລກທີໃບຮັບລົດ / Job No:</b>", meta_label_style), Paragraph(job_no, meta_value_style)],
        [Paragraph("<b>ສະຖານະ / Status:</b>", meta_label_style), Paragraph(status_text, meta_value_style)]
    ]
    meta_table = Table(meta_box_data, colWidths=[110, 100])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#0D47A1')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))

    header_left = Paragraph(
        f"<font size=16 color='#0D47A1'><b>{shop_name}</b></font><br/>"
        f"<font size=9 color='#475569'>{shop_address}<br/>"
        f"ເບີໂທລະສັບ / Phone: {shop_phone}</font>",
        normal_style
    )

    header_right = [
        Paragraph("<b>ໃບສັ່ງງານຊ່ອມແປງ</b>", title_style),
        Paragraph("REPAIR WORK ORDER", subtitle_style),
        Spacer(1, 6),
        meta_table
    ]

    header_table = Table([[header_left, header_right]], colWidths=[300, 220])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)

    # B. Divider line
    divider = Table([[""]], colWidths=[520])
    divider.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 1.5, colors.HexColor('#0D47A1')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(divider)

    # C. Section 1: Customer & Vehicle Info
    customer_name = repair.get('customer_name', '-')
    customer_phone = repair.get('customer_phone', '-')
    plate_number = repair.get('plate_number', '-')
    brand = repair.get('brand', '-')
    model = repair.get('model', '-')
    year = repair.get('year', '')
    color = repair.get('color', '-')
    mechanic_name = repair.get('mechanic_name', 'ຍັງບໍ່ໄດ້ມອບໝາຍ (Unassigned)')
    
    mileage = repair.get('mileage', '-')
    if mileage is not None and mileage != '-':
        try:
            mileage_text = f"{int(mileage):,} km"
        except:
            mileage_text = f"{mileage} km"
    else:
        mileage_text = "-"
        
    fuel_level = repair.get('fuel_level', '-')
    if not fuel_level:
        fuel_level = "-"

    info_data = [
        [
            Paragraph("<b>ຊື່ລູກຄ້າ / Customer:</b>", meta_label_style), Paragraph(customer_name, meta_value_style),
            Paragraph("<b>ທະບຽນລົດ / Plate No:</b>", meta_label_style), Paragraph(f"<b>{plate_number}</b>", meta_value_style)
        ],
        [
            Paragraph("<b>ເບີໂທ / Phone No:</b>", meta_label_style), Paragraph(customer_phone, meta_value_style),
            Paragraph("<b>ຍີ່ຫໍ້ & ລຸ້ນ / Brand & Model:</b>", meta_label_style), Paragraph(f"{brand} {model} {f'({year})' if year else ''}", meta_value_style)
        ],
        [
            Paragraph("<b>ຊ່າງຮັບຜິດຊອບ / Mechanic:</b>", meta_label_style), Paragraph(f"<b>{mechanic_name}</b>", meta_value_style),
            Paragraph("<b>ສີລົດ / Color:</b>", meta_label_style), Paragraph(color, meta_value_style)
        ],
        [
            Paragraph("<b>ໄລຍະທາງ / Mileage:</b>", meta_label_style), Paragraph(mileage_text, meta_value_style),
            Paragraph("<b>ລະດັບນໍ້າມັນ / Fuel Level:</b>", meta_label_style), Paragraph(fuel_level, meta_value_style)
        ]
    ]
    info_table = Table(info_data, colWidths=[110, 150, 110, 150])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#F1F5F9')),
    ]))
    
    story.append(Paragraph("<b>ຂໍ້ມູນລູກຄ້າ ແລະ ພາຫະນະ / Customer & Vehicle Info</b>", section_header_style))
    story.append(info_table)
    story.append(Spacer(1, 8))

    # D. Section 2: Problem Description
    problem = repair.get('problem_description', '-')
    if problem:
        problem = problem.replace('\n', '<br/>')
    problem_box_data = [
        [Paragraph("<b>ອາການເສຍ ແລະ ບັນຫາທີ່ແຈ້ງຊ່ອມ / Symptoms & Problems Reported:</b>", meta_label_style)],
        [Paragraph(problem if problem else 'ບໍ່ມີຂໍ້ມູນ (No description)', meta_value_style)]
    ]
    problem_table = Table(problem_box_data, colWidths=[520])
    problem_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(problem_table)
    story.append(Spacer(1, 8))

    # E. Section 3: Repair Tasks / Services Table
    services_data = [
        [
            Paragraph("<b>ລຳດັບ<br/>No.</b>", table_header_style),
            Paragraph("<b>ລາຍການບໍລິການ ແລະ ໜ້າວຽກຊ່ອມແປງ<br/>Task / Service Description</b>", table_header_style),
            Paragraph("<b>ສະຖານະໜ້າວຽກ<br/>Work Status Checklist</b>", table_header_style),
            Paragraph("<b>ບັນທຶກຂອງຊ່າງ / ໝາຍເຫດ<br/>Mechanic Remarks</b>", table_header_style)
        ]
    ]

    service_index = 1
    for item in quotation_items:
        if item.get('item_type') in ('service', 'custom'):
            task_name = item.get('name', '-')
            services_data.append([
                Paragraph(str(service_index), table_cell_center_style),
                Paragraph(task_name, table_cell_style),
                Paragraph("[  ] ລໍຖ້າ (Pending)  [  ] ກຳລັງເຮັດ (Active)  [  ] ສຳເລັດ (Done)", table_cell_style),
                Paragraph("", table_cell_style)
            ])
            service_index += 1

    if service_index == 1:
        services_data.append([
            Paragraph("-", table_cell_center_style),
            Paragraph("ບໍ່ມີລາຍການບໍລິການ/ໜ້າວຽກ (No service tasks assigned)", table_cell_style),
            Paragraph("-", table_cell_center_style),
            Paragraph("-", table_cell_center_style)
        ])

    services_table = Table(services_data, colWidths=[35, 205, 150, 130])
    services_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))

    story.append(Paragraph("<b>ລາຍການໜ້າວຽກບໍລິການ / Service Tasks to Perform</b>", section_header_style))
    story.append(services_table)
    story.append(Spacer(1, 8))

    # F. Section 4: Spare Parts Table (Merged planned and actual withdrawn)
    parts_merged = {}
    for item in quotation_items:
        if item.get('item_type') == 'part':
            part_id = item.get('part_id')
            parts_merged[part_id] = {
                'name': item.get('name', '-'),
                'approved_qty': item.get('qty', 0),
                'withdrawn_qty': 0,
                'unit': item.get('unit_name') or 'ລາຍການ'
            }

    for usage in parts_usage:
        part_id = usage.get('part_id')
        qty = usage.get('qty', 0)
        if part_id in parts_merged:
            parts_merged[part_id]['withdrawn_qty'] += qty
        else:
            # Unplanned part withdrawn!
            parts_merged[part_id] = {
                'name': usage.get('part_name', '-'),
                'approved_qty': 0,
                'withdrawn_qty': qty,
                'unit': usage.get('unit_name') or 'ລາຍການ'
            }

    parts_data = [
        [
            Paragraph("<b>ລຳດັບ<br/>No.</b>", table_header_style),
            Paragraph("<b>ຊື່ອາໄຫຼ່ ແລະ ອຸປະກອນ<br/>Spare Part Name & Description</b>", table_header_style),
            Paragraph("<b>ອະນຸມັດ<br/>Appr Qty</b>", table_header_style),
            Paragraph("<b>ເບີກຕົວຈິງ<br/>Withd Qty</b>", table_header_style),
            Paragraph("<b>ຫົວໜ່ວຍ<br/>Unit</b>", table_header_style),
            Paragraph("<b>ສະຖານະ / ໝາຍເຫດ<br/>Withdrawal Status</b>", table_header_style)
        ]
    ]

    part_index = 1
    for part_id, p_info in parts_merged.items():
        approved_qty = p_info['approved_qty']
        withdrawn_qty = p_info['withdrawn_qty']
        unit = p_info['unit']

        if approved_qty > 0 and withdrawn_qty == 0:
            status_note = "ລໍຖ້າເບີກ (Pending)"
        elif approved_qty == withdrawn_qty and approved_qty > 0:
            status_note = "ເບີກຄົບຖ້ວນ (Issued)"
        elif approved_qty > withdrawn_qty and withdrawn_qty > 0:
            status_note = f"ເບີກບາງສ່ວນ ({int(withdrawn_qty)}/{int(approved_qty)})"
        elif withdrawn_qty > approved_qty and approved_qty > 0:
            status_note = f"ເບີກເກີນ (+{int(withdrawn_qty - approved_qty)})"
        else:
            status_note = "ເບີກເພີ່ມ (Extra)"

        parts_data.append([
            Paragraph(str(part_index), table_cell_center_style),
            Paragraph(p_info['name'], table_cell_style),
            Paragraph(str(int(approved_qty)) if approved_qty > 0 else "-", table_cell_center_style),
            Paragraph(str(int(withdrawn_qty)) if withdrawn_qty > 0 else "-", table_cell_center_style),
            Paragraph(unit, table_cell_center_style),
            Paragraph(status_note, table_cell_style)
        ])
        part_index += 1

    if part_index == 1:
        parts_data.append([
            Paragraph("-", table_cell_center_style),
            Paragraph("ບໍ່ມີລາຍການອາໄຫຼ່ທີ່ຕ້ອງໃຊ້ (No spare parts required)", table_cell_style),
            Paragraph("-", table_cell_center_style),
            Paragraph("-", table_cell_center_style),
            Paragraph("-", table_cell_center_style),
            Paragraph("-", table_cell_center_style)
        ])

    parts_table = Table(parts_data, colWidths=[35, 195, 60, 60, 50, 120])
    parts_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))

    story.append(Paragraph("<b>ລາຍການອາໄຫຼ່ ແລະ ອຸປະກອນ / Spare Parts Required</b>", section_header_style))
    story.append(parts_table)

    # G. Keep Signatures Block together on the same page
    sig_data = [
        [
            Paragraph("<b>ຊ່າງຜູ້ຮັບຜິດຊອບສ້ອມແປງ / Assigned Mechanic</b>", meta_label_style),
            Paragraph("<b>ຫົວໜ້າຊ່າງ ຫຼື ຜູ້ກວດສອບ / Supervisor / Inspector</b>", meta_label_style)
        ],
        [
            Spacer(1, 35),
            Spacer(1, 35)
        ],
        [
            Paragraph("ລົງຊື່: ...........................................................", meta_label_style),
            Paragraph("ລົງຊື່: ...........................................................", meta_label_style)
        ],
        [
            Paragraph(f"({mechanic_name})", meta_value_style),
            Paragraph("(....................................................................)", meta_value_style)
        ],
        [
            Paragraph("ວັນທີ / Date: ...... / ...... / ............", meta_label_style),
            Paragraph("ວັນທີ / Date: ...... / ...... / ............", meta_label_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[260, 260])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))

    sig_section = KeepTogether([
        Spacer(1, 15),
        Paragraph("<b>ການຢືນຢັນການສ້ອມແປງ / Repair Work Sign-off</b>", section_header_style),
        Spacer(1, 2),
        sig_table
    ])
    story.append(sig_section)

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_content = buffer.getvalue()
    buffer.close()
    return pdf_content


def generate_job_order_pdf(order_id: int) -> bytes:
    """Queries job order information and generates an A4 PDF receipt."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Fetch job order details and associated customer and vehicle
        cursor.execute("""
            SELECT jo.*, 
                   c.name as customer_name, c.phone as customer_phone, c.address as customer_address,
                   v.plate_number, b.name as brand, v.model, v.year, v.color,
                   e.name as created_by_name
            FROM job_orders jo
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            LEFT JOIN employees e ON jo.created_by = e.id
            WHERE jo.id = %s
        """, (order_id,))
        order = cursor.fetchone()
        
        if not order:
            raise HTTPException(status_code=404, detail=f"Job order ID {order_id} not found")

        # Fetch shop information
        cursor.execute("SELECT name, address, phone FROM Shop LIMIT 1")
        shop = cursor.fetchone()
        if not shop:
            shop = {
                "name": "J&P Auto Maxing",
                "address": "ນະຄອນຫຼວງວຽງຈັນ (Vientiane, Laos)",
                "phone": "020 22224444"
            }
            
    except Exception as ex:
        print(f"Error querying data for PDF: {ex}")
        raise HTTPException(status_code=500, detail=f"Database query error: {str(ex)}")
    finally:
        cursor.close()
        db.close()

    # Build ReportLab PDF flowables
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=54 # extra space at bottom for footer canvas
    )

    # Styles
    styles = getSampleStyleSheet()
    
    # Modify default style to support Phetsarath font
    normal_style = styles['Normal']
    normal_style.fontName = FONT_NAME
    normal_style.fontSize = 10
    normal_style.leading = 14

    title_style = ParagraphStyle(
        'DocTitle',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=18,
        leading=22,
        alignment=2, # Right aligned
        textColor=colors.HexColor('#0D47A1')
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=9,
        leading=11,
        alignment=2, # Right aligned
        textColor=colors.HexColor('#64748B')
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0D47A1'),
        spaceBefore=12,
        spaceAfter=4,
        keepWithNext=True
    )

    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#475569')
    )

    meta_value_style = ParagraphStyle(
        'MetaValue',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )

    story = []

    # A. PDF Header Table (Company info on left, document metadata on right)
    shop_name = shop.get('name', 'J&P Auto Maxing')
    shop_address = shop.get('address', '')
    shop_phone = shop.get('phone', '')

    job_no = order.get('job_no', '-')
    
    receive_date = order.get('receive_date')
    if receive_date:
        if isinstance(receive_date, str):
            receive_date_str = receive_date
        else:
            try:
                receive_date_str = receive_date.strftime("%d/%m/%Y %H:%M")
            except:
                receive_date_str = str(receive_date)
    else:
        receive_date_str = '-'
        
    status = order.get('status', 'pending')
    status_translations = {
        "pending": "ລໍຖ້າກວດເຊັກ (Pending)",
        "diagnosed": "ກວດເຊັກແລ້ວ (Diagnosed)",
        "repairing": "ກຳລັງສ້ອມແປງ (Repairing)",
        "finished": "ສຳເລັດແລ້ວ (Finished)",
        "closed": "ປິດວຽກແລ້ວ (Closed)"
    }
    status_text = status_translations.get(status, status)

    meta_box_data = [
        [Paragraph("<b>ເລກທີໃບຮັບລົດ / Job No:</b>", meta_label_style), Paragraph(f"<b>{job_no}</b>", meta_value_style)],
        [Paragraph("<b>ວັນທີ / Date:</b>", meta_label_style), Paragraph(receive_date_str, meta_value_style)],
        [Paragraph("<b>ສະຖານະ / Status:</b>", meta_label_style), Paragraph(status_text, meta_value_style)]
    ]
    meta_table = Table(meta_box_data, colWidths=[110, 100])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#0D47A1')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))

    header_left = Paragraph(
        f"<font size=16 color='#0D47A1'><b>{shop_name}</b></font><br/>"
        f"<font size=9 color='#475569'>{shop_address}<br/>"
        f"ເບີໂທລະສັບ / Phone: {shop_phone}</font>",
        normal_style
    )

    header_right = [
        Paragraph("<b>ໃບຮັບລົດ</b>", title_style),
        Paragraph("JOB ORDER RECEIPT", subtitle_style),
        Spacer(1, 6),
        meta_table
    ]

    header_table = Table([[header_left, header_right]], colWidths=[300, 220])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)

    # B. Divider line
    divider = Table([[""]], colWidths=[520])
    divider.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 1.5, colors.HexColor('#0D47A1')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(divider)

    # C. Customer & Vehicle Info Section
    customer_name = order.get('customer_name', '-')
    customer_phone = order.get('customer_phone', '-')
    customer_address = order.get('customer_address', '-')
    
    plate_number = order.get('plate_number', '-')
    brand = order.get('brand', '-')
    model = order.get('model', '-')
    year = order.get('year', '')
    color = order.get('color', '-')
    mileage = order.get('mileage', 0)
    fuel_level = order.get('fuel_level', '-')
    
    created_by_name = order.get('created_by_name', '-')

    left_info = [
        [Paragraph("<b>ຂໍ້ມູນລູກຄ້າ / Customer Info</b>", section_header_style), ""],
        [Paragraph("<b>ຊື່ລູກຄ້າ / Name:</b>", meta_label_style), Paragraph(customer_name, meta_value_style)],
        [Paragraph("<b>ເບີໂທລະສັບ / Phone:</b>", meta_label_style), Paragraph(customer_phone, meta_value_style)],
        [Paragraph("<b>ທີ່ຢູ່ / Address:</b>", meta_label_style), Paragraph(customer_address, meta_value_style)]
    ]
    left_table = Table(left_info, colWidths=[100, 150])
    left_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('SPAN', (0, 0), (1, 0)),
    ]))

    right_info = [
        [Paragraph("<b>...</b>", meta_label_style)]  # Placeholder to prevent empty column layout warning
    ]
    
    right_info = [
        [Paragraph("<b>ຂໍ້ມູນລົດ / Vehicle Info</b>", section_header_style), ""],
        [Paragraph("<b>ທະບຽນລົດ / Plate No:</b>", meta_label_style), Paragraph(plate_number, meta_value_style)],
        [Paragraph("<b>ຍີ່ຫໍ້ ແລະ ລຸ້ນ / Model:</b>", meta_label_style), Paragraph(f"{brand} {model} {f'({year})' if year else ''}", meta_value_style)],
        [Paragraph("<b>ສີລົດ / Color:</b>", meta_label_style), Paragraph(color, meta_value_style)],
        [Paragraph("<b>ເລກກິໂລ / Mileage:</b>", meta_label_style), Paragraph(f"{mileage:,} km" if mileage else "-", meta_value_style)],
        [Paragraph("<b>ລະດັບນ້ຳມັນ / Fuel Level:</b>", meta_label_style), Paragraph(fuel_level, meta_value_style)]
    ]
    right_table = Table(right_info, colWidths=[110, 140])
    right_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('SPAN', (0, 0), (1, 0)),
    ]))

    info_layout_table = Table([[left_table, right_table]], colWidths=[260, 260])
    info_layout_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(info_layout_table)
    story.append(Spacer(1, 10))

    # D. Problem Description Section
    problem = order.get('problem_description', '-')
    
    problem_style = ParagraphStyle(
        'ProblemStyle',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1E293B')
    )
    
    problem_data = [
        [Paragraph("<b>ອາການລົດ ຫຼື ບັນຫາທີ່ແຈ້ງຊ່ອມ / Problem & Symptoms Reported:</b>", section_header_style)],
        [Paragraph(problem, problem_style)]
    ]
    problem_table = Table(problem_data, colWidths=[520])
    problem_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(problem_table)
    story.append(Spacer(1, 20))

    # E. Signatures Block
    sig_data = [
        [
            Paragraph("<b>ລູກຄ້າຜູ້ແຈ້ງຊ່ອມ / Customer Signature</b>", meta_label_style),
            Paragraph("<b>ພະນັກງານຕ້ອນຮັບ / Service Advisor</b>", meta_label_style)
        ],
        [
            Spacer(1, 40),
            Spacer(1, 40)
        ],
        [
            Paragraph("ລົງຊື່: ...........................................................", meta_label_style),
            Paragraph("ລົງຊື່: ...........................................................", meta_label_style)
        ],
        [
            Paragraph(f"({customer_name})", meta_value_style),
            Paragraph(f"({created_by_name})", meta_value_style)
        ],
        [
            Paragraph("ວັນທີ / Date: ...... / ...... / ............", meta_label_style),
            Paragraph("ວັນທີ / Date: ...... / ...... / ............", meta_label_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[260, 260])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))

    sig_section = KeepTogether([
        Paragraph("<b>ການຢືນຢັນ ແລະ ມອບຮັບລົດ / Authorization & Sign-off</b>", section_header_style),
        Spacer(1, 6),
        sig_table
    ])
    story.append(sig_section)

    # Build the document
    doc.build(story, canvasmaker=create_canvas_class("ໃบຮັບລົດ (Job Order Receipt)"))
    pdf_content = buffer.getvalue()
    buffer.close()
    return pdf_content


def generate_quotation_pdf(quotation_id: int) -> bytes:
    """Queries quotation information and generates a formal A4 PDF quotation."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Fetch quotation details and associated job order, customer, vehicle, brand, etc.
        cursor.execute("""
            SELECT q.*, 
                   jo.job_no, jo.problem_description, jo.mileage, jo.fuel_level,
                   c.name as customer_name, c.phone as customer_phone, c.address as customer_address,
                   v.plate_number, b.name as brand, v.model, v.year, v.color,
                   e.name as created_by_name, app.name as approved_by_name
            FROM quotations q
            LEFT JOIN job_orders jo ON q.job_order_id = jo.id
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            LEFT JOIN employees e ON q.created_by = e.id
            LEFT JOIN employees app ON q.approved_by = app.id
            WHERE q.id = %s
        """, (quotation_id,))
        quotation = cursor.fetchone()
        
        if not quotation:
            raise HTTPException(status_code=404, detail=f"Quotation ID {quotation_id} not found")

        # Fetch shop information
        cursor.execute("SELECT name, address, phone FROM Shop LIMIT 1")
        shop = cursor.fetchone()
        if not shop:
            shop = {
                "name": "J&P Auto Maxing",
                "address": "ນະຄອນຫຼວງວຽງຈັນ (Vientiane, Laos)",
                "phone": "020 22224444"
            }

        # Fetch items
        cursor.execute("""
            SELECT qi.id, qi.quotation_id, qi.part_id, qi.service_id, qi.qty, qi.unit_price, qi.discount_amount, qi.total,
                   CASE
                       WHEN qi.part_id IS NOT NULL THEN 'part'
                       WHEN qi.service_id IS NOT NULL THEN 'service'
                       ELSE 'custom'
                   END AS item_type,
                   COALESCE(p.name, s.name, qi.custom_name) AS name,
                   u.name as unit_name
            FROM quotation_items qi
            LEFT JOIN parts p ON qi.part_id = p.id
            LEFT JOIN units u ON p.unit_id = u.id
            LEFT JOIN services s ON qi.service_id = s.id
            WHERE qi.quotation_id = %s
            ORDER BY qi.id
        """, (quotation_id,))
        items = cursor.fetchall()

    except Exception as ex:
        print(f"Error querying data for PDF: {ex}")
        raise HTTPException(status_code=500, detail=f"Database query error: {str(ex)}")
    finally:
        cursor.close()
        db.close()

    # Build ReportLab PDF flowables
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=54 # extra space at bottom for footer canvas
    )

    # Styles
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    normal_style.fontName = FONT_NAME
    normal_style.fontSize = 10
    normal_style.leading = 14

    title_style = ParagraphStyle(
        'DocTitle',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=18,
        leading=22,
        alignment=2, # Right aligned
        textColor=colors.HexColor('#0D47A1')
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=9,
        leading=11,
        alignment=2, # Right aligned
        textColor=colors.HexColor('#64748B')
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0D47A1'),
        spaceBefore=12,
        spaceAfter=4,
        keepWithNext=True
    )

    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#475569')
    )

    meta_value_style = ParagraphStyle(
        'MetaValue',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=1 # Center aligned
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=normal_style,
        fontName=FONT_NAME,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1E293B')
    )

    table_cell_right_style = ParagraphStyle(
        'TableCellRight',
        parent=table_cell_style,
        alignment=2 # Right aligned
    )

    table_cell_center_style = ParagraphStyle(
        'TableCellCenter',
        parent=table_cell_style,
        alignment=1 # Center aligned
    )

    story = []

    # A. PDF Header Table
    shop_name = shop.get('name', 'J&P Auto Maxing')
    shop_address = shop.get('address', '')
    shop_phone = shop.get('phone', '')

    quotation_no = f"QT-{quotation['id']:04d}"
    
    from datetime import datetime
    created_at = quotation.get('created_at')
    if created_at:
        if isinstance(created_at, str):
            created_at_str = created_at
            try:
                dt = datetime.strptime(created_at[:19], "%Y-%m-%d %H:%M:%S")
                created_at_str = dt.strftime("%d/%m/%Y")
            except:
                pass
        else:
            try:
                created_at_str = created_at.strftime("%d/%m/%Y")
            except:
                created_at_str = str(created_at)
    else:
        created_at_str = '-'
        
    status = quotation.get('status', 'draft')
    status_translations = {
        "draft": "ສະເໜີລາຄາ (Draft)",
        "approved": "ອະນຸມັດແລ້ວ (Approved)",
        "rejected": "ປະຕິເສດ (Rejected)"
    }
    status_text = status_translations.get(status, status)

    meta_box_data = [
        [Paragraph("<b>ເລກທີໃບສະເໜີ / Quotation No:</b>", meta_label_style), Paragraph(f"<b>{quotation_no}</b>", meta_value_style)],
        [Paragraph("<b>ວັນທີ / Date:</b>", meta_label_style), Paragraph(created_at_str, meta_value_style)],
        [Paragraph("<b>ສະຖານະ / Status:</b>", meta_label_style), Paragraph(status_text, meta_value_style)]
    ]
    meta_table = Table(meta_box_data, colWidths=[130, 90])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#0D47A1')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))

    header_left = Paragraph(
        f"<font size=16 color='#0D47A1'><b>{shop_name}</b></font><br/>"
        f"<font size=9 color='#475569'>{shop_address}<br/>"
        f"ເບີໂທລະສັບ / Phone: {shop_phone}</font>",
        normal_style
    )

    header_right = [
        Paragraph("<b>ໃບສະເໜີລາຄາ</b>", title_style),
        Paragraph("QUOTATION", subtitle_style),
        Spacer(1, 6),
        meta_table
    ]

    header_table = Table([[header_left, header_right]], colWidths=[300, 220])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)

    # B. Divider line
    divider = Table([[""]], colWidths=[520])
    divider.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 1.5, colors.HexColor('#0D47A1')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(divider)

    # C. Customer & Vehicle Info Section
    customer_name = quotation.get('customer_name', '-')
    customer_phone = quotation.get('customer_phone', '-')
    customer_address = quotation.get('customer_address', '-')
    
    plate_number = quotation.get('plate_number', '-')
    brand = quotation.get('brand', '-')
    model = quotation.get('model', '-')
    year = quotation.get('year', '')
    color = quotation.get('color', '-')
    mileage = quotation.get('mileage', 0)
    job_no = quotation.get('job_no', '-')

    left_info = [
        [Paragraph("<b>ຂໍ້ມູນລູກຄ້າ / Customer Info</b>", section_header_style), ""],
        [Paragraph("<b>ຊື່ລູກຄ້າ / Name:</b>", meta_label_style), Paragraph(customer_name, meta_value_style)],
        [Paragraph("<b>ເບີໂທລະສັບ / Phone:</b>", meta_label_style), Paragraph(customer_phone, meta_value_style)],
        [Paragraph("<b>ທີ່ຢູ່ / Address:</b>", meta_label_style), Paragraph(customer_address, meta_value_style)]
    ]
    left_table = Table(left_info, colWidths=[100, 150])
    left_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('SPAN', (0, 0), (1, 0)),
    ]))

    right_info = [
        [Paragraph("<b>ຂໍ້ມູນລົດ / Vehicle Info</b>", section_header_style), ""],
        [Paragraph("<b>ທະບຽນລົດ / Plate No:</b>", meta_label_style), Paragraph(plate_number, meta_value_style)],
        [Paragraph("<b>ຍີ່ຫໍ້ ແລະ ລຸ້ນ / Model:</b>", meta_label_style), Paragraph(f"{brand} {model} {f'({year})' if year else ''}", meta_value_style)],
        [Paragraph("<b>ເລກກິໂລ / Mileage:</b>", meta_label_style), Paragraph(f"{mileage:,} km" if mileage else "-", meta_value_style)],
        [Paragraph("<b>ເລກໃບຮັບລົດ / Job No:</b>", meta_label_style), Paragraph(job_no, meta_value_style)]
    ]
    right_table = Table(right_info, colWidths=[110, 140])
    right_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('SPAN', (0, 0), (1, 0)),
    ]))

    info_layout_table = Table([[left_table, right_table]], colWidths=[260, 260])
    info_layout_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(info_layout_table)
    story.append(Spacer(1, 10))

    # D. Quotation Items Table
    story.append(Paragraph("<b>ລາຍການສະເໜີລາຄາ / Quotation Items:</b>", section_header_style))
    story.append(Spacer(1, 4))

    table_data = [
        [
            Paragraph("<b>ລຳດັບ<br/>No.</b>", table_header_style),
            Paragraph("<b>...<br/>Description</b>", table_header_style), # Placeholder replaced by Lao text below
            Paragraph("<b>ຈຳນວນ<br/>Qty</b>", table_header_style),
            Paragraph("<b>ລາຄາ/หน่วย<br/>Unit Price (KIP)</b>", table_header_style),
            Paragraph("<b>ສ່ວນຫຼຸດ<br/>Discount (KIP)</b>", table_header_style),
            Paragraph("<b>ລວມ<br/>Total (KIP)</b>", table_header_style)
        ]
    ]
    # Set the headers properly
    table_data[0][1] = Paragraph("<b>ລາຍການ<br/>Description</b>", table_header_style)

    subtotal = 0.0
    total_discount = 0.0

    for idx, item in enumerate(items, 1):
        name = item.get('name', '-')
        qty = item.get('qty', 1)
        unit_price = float(item.get('unit_price', 0) or 0)
        discount_amount = float(item.get('discount_amount', 0) or 0)
        total = float(item.get('total', 0) or 0)

        subtotal += (qty * unit_price)
        total_discount += discount_amount

        table_data.append([
            Paragraph(str(idx), table_cell_center_style),
            Paragraph(name, table_cell_style),
            Paragraph(f"{qty} {item.get('unit_name') or ''}".strip(), table_cell_center_style),
            Paragraph(f"{int(unit_price):,}", table_cell_right_style),
            Paragraph(f"{int(discount_amount):,}", table_cell_right_style),
            Paragraph(f"{int(total):,}", table_cell_right_style)
        ])

    net_total = subtotal - total_discount
    if net_total < 0:
        net_total = 0.0

    items_table = Table(table_data, colWidths=[30, 210, 50, 70, 70, 90])
    
    # Grid styles
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]
    # Alternating backgrounds for data rows
    for r in range(1, len(table_data)):
        if r % 2 == 0:
            t_style.append(('BACKGROUND', (0, r), (-1, r), colors.HexColor('#F8FAFC')))
    
    items_table.setStyle(TableStyle(t_style))
    story.append(items_table)
    story.append(Spacer(1, 10))

    # E. Totals Summary Table
    totals_data = [
        ["", Paragraph("<b>ລວມຍ່ອຍ / Subtotal:</b>", table_cell_right_style), Paragraph(f"{int(subtotal):,} KIP", table_cell_right_style)],
        ["", Paragraph("<b>ສ່ວນຫຼຸດ / Discount:</b>", table_cell_right_style), Paragraph(f"{int(total_discount):,} KIP", table_cell_right_style)],
        ["", Paragraph("<font size=11 color='#0D47A1'><b>ລວມທັງໝົດ / Net Total:</b></font>", table_cell_right_style), Paragraph(f"<font size=11 color='#0D47A1'><b>{int(net_total):,} KIP</b></font>", table_cell_right_style)]
    ]
    totals_table = Table(totals_data, colWidths=[290, 140, 90])
    totals_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LINEABOVE', (1, 0), (2, 0), 0.5, colors.HexColor('#CBD5E1')),
        ('LINEBELOW', (1, -1), (2, -1), 1.5, colors.HexColor('#0D47A1')),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 20))

    # F. Signatures Block
    created_by_name = quotation.get('created_by_name', '-')
    approved_by_name = quotation.get('approved_by_name', '-')
    
    sig_data = [
        [
            Paragraph("<b>ລາຍເຊັນລູກຄ້າ / Customer Signature</b>", meta_label_style),
            Paragraph("<b>ລາຍເຊັນຮ້ານ / Shop Signature</b>", meta_label_style)
        ],
        [
            Spacer(1, 40),
            Spacer(1, 40)
        ],
        [
            Paragraph("ລົງຊື່: ...........................................................", meta_label_style),
            Paragraph("ລົງຊື່: ...........................................................", meta_label_style)
        ],
        [
            Paragraph(f"({customer_name})", meta_value_style),
            Paragraph(f"({approved_by_name if approved_by_name and approved_by_name != '-' else (created_by_name if created_by_name else '-')})", meta_value_style)
        ],
        [
            Paragraph("ວັນທີ / Date: ...... / ...... / ............", meta_label_style),
            Paragraph("ວັນທີ / Date: ...... / ...... / ............", meta_label_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[260, 260])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))

    sig_section = KeepTogether([
        sig_table
    ])
    story.append(sig_section)

    # Build the document
    doc.build(story, canvasmaker=create_canvas_class("ໃບສະເໜີລາຄາ (Quotation)"))
    pdf_content = buffer.getvalue()
    buffer.close()
    return pdf_content


# =========================================================================
# ========== 5 SPECIALIZED REPORTS PDF GENERATORS WITH LAO SUPPORT ========
# =========================================================================

from datetime import datetime, timedelta

def create_canvas_class(title_text):
    """Dynamically creates a NumberedCanvas subclass with custom document footer title."""
    class CustomNumberedCanvas(NumberedCanvas):
        def draw_page_decorations(self, page_count):
            self.saveState()
            self.setFont(FONT_NAME, 8)
            self.setFillColor(colors.HexColor('#64748B'))
            
            # Draw thin horizontal divider line just above the page footer
            self.setStrokeColor(colors.HexColor('#CBD5E1'))
            self.setLineWidth(0.5)
            self.line(36, 35, 559, 35)
            
            # Right aligned page number in Lao
            page_text = f"ໜ້າ {self._pageNumber} / {page_count}"
            self.drawRightString(559, 22, page_text)
            
            # Left aligned document info in Lao
            self.drawString(36, 22, f"J&P Auto Maxing — {title_text}")
            self.restoreState()
    return CustomNumberedCanvas


def build_report_header(story, title_lao, title_eng, start_date, end_date, shop_info):
    """Builds a consistent and formal A4 report header block with company metadata."""
    shop_name = shop_info.get('name', 'J&P Auto Maxing')
    shop_address = shop_info.get('address', '')
    shop_phone = shop_info.get('phone', '')
    
    # Base normal style to resolve Phetsarath font
    normal_style = ParagraphStyle(
        'HeaderNormal',
        fontName=FONT_NAME,
        fontSize=10,
        leading=14
    )

    title_style = ParagraphStyle(
        'DocTitle',
        parent=normal_style,
        fontSize=18,
        leading=22,
        alignment=2, # Right aligned
        textColor=colors.HexColor('#0D47A1')
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=normal_style,
        fontSize=9,
        leading=11,
        alignment=2, # Right aligned
        textColor=colors.HexColor('#64748B')
    )

    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=normal_style,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#475569')
    )

    meta_value_style = ParagraphStyle(
        'MetaValue',
        parent=normal_style,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )

    meta_box_data = [
        [Paragraph("<b>ວັນທີເລີ່ມ / Start Date:</b>", meta_label_style), Paragraph(start_date or "-", meta_value_style)],
        [Paragraph("<b>ວັນທີສິ້ນສຸດ / End Date:</b>", meta_label_style), Paragraph(end_date or "-", meta_value_style)],
        [Paragraph("<b>ພິມວັນທີ / Export Date:</b>", meta_label_style), Paragraph(datetime.now().strftime("%Y-%m-%d"), meta_value_style)]
    ]
    meta_table = Table(meta_box_data, colWidths=[110, 100])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#0D47A1')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))

    header_left = Paragraph(
        f"<font size=16 color='#0D47A1'><b>{shop_name}</b></font><br/>"
        f"<font size=9 color='#475569'>{shop_address}<br/>"
        f"ເບີໂທລະສັບ / Phone: {shop_phone}</font>",
        normal_style
    )

    header_right = [
        Paragraph(f"<b>{title_lao}</b>", title_style),
        Paragraph(title_eng, subtitle_style),
        Spacer(1, 6),
        meta_table
    ]

    header_table = Table([[header_left, header_right]], colWidths=[300, 220])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)

    # Divider line
    divider = Table([[""]], colWidths=[520])
    divider.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 1.5, colors.HexColor('#0D47A1')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(divider)


def build_report_signatures(story):
    """Builds prepared/approved signatures block at the end of the report."""
    normal_style = ParagraphStyle(
        'SigNormal',
        fontName=FONT_NAME,
        fontSize=10,
        leading=14
    )
    
    meta_label_style = ParagraphStyle(
        'MetaLabelSig',
        parent=normal_style,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#475569')
    )
    
    sig_data = [
        [
            Paragraph("<b>ຜູ້ຈັດເຮັດລາຍງານ / Prepared By</b>", meta_label_style),
            Paragraph("<b>ຜູ້ອະນຸມັດ / Approved By</b>", meta_label_style)
        ],
        [
            Spacer(1, 35),
            Spacer(1, 35)
        ],
        [
            Paragraph("ລົງຊື່: ...........................................................", meta_label_style),
            Paragraph("ລົງຊື່: ...........................................................", meta_label_style)
        ],
        [
            Paragraph("(....................................................................)", meta_label_style),
            Paragraph("(....................................................................)", meta_label_style)
        ],
        [
            Paragraph("ຕຳແໜ່ງ: .......................................................", meta_label_style),
            Paragraph("ຕຳແໜ່ງ: .......................................................", meta_label_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[260, 260])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(Spacer(1, 15))
    story.append(KeepTogether([
        sig_table
    ]))


def generate_revenue_report_pdf(start_date: str = None, end_date: str = None) -> bytes:
    """Generates the Revenue, Expenses, and Profit Report as PDF bytes."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 1. Fetch shop info
        cursor.execute("SELECT name, address, phone FROM Shop LIMIT 1")
        shop = cursor.fetchone() or {
            "name": "J&P Auto Maxing",
            "address": "ນະຄອນຫຼວງວຽງຈັນ (Vientiane, Laos)",
            "phone": "020 22224444"
        }
        
        # 2. Financial Totals
        cursor.execute("""
            SELECT 
                SUM(final_total) as total_revenue,
                SUM(total_discount) as total_discount_given,
                COUNT(*) as invoice_count,
                SUM(received_amount) as total_received
            FROM invoices
            WHERE DATE(paid_date) BETWEEN %s AND %s
            AND payment_status = 'paid'
        """, (start_date, end_date))
        revenue_data = cursor.fetchone() or {}
        
        # Parts cost
        cursor.execute("""
            SELECT 
                SUM(pu.qty * pu.cost_price) as total_parts_cost
            FROM parts_usage pu
            LEFT JOIN repair_orders ro ON pu.repair_id = ro.id
            WHERE DATE(ro.start_date) BETWEEN %s AND %s
        """, (start_date, end_date))
        parts_cost_data = cursor.fetchone() or {}
        
        # Purchase cost
        cursor.execute("""
            SELECT 
                SUM(total_amount) as total_purchase_cost
            FROM purchase_orders
            WHERE DATE(order_date) BETWEEN %s AND %s
            AND status IN ('ordering', 'partial', 'completed')
        """, (start_date, end_date))
        purchase_cost_data = cursor.fetchone() or {}
        
        # Payment methods
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
        
        # Daily revenue
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
        
    except Exception as ex:
        print(f"Error querying data for PDF: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        cursor.close()
        db.close()
        
    # Formatting helper for currency
    def format_kip(val):
        try:
            return f"{int(val or 0):,} KIP"
        except:
            return "0 KIP"
            
    # Calculate
    total_rev = revenue_data.get('total_revenue', 0) or 0
    total_disc = revenue_data.get('total_discount_given', 0) or 0
    total_parts = parts_cost_data.get('total_parts_cost', 0) or 0
    total_purchase = purchase_cost_data.get('total_purchase_cost', 0) or 0
    total_expenses = total_parts + total_purchase
    net_profit = total_rev - total_expenses
    profit_margin = (net_profit / total_rev * 100) if total_rev > 0 else 0
    
    # Story
    story = []
    build_report_header(story, "ລາຍງານລາຍຮັບ-ລາຍຈ່າຍ ແລະ ກຳໄລ", "Revenue, Expenses, and Profit Report", start_date, end_date, shop)
    
    # Styling
    normal_style = ParagraphStyle('ReportNormal', fontName=FONT_NAME, fontSize=10, leading=14)
    
    sect_title_style = ParagraphStyle(
        'SectTitle',
        parent=normal_style,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0D47A1'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    table_cell = ParagraphStyle(
        'TableCell',
        parent=normal_style,
        fontSize=9,
        leading=12
    )
    
    table_hdr = ParagraphStyle(
        'TableHdr',
        parent=normal_style,
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=1 # Center
    )
    
    # Financial Summary Table
    summary_data = [
        [Paragraph("<b>ລາຍການ / Financial Item</b>", table_hdr), Paragraph("<b>ມູນຄ່າ / Amount (KIP)</b>", table_hdr)],
        [Paragraph("ລາຍຮັບທັງໝົດ / Total Revenue", table_cell), Paragraph(format_kip(total_rev), table_cell)],
        [Paragraph("ສ່ວນຫຼຸດທັງໝົດ / Total Discounts Given", table_cell), Paragraph(format_kip(total_disc), table_cell)],
        [Paragraph("ຕົ້ນທຶນອາໄຫຼ່ທີ່ໃຊ້ / Spare Parts Expenses", table_cell), Paragraph(format_kip(total_parts), table_cell)],
        [Paragraph("ຕົ້ນທຶນການສັ່ງຊື້ອາໄຫຼ່ / Purchase Expenses", table_cell), Paragraph(format_kip(total_purchase), table_cell)],
        [Paragraph("ລາຍຈ່າຍທັງໝົດ / Total Expenses (Parts + Purchases)", table_cell), Paragraph(format_kip(total_expenses), table_cell)],
        [Paragraph("<b>ກຳໄລສຸດທິ / Net Profit</b>", table_cell), Paragraph(f"<b>{format_kip(net_profit)}</b>", table_cell)],
        [Paragraph("<b>ອັດຕາກຳໄລ / Net Profit Margin</b>", table_cell), Paragraph(f"<b>{profit_margin:.1f}%</b>", table_cell)]
    ]
    summary_table = Table(summary_data, colWidths=[300, 220])
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('BACKGROUND', (0, 6), (1, 7), colors.HexColor('#F1F5F9')),
    ]))
    
    story.append(Paragraph("<b>ສະຫຼຸບລາຍຮັບ-ລາຍຈ່າຍ / Financial Summary</b>", sect_title_style))
    story.append(summary_table)
    story.append(Spacer(1, 10))
    
    # Payment Method Table
    pm_data = [
        [
            Paragraph("<b>ວິທີການຊຳລະ / Payment Method</b>", table_hdr), 
            Paragraph("<b>ຈຳນວນບິນ / Invoices</b>", table_hdr), 
            Paragraph("<b>ຍອດເງິນ / Amount (KIP)</b>", table_hdr)
        ]
    ]
    for method in payment_methods:
        name = method.get('payment_method', '-')
        display = "\u0ec0\u0e87\u0eb4\u0e99\u0eaa\u0ebb\u0e94 (Cash)" if name == 'cash' else "\u0ec2\u0e8a\u0e99\u0ec0\u0e87\u0eb4\u0e99 (Transfer)" if name == 'transfer' else "QR Payment" if name == 'qr' else name.capitalize()
        pm_data.append([
            Paragraph(display, table_cell),
            Paragraph(str(method.get('count', 0)), table_cell),
            Paragraph(format_kip(method.get('amount', 0)), table_cell)
        ])
    if len(pm_data) == 1:
        pm_data.append([Paragraph("ບໍ່ມີຂໍ້ມູນ (No data)", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell)])
        
    pm_table = Table(pm_data, colWidths=[200, 120, 200])
    pm_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    story.append(Paragraph("<b>ຊ່ອງທາງການຊຳລະເງິນ / Payment Methods</b>", sect_title_style))
    story.append(pm_table)
    story.append(Spacer(1, 10))
    
    # Daily Revenue Table
    daily_data = [
        [
            Paragraph("<b>ວັນທີ / Date</b>", table_hdr),
            Paragraph("<b>ຈຳນວນບິນ / Invoices</b>", table_hdr),
            Paragraph("<b>ຍອດລາຍຮັບ / Revenue (KIP)</b>", table_hdr)
        ]
    ]
    for d in daily_revenue[:20]: # show top 20 days
        date_str = str(d.get('date', '-'))
        daily_data.append([
            Paragraph(date_str, table_cell),
            Paragraph(str(d.get('daily_invoice_count', 0)), table_cell),
            Paragraph(format_kip(d.get('daily_revenue', 0)), table_cell)
        ])
    if len(daily_data) == 1:
        daily_data.append([Paragraph("ບໍ່ມີຂໍ້ມູນ (No data)", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell)])
        
    daily_table = Table(daily_data, colWidths=[150, 120, 250])
    daily_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    
    story.append(Paragraph("<b>ລາຍຮັບປະຈຳວັນ / Daily Breakdown (Top 20 Days)</b>", sect_title_style))
    story.append(daily_table)
    
    build_report_signatures(story)
    
    # Build
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=54
    )
    doc.build(story, canvasmaker=create_canvas_class("ລາຍງານລາຍຮັບ-ລາຍຈ່າຍ ແລະ ກຳໄລ (Revenue Report)"))
    pdf_content = buffer.getvalue()
    buffer.close()
    return pdf_content


def generate_repair_summary_pdf(start_date: str = None, end_date: str = None) -> bytes:
    """Generates the Repair Statistics Report as PDF bytes."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Shop info
        cursor.execute("SELECT name, address, phone FROM Shop LIMIT 1")
        shop = cursor.fetchone() or {
            "name": "J&P Auto Maxing",
            "address": "ນະຄອນຫຼວງວຽງຈັນ (Vientiane, Laos)",
            "phone": "020 22224444"
        }
        
        # Status summary
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
        
        # Overall repair stats
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
        repair_stats = cursor.fetchone() or {}
        
        # Vehicle brand stats
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
        
        # Daily repair trends
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
            LIMIT 20
        """, (start_date, end_date))
        daily_repairs = cursor.fetchall()
        
    except Exception as ex:
        print(f"Error querying data for PDF: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        cursor.close()
        db.close()
        
    total_repairs = repair_stats.get('total_repairs', 0) or 0
    completed_repairs = repair_stats.get('completed_repairs', 0) or 0
    working_repairs = repair_stats.get('working_repairs', 0) or 0
    waiting_repairs = repair_stats.get('waiting_repairs', 0) or 0
    paused_repairs = repair_stats.get('paused_repairs', 0) or 0
    avg_hours = repair_stats.get('avg_repair_hours', 0) or 0
    completion_rate = (completed_repairs / total_repairs * 100) if total_repairs > 0 else 0
    
    # Story
    story = []
    build_report_header(story, "ລາຍງານການສ້ອມແປງ", "Repair Statistics Report", start_date, end_date, shop)
    
    # Styling
    normal_style = ParagraphStyle('ReportNormal', fontName=FONT_NAME, fontSize=10, leading=14)
    
    sect_title_style = ParagraphStyle(
        'SectTitle',
        parent=normal_style,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0D47A1'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    table_cell = ParagraphStyle(
        'TableCell',
        parent=normal_style,
        fontSize=9,
        leading=12
    )
    
    table_hdr = ParagraphStyle(
        'TableHdr',
        parent=normal_style,
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=1 # Center
    )
    
    # Overall metrics
    metrics_data = [
        [
            Paragraph("<b>ຕົວຊີ້ບອກ / Metric</b>", table_hdr), 
            Paragraph("<b>ຄ່າສະຖິຕິ / Value</b>", table_hdr)
        ],
        [Paragraph("ວຽກສ້ອມແປງທັງໝົດ / Total Repair Orders", table_cell), Paragraph(str(total_repairs), table_cell)],
        [Paragraph("ສຳເລັດແລ້ວ / Completed", table_cell), Paragraph(str(completed_repairs), table_cell)],
        [Paragraph("ກຳລັງດຳເນີນການ / In-Progress", table_cell), Paragraph(str(working_repairs), table_cell)],
        [Paragraph("ລໍຖ້າອາໄຫຼ່/ຄິວ / Waiting", table_cell), Paragraph(str(waiting_repairs), table_cell)],
        [Paragraph("ຢຸດຊົ່ວຄາວ / Paused", table_cell), Paragraph(str(paused_repairs), table_cell)],
        [Paragraph("ອັດຕາຊ່ອມສຳເລັດ / Completion Success Rate", table_cell), Paragraph(f"{completion_rate:.1f}%", table_cell)],
        [Paragraph("ໄລຍະເວລາຊ່ອມສະເລ່ຍ / Average Repair Time", table_cell), Paragraph(f"{avg_hours:.1f} ຊົ່ວໂມງ (Hours)", table_cell)]
    ]
    metrics_table = Table(metrics_data, colWidths=[300, 220])
    metrics_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    story.append(Paragraph("<b>ສະຫຼຸບສະຖິຕິການສ້ອມແປງ / Repair Summary KPIs</b>", sect_title_style))
    story.append(metrics_table)
    story.append(Spacer(1, 10))
    
    # Repairs by brand
    brand_data = [
        [
            Paragraph("<b>ຍີ່ຫໍ້ລົດ / Brand</b>", table_hdr), 
            Paragraph("<b>ຈຳນວນງານສ້ອມແປງ / Total Repairs</b>", table_hdr), 
            Paragraph("<b>ຊ່ອມສຳເລັດ / Completed</b>", table_hdr),
            Paragraph("<b>ເວລາສະເລ່ຍ / Avg Hours</b>", table_hdr)
        ]
    ]
    for b in vehicle_stats:
        b_hours = b.get('avg_hours')
        hours_text = f"{float(b_hours):.1f}" if b_hours is not None else "-"
        brand_data.append([
            Paragraph(b.get('brand', 'ບໍ່ລະບຸ'), table_cell),
            Paragraph(str(b.get('repair_count', 0)), table_cell),
            Paragraph(str(b.get('completed_count', 0)), table_cell),
            Paragraph(hours_text, table_cell)
        ])
    if len(brand_data) == 1:
        brand_data.append([Paragraph("ບໍ່ມີຂໍ້ມູນ (No data)", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell)])
        
    brand_table = Table(brand_data, colWidths=[180, 120, 110, 110])
    brand_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    
    story.append(Paragraph("<b>ຍານພາຫະນະທີ່ມີການສ້ອມແປງສູງສຸດ / Top Repaired Brands</b>", sect_title_style))
    story.append(brand_table)
    story.append(Spacer(1, 10))
    
    # Daily repair trends
    daily_data = [
        [
            Paragraph("<b>ວັນທີ / Date</b>", table_hdr), 
            Paragraph("<b>ງານສ້ອມແປງທັງໝົດ / Total Started</b>", table_hdr), 
            Paragraph("<b>ຊ່ອມສຳເລັດ / Completed</b>", table_hdr),
            Paragraph("<b>ກຳລັງຊ່ອມ / In Progress</b>", table_hdr)
        ]
    ]
    for d in daily_repairs:
        daily_data.append([
            Paragraph(str(d.get('date', '-')), table_cell),
            Paragraph(str(d.get('daily_repairs', 0)), table_cell),
            Paragraph(str(d.get('daily_completed', 0)), table_cell),
            Paragraph(str(d.get('daily_in_progress', 0)), table_cell)
        ])
    if len(daily_data) == 1:
        daily_data.append([Paragraph("ບໍ່ມີຂໍ້ມູນ (No data)", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell)])
        
    daily_table = Table(daily_data, colWidths=[150, 130, 120, 120])
    daily_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    
    story.append(Paragraph("<b>ແນວໂນ້ມການສ້ອມແປງປະຈຳວັນ / Daily Repair Trends</b>", sect_title_style))
    story.append(daily_table)
    
    build_report_signatures(story)
    
    # Build
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=54
    )
    doc.build(story, canvasmaker=create_canvas_class("ລາຍງານການສ້ອມແປງ (Repair Statistics Report)"))
    pdf_content = buffer.getvalue()
    buffer.close()
    return pdf_content


def generate_parts_service_sales_pdf(start_date: str = None, end_date: str = None) -> bytes:
    """Generates the Services and Spare Parts Sales Report as PDF bytes."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Shop info
        cursor.execute("SELECT name, address, phone FROM Shop LIMIT 1")
        shop = cursor.fetchone() or {
            "name": "J&P Auto Maxing",
            "address": "ນະຄອນຫຼວງວຽງຈັນ (Vientiane, Laos)",
            "phone": "020 22224444"
        }
        
        # 1. Services Sales Breakdown from approved quotations
        cursor.execute("""
            SELECT 
                s.name as service_name,
                SUM(qi.qty) as quantity_sold,
                AVG(qi.unit_price) as avg_unit_price,
                SUM(qi.total) as total_sales_amount
            FROM quotation_items qi
            LEFT JOIN services s ON qi.service_id = s.id
            LEFT JOIN quotations q ON qi.quotation_id = q.id
            WHERE qi.service_id IS NOT NULL AND q.status = 'approved'
            AND DATE(q.created_at) BETWEEN %s AND %s
            GROUP BY s.id, s.name
            ORDER BY total_sales_amount DESC
            LIMIT 30
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
            LIMIT 30
        """, (start_date, end_date))
        parts_sales = cursor.fetchall()
        
    except Exception as ex:
        print(f"Error querying data for PDF: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        cursor.close()
        db.close()
        
    # Formatting helper for currency
    def format_kip(val):
        try:
            return f"{int(val or 0):,} KIP"
        except:
            return "0 KIP"
            
    total_service_sales = sum([float(x['total_sales_amount'] or 0) for x in service_sales])
    total_parts_sales = sum([float(x['total_sales_amount'] or 0) for x in parts_sales])
    total_parts_cost = sum([float(x['total_cost_amount'] or 0) for x in parts_sales])
    total_parts_profit = sum([float(x['profit'] or 0) for x in parts_sales])
    combined_sales = total_service_sales + total_parts_sales
    
    story = []
    build_report_header(story, "ລາຍງານຍອດຂາຍບໍລິການ ແລະ ອາໄຫຼ່", "Services and Spare Parts Sales Report", start_date, end_date, shop)
    
    # Styling
    normal_style = ParagraphStyle('ReportNormal', fontName=FONT_NAME, fontSize=10, leading=14)
    
    sect_title_style = ParagraphStyle(
        'SectTitle',
        parent=normal_style,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0D47A1'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    table_cell = ParagraphStyle(
        'TableCell',
        parent=normal_style,
        fontSize=8.5,
        leading=11
    )
    
    table_hdr = ParagraphStyle(
        'TableHdr',
        parent=normal_style,
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=1 # Center
    )
    
    # Financial Summary
    summary_data = [
        [Paragraph("<b>ໝວດໝູ່ຍອດຂາຍ / Category</b>", table_hdr), Paragraph("<b>ຍອດຂາຍ / Revenue (KIP)</b>", table_hdr)],
        [Paragraph("ຍອດຂາຍບໍລິການ / Services Sales", table_cell), Paragraph(format_kip(total_service_sales), table_cell)],
        [Paragraph("ຍອດຂາຍອາໄຫຼ່ / Spare Parts Sales", table_cell), Paragraph(format_kip(total_parts_sales), table_cell)],
        [Paragraph("<b>ຍອດຂາຍລວມ / Combined Sales</b>", table_cell), Paragraph(f"<b>{format_kip(combined_sales)}</b>", table_cell)],
        [Paragraph("ຕົ້ນທຶນອາໄຫຼ່ທີ່ຂາຍ / Spare Parts Cost", table_cell), Paragraph(format_kip(total_parts_cost), table_cell)],
        [Paragraph("<b>ກຳໄລຂັ້ນຕົ້ນຈາກອາໄຫຼ່ / Spare Parts Profit</b>", table_cell), Paragraph(f"<b>{format_kip(total_parts_profit)}</b>", table_cell)]
    ]
    summary_table = Table(summary_data, colWidths=[280, 240])
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('BACKGROUND', (0, 3), (1, 3), colors.HexColor('#F1F5F9')),
        ('BACKGROUND', (0, 5), (1, 5), colors.HexColor('#E2E8F0')),
    ]))
    story.append(Paragraph("<b>ສະຫຼຸບຍອດຂາຍ / Sales Summary</b>", sect_title_style))
    story.append(summary_table)
    story.append(Spacer(1, 10))
    
    # Top Services
    srv_data = [
        [
            Paragraph("<b>ລຳດັບ<br/>No.</b>", table_hdr),
            Paragraph("<b>ชື່ການບໍລິການ / Service Description</b>", table_hdr), 
            Paragraph("<b>ຈຳນວນຄັ້ງ / Qty</b>", table_hdr), 
            Paragraph("<b>ລາຄາສະເລ່ຍ / Avg Price</b>", table_hdr),
            Paragraph("<b>ຍອດລວມ / Total (KIP)</b>", table_hdr)
        ]
    ]
    for idx, s in enumerate(service_sales[:15]): # top 15 services
        srv_data.append([
            Paragraph(str(idx + 1), table_cell),
            Paragraph(s.get('service_name', '-'), table_cell),
            Paragraph(str(int(s.get('quantity_sold', 0))), table_cell),
            Paragraph(format_kip(s.get('avg_unit_price', 0)), table_cell),
            Paragraph(format_kip(s.get('total_sales_amount', 0)), table_cell)
        ])
    if len(srv_data) == 1:
        srv_data.append([Paragraph("ບໍ່ມີຂໍ້ມູນ (No data)", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell)])
        
    srv_table = Table(srv_data, colWidths=[35, 185, 50, 110, 140])
    srv_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    story.append(Paragraph("<b>ການບໍລິການຍອດນິຍົມ / Top Services Sold</b>", sect_title_style))
    story.append(srv_table)
    story.append(Spacer(1, 10))
    
    # Top Parts
    prt_data = [
        [
            Paragraph("<b>ລຳດັບ<br/>No.</b>", table_hdr),
            Paragraph("<b>ຊື່ອາໄຫຼ່ / Spare Part Description</b>", table_hdr), 
            Paragraph("<b>ປະເພດ / Category</b>", table_hdr),
            Paragraph("<b>ຈຳນວນ / Qty</b>", table_hdr), 
            Paragraph("<b>ຍອດຂາຍ / Revenue</b>", table_hdr),
            Paragraph("<b>ກຳໄລ / Profit</b>", table_hdr)
        ]
    ]
    for idx, p in enumerate(parts_sales[:15]): # top 15 parts
        prt_data.append([
            Paragraph(str(idx + 1), table_cell),
            Paragraph(p.get('part_name', '-'), table_cell),
            Paragraph(p.get('category_name', '-'), table_cell),
            Paragraph(f"{int(p.get('quantity_sold', 0))} {p.get('unit_name', 'ອັນ')}", table_cell),
            Paragraph(format_kip(p.get('total_sales_amount', 0)), table_cell),
            Paragraph(format_kip(p.get('profit', 0)), table_cell)
        ])
    if len(prt_data) == 1:
        prt_data.append([Paragraph("ບໍ່ມີຂໍ້ມູນ (No data)", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell)])
        
    prt_table = Table(prt_data, colWidths=[35, 175, 90, 60, 80, 80])
    prt_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    story.append(Paragraph("<b>ລາຍການອາໄຫຼ່ຂາຍດີ / Top Spare Parts Sold</b>", sect_title_style))
    story.append(prt_table)
    
    build_report_signatures(story)
    
    # Build
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=54
    )
    doc.build(story, canvasmaker=create_canvas_class("ລາຍງານຍອດຂາຍບໍລິການ ແລະ ອາໄຫຼ່ (Sales Report)"))
    pdf_content = buffer.getvalue()
    buffer.close()
    return pdf_content


def generate_mechanic_performance_pdf(start_date: str = None, end_date: str = None) -> bytes:
    """Generates the Mechanic Performance Report as PDF bytes."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Shop info
        cursor.execute("SELECT name, address, phone FROM Shop LIMIT 1")
        shop = cursor.fetchone() or {
            "name": "J&P Auto Maxing",
            "address": "ນະຄອນຫຼວງວຽງຈັນ (Vientiane, Laos)",
            "phone": "020 22224444"
        }
        
        cursor.execute("""
            SELECT 
                e.id as mechanic_id,
                e.name as mechanic_name,
                e.phone as mechanic_phone,
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
            GROUP BY e.id, e.name, e.phone
            ORDER BY completed_count DESC
        """, (start_date, end_date))
        mechanic_stats = cursor.fetchall()
        
    except Exception as ex:
        print(f"Error querying data for PDF: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        cursor.close()
        db.close()
        
    total_assigned = 0
    total_completed = 0
    total_working = 0
    valid_durations = []
    
    for m in mechanic_stats:
        m['total_assigned'] = int(m['total_assigned'] or 0)
        m['completed_count'] = int(m['completed_count'] or 0)
        m['working_count'] = int(m['working_count'] or 0)
        m['avg_hours'] = float(m['avg_hours'] or 0) if m['avg_hours'] is not None else None
        
        total_assigned += m['total_assigned']
        total_completed += m['completed_count']
        total_working += m['working_count']
        if m['avg_hours'] is not None and m['avg_hours'] > 0:
            valid_durations.append(m['avg_hours'])
            
    avg_workshop_hours = round(sum(valid_durations) / len(valid_durations), 1) if valid_durations else 0
    workshop_efficiency = (total_completed / total_assigned * 100) if total_assigned > 0 else 0
    
    story = []
    build_report_header(story, "ລາຍງານປະສິດທິພາບຂອງຊ່າງ", "Mechanic Performance Report", start_date, end_date, shop)
    
    # Styling
    normal_style = ParagraphStyle('ReportNormal', fontName=FONT_NAME, fontSize=10, leading=14)
    
    sect_title_style = ParagraphStyle(
        'SectTitle',
        parent=normal_style,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0D47A1'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    table_cell = ParagraphStyle(
        'TableCell',
        parent=normal_style,
        fontSize=9,
        leading=12
    )
    
    table_hdr = ParagraphStyle(
        'TableHdr',
        parent=normal_style,
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=1 # Center
    )
    
    # KPI metrics table
    metrics_data = [
        [Paragraph("<b>ຕົວຊີ້ບອກ / KPI Indicator</b>", table_hdr), Paragraph("<b>ຄ່າວັດແທກ / Performance Value</b>", table_hdr)],
        [Paragraph("ຈຳນວນຊ່າງສ້ອມແປງທັງໝົດ / Total Mechanics", table_cell), Paragraph(str(len(mechanic_stats)), table_cell)],
        [Paragraph("ຈຳນວນງານສ້ອມແປງທີ່ມອບໝາຍ / Total Assigned Jobs", table_cell), Paragraph(str(total_assigned), table_cell)],
        [Paragraph("ງານຊ່ອມແປງທີ່ສຳເລັດ / Completed Jobs", table_cell), Paragraph(str(total_completed), table_cell)],
        [Paragraph("ງານຊ່ອມແປງທີ່ກຳລັງເຮັດ / Ongoing Jobs", table_cell), Paragraph(str(total_working), table_cell)],
        [Paragraph("ເວລາຊ່ອມແປງສະເລ່ຍ / Avg Workshop Repair Duration", table_cell), Paragraph(f"{avg_workshop_hours:.1f} ຊົ່ວໂມງ (Hours)", table_cell)],
        [Paragraph("ອັດຕາຊ່ອມສຳເລັດຂອງຮ້ານ / Overall Completion Rate", table_cell), Paragraph(f"{workshop_efficiency:.1f}%", table_cell)],
    ]
    metrics_table = Table(metrics_data, colWidths=[280, 240])
    metrics_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(Paragraph("<b>ພາບລວມປະສິດທິພາບຮ້ານ / Workshop Performance Overview</b>", sect_title_style))
    story.append(metrics_table)
    story.append(Spacer(1, 10))
    
    # Mechanic details
    perf_data = [
        [
            Paragraph("<b>ລຳດັບ<br/>No.</b>", table_hdr),
            Paragraph("<b>ຊື່ນາຍຊ່າງ / Mechanic Name</b>", table_hdr),
            Paragraph("<b>ເບີໂທ / Phone</b>", table_hdr),
            Paragraph("<b>ມອບໝາຍ / Jobs</b>", table_hdr),
            Paragraph("<b>ສຳເລັດ / Done</b>", table_hdr),
            Paragraph("<b>ເວລາສະເລ່ຍ / Avg Hours</b>", table_hdr),
            Paragraph("<b>ອັດຕາສຳເລັດ / Rate</b>", table_hdr)
        ]
    ]
    for idx, m in enumerate(mechanic_stats):
        assigned = m['total_assigned']
        done = m['completed_count']
        rate = (done / assigned * 100) if assigned > 0 else 0
        avg_h = m['avg_hours']
        avg_text = f"{float(avg_h):.1f}" if avg_h is not None else "-"
        perf_data.append([
            Paragraph(str(idx + 1), table_cell),
            Paragraph(m.get('mechanic_name', '-'), table_cell),
            Paragraph(m.get('mechanic_phone', '-'), table_cell),
            Paragraph(str(assigned), table_cell),
            Paragraph(str(done), table_cell),
            Paragraph(avg_text, table_cell),
            Paragraph(f"{rate:.1f}%", table_cell)
        ])
    if len(perf_data) == 1:
        perf_data.append([Paragraph("ບໍ່ມີຂໍ້ມູນຊ່າງສ້ອມແປງ (No mechanic data available)", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell)])
        
    perf_table = Table(perf_data, colWidths=[35, 145, 90, 50, 50, 80, 70])
    perf_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    story.append(Paragraph("<b>ລາຍລະອຽດປະສິດທິພາບຂອງຊ່າງ / Mechanic Performance Details</b>", sect_title_style))
    story.append(perf_table)
    
    build_report_signatures(story)
    
    # Build
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=54
    )
    doc.build(story, canvasmaker=create_canvas_class("ລາຍງານປະສິດທິພາບຂອງຊ່າງ (Mechanic Performance Report)"))
    pdf_content = buffer.getvalue()
    buffer.close()
    return pdf_content


def generate_promotion_usage_pdf(start_date: str = None, end_date: str = None) -> bytes:
    """Generates the Promotion & Discount Usage Report as PDF bytes."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Shop info
        cursor.execute("SELECT name, address, phone FROM Shop LIMIT 1")
        shop = cursor.fetchone() or {
            "name": "J&P Auto Maxing",
            "address": "ນະຄອນຫຼວງວຽງຈັນ (Vientiane, Laos)",
            "phone": "020 22224444"
        }
        
        # 1. Promotion usage from invoices
        cursor.execute("""
            SELECT 
                p.name as promotion_name,
                p.discount_type,
                p.value,
                COUNT(i.id) as usage_count,
                SUM(i.total_discount) as total_discount_given,
                SUM(i.final_total) as total_revenue_with_promotion
            FROM invoices i
            LEFT JOIN promotions p ON i.promotion_id = p.id
            WHERE DATE(i.paid_date) BETWEEN %s AND %s
            AND i.promotion_id IS NOT NULL
            AND i.payment_status = 'paid'
            GROUP BY p.id, p.name, p.discount_type, p.value
            ORDER BY usage_count DESC
        """, (start_date, end_date))
        promotion_usage = cursor.fetchall()
        
        # 2. Promotions quoted but not yet used
        cursor.execute("""
            SELECT 
                p.name as promotion_name,
                COUNT(DISTINCT q.id) as quoted_count,
                SUM(q.discount_amount) as total_quoted_discount
            FROM quotations q
            LEFT JOIN promotions p ON q.promotion_id = p.id
            WHERE DATE(q.created_at) BETWEEN %s AND %s
            AND q.promotion_id IS NOT NULL
            AND q.status = 'approved'
            GROUP BY p.id, p.name
            ORDER BY quoted_count DESC
        """, (start_date, end_date))
        promotion_quoted = cursor.fetchall()
        
        # 3. Compare revenue with vs without promotion
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN promotion_id IS NOT NULL THEN 'With Promotion'
                    ELSE 'Without Promotion'
                END as promo_status,
                COUNT(*) as invoice_count,
                SUM(final_total) as total_revenue
            FROM invoices
            WHERE DATE(paid_date) BETWEEN %s AND %s
            AND payment_status = 'paid'
            GROUP BY CASE WHEN promotion_id IS NOT NULL THEN 'With Promotion' ELSE 'Without Promotion' END
        """, (start_date, end_date))
        comparison = cursor.fetchall()
        
    except Exception as ex:
        print(f"Error querying data for PDF: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))
    finally:
        cursor.close()
        db.close()
        
    # Formatting helper for currency
    def format_kip(val):
        try:
            return f"{int(val or 0):,} KIP"
        except:
            return "0 KIP"
            
    total_discount_given = sum([float(x['total_discount_given'] or 0) for x in promotion_usage])
    total_promo_invoices = sum([int(x['usage_count'] or 0) for x in promotion_usage])
    total_promo_revenue = sum([float(x['total_revenue_with_promotion'] or 0) for x in promotion_usage])
    
    story = []
    build_report_header(story, "ລາຍງານການນຳໃຊ້ໂປຣໂມຊັນ", "Promotion & Discount Usage Report", start_date, end_date, shop)
    
    # Styling
    normal_style = ParagraphStyle('ReportNormal', fontName=FONT_NAME, fontSize=10, leading=14)
    
    sect_title_style = ParagraphStyle(
        'SectTitle',
        parent=normal_style,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0D47A1'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    table_cell = ParagraphStyle(
        'TableCell',
        parent=normal_style,
        fontSize=9,
        leading=12
    )
    
    table_hdr = ParagraphStyle(
        'TableHdr',
        parent=normal_style,
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=1 # Center
    )
    
    # KPI metrics table
    metrics_data = [
        [Paragraph("<b>ຕົວຊີ້ບອກ / KPI Indicator</b>", table_hdr), Paragraph("<b>ຄ່າສະຖິຕິ / Value</b>", table_hdr)],
        [Paragraph("ຈຳນວນຄັ້ງທີ່ໃຊ້ໂປຣໂມຊັນ / Total Promotions Applied", table_cell), Paragraph(str(total_promo_invoices), table_cell)],
        [Paragraph("ສ່ວນຫຼຸດທັງໝົດທີ່ມອບໃຫ້ / Total Discount Given", table_cell), Paragraph(format_kip(total_discount_given), table_cell)],
        [Paragraph("ລາຍຮັບຈາກໃບບິນໂປໂມຊັນ / Revenue from Promo Invoices", table_cell), Paragraph(format_kip(total_promo_revenue), table_cell)],
    ]
    metrics_table = Table(metrics_data, colWidths=[280, 240])
    metrics_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(Paragraph("<b>ສະຫຼຸບການນຳໃຊ້ / Campaign Summary</b>", sect_title_style))
    story.append(metrics_table)
    story.append(Spacer(1, 10))
    
    # Detailed Usage
    det_data = [
        [
            Paragraph("<b>ຊື່ໂປຣໂມຊັນ / Promotion Name</b>", table_hdr),
            Paragraph("<b>ປະເພດສ່ວນຫຼຸດ / Type</b>", table_hdr),
            Paragraph("<b>ຈຳນວນຄັ້ງ / Count</b>", table_hdr),
            Paragraph("<b>ສ່ວນຫຼຸດລວມ / Discount</b>", table_hdr),
            Paragraph("<b>ລາຍຮັບ / Revenue</b>", table_hdr)
        ]
    ]
    for p in promotion_usage:
        disc_type = p.get('discount_type')
        val = p.get('value')
        val_text = f"{int(val)}%" if disc_type == 'percentage' else f"{format_kip(val)}"
        det_data.append([
            Paragraph(p.get('promotion_name', '-'), table_cell),
            Paragraph(val_text, table_cell),
            Paragraph(str(p.get('usage_count', 0)), table_cell),
            Paragraph(format_kip(p.get('total_discount_given', 0)), table_cell),
            Paragraph(format_kip(p.get('total_revenue_with_promotion', 0)), table_cell)
        ])
    if len(det_data) == 1:
        det_data.append([Paragraph("ບໍ່ມີຂໍ້ມູນໂປຣໂມຊັນທີ່ໃຊ້ງານ (No promotions used)", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell)])
        
    det_table = Table(det_data, colWidths=[150, 90, 60, 110, 110])
    det_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    story.append(Paragraph("<b>ລາຍລະອຽດການນຳໃຊ້ໂປຣໂມຊັນ / Detailed Promotion Usage</b>", sect_title_style))
    story.append(det_table)
    story.append(Spacer(1, 10))
    
    # Revenue comparison
    comp_data = [
        [
            Paragraph("<b>ສະຖານະ / Promo Status</b>", table_hdr),
            Paragraph("<b>ຈຳນວນບິນ / Invoices</b>", table_hdr),
            Paragraph("<b>ລາຍຮັບ / Total Revenue</b>", table_hdr),
            Paragraph("<b>ຍອດສະເລ່ຍ / Average Value</b>", table_hdr)
        ]
    ]
    for c in comparison:
        status_text = "ນຳໃຊ້ໂປຣໂມຊັນ (With Promo)" if c.get('promo_status') == 'With Promotion' else "ບໍ່ໃຊ້ໂປຣໂມຊັນ (Without Promo)"
        rev = float(c.get('total_revenue', 0) or 0)
        cnt = int(c.get('invoice_count', 0) or 0)
        avg_val = (rev / cnt) if cnt > 0 else 0
        comp_data.append([
            Paragraph(status_text, table_cell),
            Paragraph(str(cnt), table_cell),
            Paragraph(format_kip(rev), table_cell),
            Paragraph(format_kip(avg_val), table_cell)
        ])
    if len(comp_data) == 1:
        comp_data.append([Paragraph("ບໍ່ມີຂໍ້ມູນ (No data)", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell), Paragraph("-", table_cell)])
        
    comp_table = Table(comp_data, colWidths=[170, 90, 130, 130])
    comp_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    story.append(Paragraph("<b>ປຽບທຽບຍອດຂາຍ / Campaign Revenue Comparison</b>", sect_title_style))
    story.append(comp_table)
    
    build_report_signatures(story)
    
    # Build
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=54
    )
    doc.build(story, canvasmaker=create_canvas_class("ລາຍງານການນຳໃຊ້ໂປຣໂມຊັນ (Promotion Usage Report)"))
    pdf_content = buffer.getvalue()
    buffer.close()
    return pdf_content
