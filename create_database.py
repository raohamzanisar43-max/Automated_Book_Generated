import psycopg2
import sys

def create_database():
    try:
        # Connect to PostgreSQL default database
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="admin123",
            database="postgres"  # Connect to default postgres database first
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create the automated_book database
        cursor.execute("CREATE DATABASE automated_book;")
        print("Database 'automated_book' created successfully!")
        
        cursor.close()
        conn.close()
        
    except psycopg2.errors.DuplicateDatabase:
        print("Database 'automated_book' already exists!")
    except Exception as e:
        print(f"Error creating database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_database()
