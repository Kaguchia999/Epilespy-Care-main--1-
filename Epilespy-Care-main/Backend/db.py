import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))


def get_connection() -> mysql.connector.MySQLConnection:
    config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    }
    missing = [name for name, value in config.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing database configuration: "
            + ", ".join(missing)
            + ". Set these values in Backend/.env."
        )

    return mysql.connector.connect(
        **config,
    )