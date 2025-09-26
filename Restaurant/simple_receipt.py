from datetime import datetime
from fastapi.responses import Response

def generate_simple_receipt(order_details, table_number, restaurant_name, tip_amount=0):
    """Generate a simple text receipt"""
    
    receipt_text = f"""RECEIPT - {restaurant_name}
{'='*40}
Table: {table_number}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Order #: {order_details['order_id']}

--- ITEMS ---
"""
    
    for item in order_details['items']:
        receipt_text += f"{item['name']} x{item['qty']} - €{item['total']:.2f}\n"
        
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
                    receipt_text += f"  ({' | '.join(custom_parts)})\n"
            except:
                pass
    
    # Calculate totals
    order_total = order_details['total']
    products_plus_tip = order_total + tip_amount
    iva_amount = products_plus_tip * 0.21
    subtotal_without_iva = products_plus_tip - iva_amount
    
    receipt_text += f"""
--- TOTALS ---
Subtotal: €{order_total:.2f}
Tip: €{tip_amount:.2f}
Subtotal (excl. IVA): €{subtotal_without_iva:.2f}
IVA (21%): €{iva_amount:.2f}
TOTAL: €{products_plus_tip:.2f}

Thank you for dining with us!
{'='*40}"""
    
    return Response(
        content=receipt_text,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=receipt_table_{table_number}.txt"}
    )