import asyncio
import os
from dotenv import load_dotenv
import libsql_client

load_dotenv()

async def main():
    url = os.getenv("TURSO_DATABASE_URL")
    token = os.getenv("TURSO_AUTH_TOKEN")
    
    # We will test synchronous wrapper since database.py uses sync functions
    client = libsql_client.create_client_sync(url=url, auth_token=token)
    
    # Test table creation
    client.execute("CREATE TABLE IF NOT EXISTS test_libsql (id INTEGER PRIMARY KEY, name TEXT)")
    
    # Test insertion
    client.execute("INSERT INTO test_libsql (name) VALUES (?)", ("test_name",))
    
    # Test fetching
    rs = client.execute("SELECT * FROM test_libsql")
    print(f"Columns: {rs.columns}")
    print(f"Rows: {rs.rows}")
    
    if rs.rows:
        row = rs.rows[0]
        print(f"Row by index: {row[1]}")
        try:
            print(f"Row by key: {row['name']}")
        except Exception as e:
            print(f"Error by key: {e}")
            
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
