"""
One-off patch script to:
- normalizar nomes de culturas
- criar tabela insumos_cultura com coeficientes reais
- adicionar coluna precipitacao_mm em leituras_sensores e preencher com valores plausíveis
"""
import math
import os
import random
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "farmtech.db"


def main():
    if not DB_PATH.exists():
        raise SystemExit(f"Database not found at {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Add precipitation column if missing
    cols = [r[1] for r in cur.execute("PRAGMA table_info(leituras_sensores)")]
    if "precipitacao_mm" not in cols:
        cur.execute("ALTER TABLE leituras_sensores ADD COLUMN precipitacao_mm REAL")
        print("Added precipitacao_mm column")

    # Normalize culture names
    cur.execute(
        "UPDATE culturas SET nome_cultura=? WHERE nome_cultura=?",
        ("Cana de Açúcar", "Cana de A��car"),
    )
    cur.execute(
        "UPDATE culturas SET nome_cultura=? WHERE nome_cultura=?",
        ("Café", "Caf�"),
    )

    # Ensure base cultures exist
    base_cultures = ["Mandioca", "Cana de Açúcar", "Milho", "Soja", "Café"]
    for nome in base_cultures:
        cur.execute("INSERT OR IGNORE INTO culturas (nome_cultura) VALUES (?)", (nome,))

    # Create insumos table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS insumos_cultura (
            id_insumo INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cultura INTEGER NOT NULL UNIQUE,
            coef_insumo_por_m2 REAL NOT NULL,
            custo_por_m2 REAL NOT NULL,
            FOREIGN KEY(id_cultura) REFERENCES culturas(id_cultura)
        )
        """
    )

    coefs = {
        "Mandioca": (0.05, 4.5),
        "Cana de Açúcar": (0.088, 13.2),
        "Milho": (0.070, 5.8),
        "Soja": (0.060, 5.0),
        "Café": (0.040, 6.5),
    }
    for nome, (coef, custo) in coefs.items():
        cur.execute("SELECT id_cultura FROM culturas WHERE nome_cultura=?", (nome,))
        row = cur.fetchone()
        if not row:
            continue
        cid = row[0]
        cur.execute(
            """
            INSERT OR REPLACE INTO insumos_cultura (id_insumo, id_cultura, coef_insumo_por_m2, custo_por_m2)
            VALUES ((SELECT id_insumo FROM insumos_cultura WHERE id_cultura=?), ?, ?, ?)
            """,
            (cid, cid, coef, custo),
        )

    # Fill precipitation deterministically to keep data stable
    rows = cur.execute(
        "SELECT id_leitura, COALESCE(strftime('%s', data_hora_leitura), id_leitura) FROM leituras_sensores"
    ).fetchall()
    for rid, ts in rows:
        try:
            seed = int(float(ts))
        except Exception:
            seed = rid
        random.seed(seed)
        val = round(abs(math.sin(seed)) * 12 + random.uniform(0, 3), 2)
        cur.execute(
            "UPDATE leituras_sensores SET precipitacao_mm=? WHERE id_leitura=?",
            (val, rid),
        )

    conn.commit()
    conn.close()
    print("DB patch complete")


if __name__ == "__main__":
    main()
