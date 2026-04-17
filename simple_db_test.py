import psycopg2

def test_connection():
    try:
        # Test direct connection to the automated_book database
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="admin123",
            database="automated_book"
        )
        cursor = conn.cursor()
        
        # Test a simple query
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        print(f"Database connection test successful: {result}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
