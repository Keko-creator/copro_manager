#!/usr/bin/env python3
"""Importe Assurance.xlsx dans la base de données (modèles dynamiques).

Crée les AssuranceColonne, AssuranceLigne (dont la ligne TOTAL) et
AssuranceCellule correspondant au fichier Excel. À exécuter une fois
après avoir initialisé la base.
"""
import os
import json

import openpyxl

from app import app, db, AssuranceColonne, AssuranceLigne, AssuranceCellule

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
XLSX_PATH = os.path.join(BASE_DIR, "Assurance.xlsx")

GROUP_HEADER_ROW = 8
SUB_HEADER_ROW = 9
FIRST_DATA_ROW = 10
NUM_COLS = 41


def groupe_pour_colonne(idx):
    if idx < 5:
        return "Copropriété"
    if idx < 9:
        return "Contrat"
    return "Tarif"


def cellule_valeur(v):
    if v is None:
        return ""
    if isinstance(v, float):
        if v != v:  # NaN
            return ""
        if v.is_integer():
            return str(int(v))
        return str(round(v, 4))
    return str(v).strip()


# Mapping index de colonne -> (type de formule, parametres).
# Règles reconstituées depuis les formules Excel :
#   - prix_m2 : valeur = cotisation_annee / superficie
#   - evolution_n : valeur = (cotisation_N - cotisation_N-1) / cotisation_N-1
#   - evolution_base : valeur = (cotisation_N - cotisation_base) / cotisation_base
# Les "cotisation_base" = colonne 11 (Cotisation de base TTC).
# La superficie = colonne 9.
FORMULES = {
    12: ('prix_m2', {'cotisation': 11, 'superficie': 9}),
    17: ('prix_m2', {'cotisation': 15, 'superficie': 9}),   # 2022
    21: ('prix_m2', {'cotisation': 19, 'superficie': 9}),   # 2023
    24: ('prix_m2', {'cotisation': 23, 'superficie': 9}),   # 2024
    29: ('prix_m2', {'cotisation': 28, 'superficie': 9}),   # 2025
    33: ('prix_m2', {'cotisation': 32, 'superficie': 9}),   # 2025 avenant
    36: ('prix_m2', {'cotisation': 35, 'superficie': 9}),   # 2026
    16: ('evolution_base', {'annee': 15, 'base': 11}),      # Base-2022
    20: ('evolution_n', {'annee': 19, 'ref': 15}),          # 2022-2023
    25: ('evolution_n', {'annee': 23, 'ref': 19}),          # 2023-2024
    26: ('evolution_base', {'annee': 23, 'base': 11}),      # Base-2024
    30: ('evolution_n', {'annee': 28, 'ref': 23}),          # 2024-2025
    31: ('evolution_base', {'annee': 28, 'base': 11}),      # Base-2025
    37: ('evolution_n', {'annee': 35, 'ref': 32}),          # 2025-2026 (ref = avenant 2025)
    38: ('evolution_base', {'annee': 35, 'base': 11}),      # Base-2026
}


def main():
    if not os.path.exists(XLSX_PATH):
        raise SystemExit(f"Fichier introuvable : {XLSX_PATH}")

    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    ws = wb["Assurance"]
    rows = list(ws.iter_rows(values_only=True))

    sub_headers = [rows[SUB_HEADER_ROW][c] for c in range(NUM_COLS)]

    with app.app_context():
        db.create_all()

        # Ajoute les colonnes formule/formule_params si elles manquent
        # (db.create_all() ne modifie pas une table existante).
        with db.engine.begin() as conn:
            cols = [r[1] for r in conn.exec_driver_sql(
                "PRAGMA table_info(assurance_colonnes)")]
            if 'formule' not in cols:
                conn.exec_driver_sql(
                    "ALTER TABLE assurance_colonnes ADD COLUMN formule VARCHAR(50)")
            if 'formule_params' not in cols:
                conn.exec_driver_sql(
                    "ALTER TABLE assurance_colonnes ADD COLUMN formule_params TEXT")

        # Réinitialise les tables assurance
        AssuranceCellule.query.delete()
        AssuranceLigne.query.delete()
        AssuranceColonne.query.delete()
        db.session.commit()

        # Colonnes
        colonnes = []
        for idx in range(NUM_COLS):
            en_tete = sub_headers[idx]
            if en_tete is None:
                en_tete = ""
            formule = None
            formule_params = None
            if idx in FORMULES:
                ftype, fparams = FORMULES[idx]
                formule = ftype
                formule_params = json.dumps(fparams)
            col = AssuranceColonne(
                groupe=groupe_pour_colonne(idx),
                en_tete=str(en_tete),
                ordre=idx,
                formule=formule,
                formule_params=formule_params,
            )
            db.session.add(col)
            colonnes.append(col)
        db.session.flush()

        # Lignes de données + ligne TOTAL
        ordre_ligne = 0
        for r in range(FIRST_DATA_ROW, len(rows)):
            first = rows[r][0]
            if first is None:
                continue
            est_total = str(first).strip().upper() == "TOTAL"
            ligne = AssuranceLigne(ordre=ordre_ligne, est_total=est_total)
            db.session.add(ligne)
            db.session.flush()
            ordre_ligne += 1
            for idx in range(NUM_COLS):
                valeur = cellule_valeur(rows[r][idx])
                cellule = AssuranceCellule(
                    ligne_id=ligne.id,
                    colonne_id=colonnes[idx].id,
                    valeur=valeur,
                )
                db.session.add(cellule)

        db.session.commit()
        nb_lignes = AssuranceLigne.query.count()
        nb_colonnes = AssuranceColonne.query.count()
        nb_cellules = AssuranceCellule.query.count()
        print(f"✅ Import Assurance : {nb_lignes} lignes, {nb_colonnes} colonnes, {nb_cellules} cellules")


if __name__ == "__main__":
    main()
