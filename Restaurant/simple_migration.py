#!/usr/bin/env python3
"""
Simple migration script to add hotel fields.
This version uses a more direct approach.
"""

import os
import sys

def run_migration():
    """Run the migration using Heroku CLI"""
    
    # SQL commands to add the columns
    sql_commands = [
        "ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS business_type VARCHAR(20) DEFAULT 'restaurant';",
        "ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS room_prefix VARCHAR(10) DEFAULT '';"
    ]
    
    print("🚀 Running hotel fields migration via Heroku CLI...")
    
    for i, sql in enumerate(sql_commands, 1):
        print(f"Step {i}: {sql}")
        
        # Use heroku pg:psql to run the command
        cmd = f'heroku pg:psql --app tablelink-space -c "{sql}"'
        
        print(f"Executing: {cmd}")
        result = os.system(cmd)
        
        if result == 0:
            print(f"✅ Step {i} completed successfully")
        else:
            print(f"❌ Step {i} failed with exit code {result}")
            return False
    
    print("🎉 Migration completed!")
    return True

def verify_migration():
    """Verify the migration worked"""
    print("🔍 Verifying migration...")
    
    verify_sql = "SELECT column_name FROM information_schema.columns WHERE table_name = 'restaurants' AND column_name IN ('business_type', 'room_prefix');"
    
    cmd = f'heroku pg:psql --app tablelink-space -c "{verify_sql}"'
    print(f"Verification command: {cmd}")
    
    result = os.system(cmd)
    
    if result == 0:
        print("✅ Verification completed - check output above")
        return True
    else:
        print("❌ Verification failed")
        return False

if __name__ == "__main__":
    print("Starting hotel migration with Heroku CLI...")
    
    if run_migration():
        verify_migration()
        print("✅ Hotel support migration process completed!")
    else:
        print("❌ Migration failed!")
        sys.exit(1)