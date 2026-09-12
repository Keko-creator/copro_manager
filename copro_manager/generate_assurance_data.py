#!/usr/bin/env python3
"""Génère assurance_data.json à partir de Assurance.xlsx.

Lit le classeur Excel Assurance.xlsx et produit un fichier JSON contenant
les en-têtes (groupes + sous-colonnes), les lignes de données des copropriétés
et la ligne TOTAL, utilisés par la page /contrats/assurance.
"""
import json
import os

import openpyxl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
XLSX_PATH = os.path.join(BASE_DIR, "Assurance.xlsx")
JSON_PATH = os.path.join(BASE_DIR, "assurance_data.json")

GROUP_HEADER_ROW = 8
SUB_HEADER_ROW = 9
FIRST_DATA_ROW = 10
NUM_COLS = 41


def clean(value):
    if value is None:
        return ""
    if isinstance(value, float):
        if value != value:  # NaN
            return ""
        if value.is_integer():
            return int(value)
        return round(value, 4)
    return value


def main():
    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    ws = wb["Assurance"]
    rows = list(ws.iter_rows(values_only=True))

    group_headers = [clean(rows[GROUP_HEADER_ROW][c]) for c in range(NUM_COLS)]
    sub_headers = [clean(rows[SUB_HEADER_ROW][c]) for c in range(NUM_COLS)]

    data_rows = []
    total_row = None
    for r in range(FIRST_DATA_ROW, len(rows)):
        first = rows[r][0]
        if first is None:
            continue
        values = [clean(rows[r][c]) for c in range(NUM_COLS)]
        if str(first).strip().upper() == "TOTAL":
            total_row = values
        else:
            data_rows.append(values)

    payload = {
        "group_headers": group_headers,
        "sub_headers": sub_headers,
        "rows": data_rows,
        "total_row": total_row,
    }

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Généré {JSON_PATH} : {len(data_rows)} copropriétés + ligne TOTAL ({NUM_COLS} colonnes)")


if __name__ == "__main__":
    main()
