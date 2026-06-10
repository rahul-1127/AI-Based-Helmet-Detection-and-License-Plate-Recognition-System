import mysql.connector

def test_connection():
    try:
        # Update these credentials to match your MySQL Workbench setup
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="Koti@9247",  # 👈 Put your password here
            database="rider_db"  # 👈 Put your database name here
        )

        if conn.is_connected():
            print("✅ Successfully connected to the MySQL database!")
            conn.close()

    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")

if __name__ == "__main__":
    test_connection()