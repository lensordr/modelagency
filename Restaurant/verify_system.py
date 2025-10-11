#!/usr/bin/env python3
"""
Verify the ready notification system is working
"""

from models import get_db, Table

def verify_system():
    db = next(get_db())
    
    # Check table 2 status
    table = db.query(Table).filter(Table.table_number == 2).first()
    
    if table:
        print(f"Table 2 status:")
        print(f"  - Status: {table.status}")
        print(f"  - Ready notification: {getattr(table, 'ready_notification', 'Column not found')}")
        print(f"  - Checkout requested: {table.checkout_requested}")
        print(f"  - Has extra order: {table.has_extra_order}")
        
        # Test the API response format
        result = {
            "table_number": table.table_number, 
            "status": table.status, 
            "code": table.code, 
            "checkout_requested": table.checkout_requested, 
            "has_extra_order": table.has_extra_order,
            "checkout_method": getattr(table, 'checkout_method', None),
            "tip_amount": getattr(table, 'tip_amount', 0.0),
            "ready_notification": getattr(table, 'ready_notification', False)
        }
        
        print(f"\nAPI Response format:")
        import json
        print(json.dumps(result, indent=2))
        
    else:
        print("Table 2 not found")
    
    db.close()

if __name__ == "__main__":
    verify_system()