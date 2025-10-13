import os
import subprocess


def export_database(host, user, password, database, output_dir="db_exports"):
    """
    Exports a full MySQL database with schema and data and also creates a fresh schema dump.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    full_dump_file = os.path.join(output_dir, f"{database}_full.sql")
    fresh_schema_file = os.path.join(output_dir, f"{database}_schema_only.sql")

    # Full database dump (schema + data)
    print(f"[+] Exporting full database '{database}' to {full_dump_file} ...")
    full_cmd = f"mysqldump -h {host} -u {user} -p{password} {database} > {full_dump_file}"
    subprocess.run(full_cmd, shell=True, check=True)

    # Schema-only dump (without data)
    print(f"[+] Exporting schema only for '{database}' to {fresh_schema_file} ...")
    schema_cmd = f"mysqldump -h {host} -u {user} -p{password} --no-data {database} > {fresh_schema_file}"
    subprocess.run(schema_cmd, shell=True, check=True)

    print("[+] Export completed successfully!")
    print(f"Full database dump: {full_dump_file}")
    print(f"Fresh schema dump: {fresh_schema_file}")


if __name__ == "__main__":
    # host = input("Enter MySQL host (default: localhost): ") or "localhost"
    # user = input("Enter MySQL username: ")
    # password = getpass("Enter MySQL password: ")
    # database = input("Enter database name: ")

    # export_database(host, user, password, database)
    export_database("host_here", "username_here", "password_here", "database_name_here")
