#!/usr/bin/env python3
"""Importe Assurance.xlsx dans la base de données (modèles dynamiques).

Crée les AssuranceColonne, AssuranceLigne (dont la ligne TOTAL) et
AssuranceCellule correspondant au fichier Excel. À exécuter une fois
après avoir initialisé la base.
"""
import os

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


def main():
    if not os.path.exists(XLSX_PATH):
        raise SystemExit(f"Fichier introuvable : {XLSX_PATH}")

    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    ws = wb["Assurance"]
    rows = list(ws.iter_rows(values_only=True))

    sub_headers = [rows[SUB_HEADER_ROW][c] for c in range(NUM_COLS)]

    with app.app_context():
        db.create_all()

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
            col = AssuranceColonne(
                groupe=groupe_pour_colonne(idx),
                en_tete=str(en_tete),
                ordre=idx,
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
