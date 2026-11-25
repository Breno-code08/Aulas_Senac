"""Exporta ou restaura o banco MySQL do Conectta Serra."""

import argparse
from datetime import datetime
from pathlib import Path
import os

import pymysql
from dotenv import load_dotenv
from sqlalchemy.engine import make_url

from iniciar import ROOT


def connection_args():
    load_dotenv(ROOT / ".env")

    url = make_url(
        os.getenv(
            "DATABASE_URL",
            "mysql+pymysql://root@127.0.0.1:3306/conectta?charset=utf8mb4",
        )
    )
    if not url.drivername.startswith("mysql"):
        raise RuntimeError("DATABASE_URL deve apontar para um banco MySQL.")

    return {
        "host": url.host or "127.0.0.1",
        "port": url.port or 3306,
        "user": url.username or "root",
        "password": url.password or "",
        "database": url.database,
        "charset": "utf8mb4",
    }


def quote_value(connection, value):
    if value is None:
        return "NULL"
    if isinstance(value, bytes):
        return "0x" + value.hex()
    if isinstance(value, (int, float)):
        return str(value)
    return connection.escape(value)


def split_sql_statements(sql):
    statement = []
    quote = None
    index = 0
    while index < len(sql):
        character = sql[index]
        if quote:
            statement.append(character)
            if character == "\\" and index + 1 < len(sql):
                statement.append(sql[index + 1])
                index += 2
                continue
            if character == quote and index + 1 < len(sql) and sql[index + 1] == quote:
                statement.append(sql[index + 1])
                index += 2
                continue
            if character == quote:
                quote = None
        elif character in ("'", '"', "`"):
            quote = character
            statement.append(character)
        elif sql.startswith("--", index) and (
            index + 2 == len(sql) or sql[index + 2].isspace()
        ):
            newline = sql.find("\n", index)
            index = len(sql) if newline == -1 else newline + 1
            continue
        elif character == "#":
            newline = sql.find("\n", index)
            index = len(sql) if newline == -1 else newline + 1
            continue
        elif sql.startswith("/*", index):
            comment_end = sql.find("*/", index + 2)
            if comment_end == -1:
                raise ValueError("Comentário SQL não foi fechado.")
            index = comment_end + 2
            continue
        elif character == ";":
            current = "".join(statement).strip()
            if current:
                yield current
            statement = []
        else:
            statement.append(character)
        index += 1

    current = "".join(statement).strip()
    if current:
        yield current


def export_database(output):
    args = connection_args()
    connection = pymysql.connect(**args)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
            tables = [row[0] for row in cursor.fetchall()]

        lines = [
            "-- Conectta Serra MySQL backup",
            "-- Generated " + datetime.now().isoformat(timespec="seconds"),
            "SET FOREIGN_KEY_CHECKS=0;",
            "SET NAMES utf8mb4;",
        ]
        with connection.cursor() as cursor:
            for table in tables:
                cursor.execute("SHOW CREATE TABLE `" + table.replace("`", "``") + "`")
                create_table = cursor.fetchone()[1]
                lines.append("DROP TABLE IF EXISTS `" + table.replace("`", "``") + "`;")
                lines.append(create_table + ";")

                cursor.execute("SELECT * FROM `" + table.replace("`", "``") + "`")
                rows = cursor.fetchall()
                if not rows:
                    continue
                column_names = [column[0] for column in cursor.description]
                columns = ", ".join("`" + name.replace("`", "``") + "`" for name in column_names)
                for row in rows:
                    values = ", ".join(quote_value(connection, value) for value in row)
                    lines.append(
                        "INSERT INTO `" + table.replace("`", "``") + "` (" + columns + ") VALUES (" + values + ");"
                    )
        lines.append("SET FOREIGN_KEY_CHECKS=1;")
        Path(output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    finally:
        connection.close()


def import_database(input_file):
    args = connection_args()
    connection = pymysql.connect(**args)
    try:
        sql = Path(input_file).read_text(encoding="utf-8")
        with connection.cursor() as cursor:
            for statement in split_sql_statements(sql):
                if not statement.startswith("--"):
                    cursor.execute(statement)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action", required=True)

    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("output", nargs="?", default="conectta-serra-backup.sql")

    import_parser = subparsers.add_parser("import")
    import_parser.add_argument("input")

    args = parser.parse_args()
    if args.action == "export":
        export_database(args.output)
        print("Backup criado: " + str(Path(args.output).resolve()))
    else:
        import_database(args.input)
        print("Backup restaurado: " + str(Path(args.input).resolve()))


if __name__ == "__main__":
    main()
