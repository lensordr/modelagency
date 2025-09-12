"""
Database Optimization for Analytics Performance
Includes indexing, query optimization, and data archiving strategies
"""

from sqlalchemy import create_engine, text, Index
from sqlalchemy.orm import sessionmaker
from models import Base, AnalyticsRecord, engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_analytics_indexes():
    """Create indexes to optimize analytics queries"""
    try:
        with engine.connect() as conn:
            # Index for date-based queries (most common)
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_analytics_checkout_date 
                ON analytics_records(checkout_date)
            """))
            
            # Composite index for item analysis
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_analytics_item_date 
                ON analytics_records(item_name, checkout_date)
            """))
            
            # Index for category analysis
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_analytics_category_date 
                ON analytics_records(item_category, checkout_date)
            """))
            
            # Index for waiter performance
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_analytics_waiter_date 
                ON analytics_records(waiter_id, checkout_date)
            """))
            
            # Composite index for top items queries
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_analytics_quantity_date 
                ON analytics_records(quantity, checkout_date DESC)
            """))
            
            conn.commit()
            logger.info("Analytics indexes created successfully")
            
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

def create_summary_tables():
    """Create pre-aggregated summary tables for faster queries"""
    try:
        with engine.connect() as conn:
            # Daily summary table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS daily_analytics_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    summary_date DATE NOT NULL,
                    total_orders INTEGER DEFAULT 0,
                    total_revenue REAL DEFAULT 0,
                    total_tips REAL DEFAULT 0,
                    unique_items INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(summary_date)
                )
            """))
            
            # Item daily summary
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS item_daily_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    summary_date DATE NOT NULL,
                    item_name TEXT NOT NULL,
                    item_category TEXT NOT NULL,
                    total_quantity INTEGER DEFAULT 0,
                    total_revenue REAL DEFAULT 0,
                    orders_count INTEGER DEFAULT 0,
                    avg_price REAL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(summary_date, item_name)
                )
            """))
            
            # Category daily summary
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS category_daily_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    summary_date DATE NOT NULL,
                    category TEXT NOT NULL,
                    total_quantity INTEGER DEFAULT 0,
                    total_revenue REAL DEFAULT 0,
                    unique_items INTEGER DEFAULT 0,
                    orders_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(summary_date, category)
                )
            """))
            
            conn.commit()
            logger.info("Summary tables created successfully")
            
    except Exception as e:
        logger.error(f"Error creating summary tables: {e}")

def update_daily_summaries(target_date=None):
    """Update daily summary tables with aggregated data"""
    from datetime import date, datetime
    
    if target_date is None:
        target_date = date.today()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    
    try:
        with engine.connect() as conn:
            # Update daily analytics summary
            conn.execute(text("""
                INSERT OR REPLACE INTO daily_analytics_summary 
                (summary_date, total_orders, total_revenue, total_tips, unique_items)
                SELECT 
                    DATE(checkout_date) as summary_date,
                    COUNT(DISTINCT checkout_date) as total_orders,
                    SUM(total_price) as total_revenue,
                    SUM(tip_amount) as total_tips,
                    COUNT(DISTINCT item_name) as unique_items
                FROM analytics_records 
                WHERE DATE(checkout_date) = :target_date
                GROUP BY DATE(checkout_date)
            """), {"target_date": target_date})
            
            # Update item daily summary
            conn.execute(text("""
                INSERT OR REPLACE INTO item_daily_summary 
                (summary_date, item_name, item_category, total_quantity, total_revenue, orders_count, avg_price)
                SELECT 
                    DATE(checkout_date) as summary_date,
                    item_name,
                    item_category,
                    SUM(quantity) as total_quantity,
                    SUM(total_price) as total_revenue,
                    COUNT(DISTINCT checkout_date) as orders_count,
                    AVG(unit_price) as avg_price
                FROM analytics_records 
                WHERE DATE(checkout_date) = :target_date
                GROUP BY DATE(checkout_date), item_name, item_category
            """), {"target_date": target_date})
            
            # Update category daily summary
            conn.execute(text("""
                INSERT OR REPLACE INTO category_daily_summary 
                (summary_date, category, total_quantity, total_revenue, unique_items, orders_count)
                SELECT 
                    DATE(checkout_date) as summary_date,
                    item_category as category,
                    SUM(quantity) as total_quantity,
                    SUM(total_price) as total_revenue,
                    COUNT(DISTINCT item_name) as unique_items,
                    COUNT(DISTINCT checkout_date) as orders_count
                FROM analytics_records 
                WHERE DATE(checkout_date) = :target_date
                GROUP BY DATE(checkout_date), item_category
            """), {"target_date": target_date})
            
            conn.commit()
            logger.info(f"Daily summaries updated for {target_date}")
            
    except Exception as e:
        logger.error(f"Error updating daily summaries: {e}")

def archive_old_data(days_to_keep=365):
    """Archive old analytics data to improve performance"""
    from datetime import date, timedelta
    
    cutoff_date = date.today() - timedelta(days=days_to_keep)
    
    try:
        with engine.connect() as conn:
            # Create archive table if it doesn't exist
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS analytics_records_archive (
                    id INTEGER PRIMARY KEY,
                    checkout_date DATETIME NOT NULL,
                    table_number INTEGER NOT NULL,
                    waiter_id INTEGER,
                    item_name TEXT NOT NULL,
                    item_category TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    total_price REAL NOT NULL,
                    tip_amount REAL DEFAULT 0,
                    archived_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Move old records to archive
            result = conn.execute(text("""
                INSERT INTO analytics_records_archive 
                SELECT *, CURRENT_TIMESTAMP as archived_at
                FROM analytics_records 
                WHERE DATE(checkout_date) < :cutoff_date
            """), {"cutoff_date": cutoff_date})
            
            archived_count = result.rowcount
            
            # Delete archived records from main table
            conn.execute(text("""
                DELETE FROM analytics_records 
                WHERE DATE(checkout_date) < :cutoff_date
            """), {"cutoff_date": cutoff_date})
            
            conn.commit()
            logger.info(f"Archived {archived_count} old records (older than {cutoff_date})")
            
    except Exception as e:
        logger.error(f"Error archiving data: {e}")

def optimize_database():
    """Run database optimization commands"""
    try:
        with engine.connect() as conn:
            # Analyze tables for query optimization
            conn.execute(text("ANALYZE"))
            
            # Vacuum to reclaim space and optimize
            conn.execute(text("VACUUM"))
            
            logger.info("Database optimization completed")
            
    except Exception as e:
        logger.error(f"Error optimizing database: {e}")

def get_database_stats():
    """Get database statistics for monitoring"""
    try:
        with engine.connect() as conn:
            # Get table sizes
            stats = {}
            
            result = conn.execute(text("""
                SELECT name, 
                       (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=m.name) as table_count
                FROM sqlite_master m WHERE type='table'
            """))
            
            for row in result:
                table_name = row[0]
                if table_name.startswith('analytics'):
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    stats[table_name] = count_result.scalar()
            
            # Get index information
            index_result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name LIKE 'idx_analytics%'
            """))
            
            stats['indexes'] = [row[0] for row in index_result]
            
            return stats
            
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {}

def setup_optimization():
    """Setup all optimization features"""
    logger.info("Setting up database optimization...")
    
    create_analytics_indexes()
    create_summary_tables()
    update_daily_summaries()
    optimize_database()
    
    stats = get_database_stats()
    logger.info(f"Optimization complete. Database stats: {stats}")

if __name__ == "__main__":
    setup_optimization()