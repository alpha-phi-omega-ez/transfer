import csv
import json
import os

import mysql.connector


def main(db_configs, output_dir) -> None:
    for db_config in db_configs:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Get the list of tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        # Export each table to a CSV file
        for (table_name,) in tables:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            column_names = (
                [i[0] for i in cursor.description] if cursor.description else []
            )

            db_output_dir = os.path.join(output_dir, db_config["database"])
            os.makedirs(db_output_dir, exist_ok=True)

            csv_file_path = os.path.join(db_output_dir, f"{table_name}.csv")
            with open(csv_file_path, mode="w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(column_names)
                writer.writerows(rows)

        # Close the cursor and connection
        cursor.close()
        conn.close()


if __name__ == "__main__":
    # Read database configurations from dbs.json
    with open("dbs.json", "r") as file:
        db_configs = json.load(file)

    # Directory to save CSV files
    output_dir = "data/"
    os.makedirs(output_dir, exist_ok=True)

    main(db_configs, output_dir)
