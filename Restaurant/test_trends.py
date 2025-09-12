#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db
from simple_analytics import get_simple_trends

def test_trends():
    db = next(get_db())
    try:
        print("Testing get_simple_trends...")
        trends = get_simple_trends(db, 7)
        print(f"Raw trends: {trends}")
        
        result = []
        for trend in trends:
            print(f"Processing trend: {trend}, type: {type(trend)}")
            result.append({
                "date": str(trend[0]),
                "orders": int(trend[1]),
                "revenue": float(trend[2] or 0)
            })
        
        print(f"Final result: {result}")
        return {"trends": result}
        
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()
        return {"trends": [], "error": str(e)}

if __name__ == "__main__":
    result = test_trends()
    print("Final output:", result)