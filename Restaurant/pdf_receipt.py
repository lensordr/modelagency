from datetime import datetime
from fastapi.responses import StreamingResponse
import io

def generate_pdf_receipt(order_details, table_number, restaurant_name, tip_amount=0):
    """Generate a PDF receipt using reportlab"""
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=(4*inch, 8*inch), 
                              topMargin=0.2*inch, bottomMargin=0.2*inch, 
                              leftMargin=0.2*inch, rightMargin=0.2*inch)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], 
                                   fontSize=14, spaceAfter=12, alignment=TA_CENTER)
        normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], 
                                    fontSize=9, spaceAfter=6)
        
        # Build content
        story = []
        
        # Header
        story.append(Paragraph(f"<b>{restaurant_name}</b>", title_style))
        story.append(Paragraph("RECEIPT", ParagraphStyle('Receipt', parent=styles['Normal'], 
                                                        fontSize=12, alignment=TA_CENTER, spaceAfter=12)))
        story.append(Spacer(1, 0.1*inch))
        
        # Order info
        story.append(Paragraph(f"<b>Table:</b> {table_number}", normal_style))
        story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style))
        story.append(Paragraph(f"<b>Order #:</b> {order_details['order_id']}", normal_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Items
        for item in order_details['items']:
            item_line = f"{item['name']} x{item['qty']}"
            price_line = f"€{item['total']:.2f}"
            
            # Create table for item and price alignment
            item_table = Table([[item_line, price_line]], colWidths=[2.5*inch, 1*inch])
            item_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(item_table)
            
            # Add customizations if any
            if item.get('customizations'):
                try:
                    import json
                    custom = json.loads(item['customizations'])
                    custom_parts = []
                    if custom.get('ingredients'):
                        for ing, qty in custom['ingredients'].items():
                            if qty == 0:
                                custom_parts.append(f"No {ing}")
                            elif qty > 1:
                                custom_parts.append(f"Extra {ing}")
                    if custom.get('extra'):
                        custom_parts.append(f"Add: {', '.join(custom['extra'])}")
                    
                    if custom_parts:
                        story.append(Paragraph(f"  <i>{' | '.join(custom_parts)}</i>", 
                                             ParagraphStyle('Small', parent=styles['Normal'], fontSize=8)))
                except:
                    pass
        
        story.append(Spacer(1, 0.1*inch))
        
        # Totals
        order_total = order_details['total']
        products_plus_tip = order_total + tip_amount
        iva_amount = products_plus_tip * 0.21
        subtotal_without_iva = products_plus_tip - iva_amount
        
        # Subtotal
        subtotal_table = Table([["Subtotal:", f"€{order_total:.2f}"]], colWidths=[2.5*inch, 1*inch])
        subtotal_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        story.append(subtotal_table)
        
        # Tip
        if tip_amount > 0:
            tip_table = Table([["Tip:", f"€{tip_amount:.2f}"]], colWidths=[2.5*inch, 1*inch])
            tip_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ]))
            story.append(tip_table)
        
        # IVA breakdown
        iva_subtotal_table = Table([["Subtotal (excl. IVA):", f"€{subtotal_without_iva:.2f}"]], 
                                  colWidths=[2.5*inch, 1*inch])
        iva_subtotal_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        story.append(iva_subtotal_table)
        
        iva_table = Table([["IVA (21%):", f"€{iva_amount:.2f}"]], colWidths=[2.5*inch, 1*inch])
        iva_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        story.append(iva_table)
        
        # Total
        total_table = Table([["TOTAL:", f"€{products_plus_tip:.2f}"]], colWidths=[2.5*inch, 1*inch])
        total_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ]))
        story.append(total_table)
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Thank you for dining with us!", 
                              ParagraphStyle('Thanks', parent=styles['Normal'], 
                                           fontSize=10, alignment=TA_CENTER)))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return StreamingResponse(
            io.BytesIO(buffer.getvalue()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=receipt_table_{table_number}.pdf"}
        )
        
    except ImportError:
        # Fallback to text if reportlab not available
        from simple_receipt import generate_simple_receipt
        return generate_simple_receipt(order_details, table_number, restaurant_name, tip_amount)