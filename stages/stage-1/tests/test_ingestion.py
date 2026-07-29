from __future__ import annotations

import csv
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import duckdb
import pytest

from ecommerce_pipeline.ingest import IngestionError, ingest_raw_data

EXPECTED_COLUMNS = {
    "customers": ("customer_id", "full_name", "email", "created_at"),
    "orders": ("order_id", "customer_id", "status", "ordered_at"),
    "order_items": (
        "order_item_id",
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
    ),
    "payments": ("payment_id", "order_id", "payment_method", "amount", "paid_at"),
}


@contextmanager
def read_database(path: Path) -> Iterator[duckdb.DuckDBPyConnection]:
    connection = duckdb.connect(str(path), read_only=True)
    try:
        yield connection
    finally:
        connection.close()


def table_snapshot(path: Path) -> dict[str, tuple[tuple[str, ...], ...]]:
    with read_database(path) as connection:
        return {
            table: tuple(
                connection.execute(f'SELECT * FROM raw."{table}" ORDER BY ALL').fetchall()
            )
            for table in EXPECTED_COLUMNS
        }


def source_rows(input_dir: Path, table: str) -> tuple[tuple[str, ...], ...]:
    with (input_dir / f"{table}.csv").open(newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        return tuple(tuple(row) for row in reader)


def test_creates_expected_raw_relations(input_dir: Path, output_path: Path) -> None:
    ingest_raw_data(input_dir, output_path)

    with read_database(output_path) as connection:
        relations = connection.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'raw'
            ORDER BY table_name
            """
        ).fetchall()

    assert relations == [
        ("customers",),
        ("order_items",),
        ("orders",),
        ("payments",),
    ]


@pytest.mark.parametrize("table", EXPECTED_COLUMNS)
def test_preserves_source_columns_and_values(
    input_dir: Path,
    output_path: Path,
    table: str,
) -> None:
    ingest_raw_data(input_dir, output_path)

    with read_database(output_path) as connection:
        column_metadata = connection.execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'raw' AND table_name = ?
            ORDER BY ordinal_position
            """,
            [table],
        ).fetchall()
        output_rows = connection.execute(
            f'SELECT * FROM raw."{table}" ORDER BY ALL'
        ).fetchall()

    assert column_metadata == [(column, "VARCHAR") for column in EXPECTED_COLUMNS[table]]
    assert output_rows == sorted(source_rows(input_dir, table))


def test_rejects_a_missing_source_file(input_dir: Path, output_path: Path) -> None:
    (input_dir / "payments.csv").unlink()

    with pytest.raises(IngestionError, match=r"payments\.csv"):
        ingest_raw_data(input_dir, output_path)


def test_rejects_an_unexpected_header(input_dir: Path, output_path: Path) -> None:
    orders_path = input_dir / "orders.csv"
    rows = orders_path.read_text(encoding="utf-8").splitlines()
    rows[0] = "order_id,customer_id,ordered_at"
    orders_path.write_text("\n".join(rows) + "\n", encoding="utf-8")

    with pytest.raises(IngestionError, match=r"orders\.csv.*status"):
        ingest_raw_data(input_dir, output_path)


def test_reexecution_is_deterministic(input_dir: Path, output_path: Path) -> None:
    ingest_raw_data(input_dir, output_path)
    first_snapshot = table_snapshot(output_path)

    ingest_raw_data(input_dir, output_path)
    second_snapshot = table_snapshot(output_path)

    assert second_snapshot == first_snapshot
