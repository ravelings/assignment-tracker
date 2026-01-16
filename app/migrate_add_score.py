"""
Database migration script to add score column to assignments table
Run this script to update the database schema
"""
import sqlite3
import os

# Path to the database
DB_PATH = "C:/Users/ravel/Documents/Coding/Assignment Tracker/assignment-tracker/app/Database/database.db"

def migrate():
    """Add score column to assignments table if it doesn't exist"""
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if score column already exists
        cursor.execute("PRAGMA table_info(assignments)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'score' in columns:
            print("Score column already exists. No migration needed.")
            conn.close()
            return True
        
        # Add score column
        print("Adding score column to assignments table...")
        cursor.execute("ALTER TABLE assignments ADD COLUMN score REAL")
        conn.commit()
        
        print("Migration completed successfully!")
        print("Score column added to assignments table.")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Starting database migration...")
    print(f"Database path: {DB_PATH}")
    print("-" * 50)
    
    success = migrate()
    
    print("-" * 50)
    if success:
        print("✓ Migration completed successfully!")
    else:
        print("✗ Migration failed. Please check the errors above.")
