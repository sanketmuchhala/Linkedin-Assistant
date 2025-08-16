#!/usr/bin/env python3
"""
Simple database migration to add new columns to existing database.
"""
import sqlite3
import os

def migrate_database():
    """Add new columns to the existing database."""
    db_path = "followup.db"
    
    if not os.path.exists(db_path):
        print("No existing database found. New database will be created with new schema.")
        return
    
    print("Migrating existing database...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(contacts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'request_reason' not in columns:
            cursor.execute("ALTER TABLE contacts ADD COLUMN request_reason TEXT")
            print("✓ Added request_reason column")
        
        if 'message_sent' not in columns:
            cursor.execute("ALTER TABLE contacts ADD COLUMN message_sent INTEGER DEFAULT 0")
            print("✓ Added message_sent column")
        
        if 'last_message_date' not in columns:
            cursor.execute("ALTER TABLE contacts ADD COLUMN last_message_date DATETIME")
            print("✓ Added last_message_date column")
        
        # Premium analytics columns
        premium_columns = [
            ('response_received', 'INTEGER DEFAULT 0'),
            ('response_date', 'DATETIME'),
            ('connection_strength', 'INTEGER DEFAULT 1'),
            ('industry', 'TEXT'),
            ('location', 'TEXT'),
            ('mutual_connections', 'INTEGER DEFAULT 0'),
            ('profile_views', 'INTEGER DEFAULT 0'),
            ('last_activity', 'DATETIME'),
            ('priority_level', 'TEXT DEFAULT "medium"'),
            ('follow_up_scheduled', 'DATETIME'),
            ('outreach_status', 'TEXT DEFAULT "pending"')
        ]
        
        for col_name, col_type in premium_columns:
            if col_name not in columns:
                cursor.execute(f"ALTER TABLE contacts ADD COLUMN {col_name} {col_type}")
                print(f"✓ Added {col_name} column")
        
        # Create new tables
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS outreach_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    contacts_added INTEGER DEFAULT 0,
                    messages_generated INTEGER DEFAULT 0,
                    messages_sent INTEGER DEFAULT 0,
                    responses_received INTEGER DEFAULT 0,
                    connections_made INTEGER DEFAULT 0,
                    response_rate INTEGER DEFAULT 0,
                    connection_rate INTEGER DEFAULT 0,
                    industry_stats TEXT,
                    best_performing_tone TEXT
                )
            """)
            print("✓ Created outreach_analytics table")
        except Exception as e:
            print(f"Note: outreach_analytics table may already exist: {e}")
        
        # Add message analytics columns
        try:
            cursor.execute("PRAGMA table_info(messages)")
            message_columns = [column[1] for column in cursor.fetchall()]
            
            message_analytics_columns = [
                ('was_sent', 'INTEGER DEFAULT 0'),
                ('sent_date', 'DATETIME'),
                ('response_received', 'INTEGER DEFAULT 0'),
                ('response_time_hours', 'INTEGER'),
                ('message_length', 'INTEGER')
            ]
            
            for col_name, col_type in message_analytics_columns:
                if col_name not in message_columns:
                    cursor.execute(f"ALTER TABLE messages ADD COLUMN {col_name} {col_type}")
                    print(f"✓ Added {col_name} to messages table")
        except Exception as e:
            print(f"Note: messages table updates: {e}")
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()