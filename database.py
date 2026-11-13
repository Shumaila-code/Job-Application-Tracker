
import sqlite3

def create_database():
    connection = sqlite3.connect("jobs.db")
    cursor = connection.cursor()

    # Create table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # Get existing columns
    cursor.execute("PRAGMA table_info(jobs)")
    existing_columns = [
        column[1] for column in cursor.fetchall()
    ]

    # New columns to add
    new_columns = {
        "location": "TEXT",
        "salary": "TEXT",
        "application_date": "TEXT",
        "job_url": "TEXT",
        "notes": "TEXT",
        "follow_up_date": "TEXT"
    }

    # Add only missing columns
    for column_name, column_type in new_columns.items():
        if column_name not in existing_columns:
            cursor.execute(
                f"ALTER TABLE jobs ADD COLUMN "
                f"{column_name} {column_type}"
            )
            print(f"Added column: {column_name}")

    connection.commit()
    connection.close()

    print("Database updated successfully!")


if __name__ == "__main__":
    create_database()
