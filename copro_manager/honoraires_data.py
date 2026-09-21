# -*- coding: utf-8 -*-
"""Données du tableau « Honoraire agate » (extraites du fichier Excel
« Honoraire agate.xlsx », feuille « HONORAIRE AGATE »).

Une fois importées en base via _importer_honoraires(), le fichier Excel
peut être supprimé : les données vivent dans la table honoraire_lignes.

Colonnes :
  numero      : N° de copro
  mise_copro  : Mise en copro (date ISO)
  fin_contrat : Fin de contrat (date ISO)
  type        : Type de facturation (Classique / Forfait / ASL / Spécifique)
  logements   : Logements
  tarif_s1    : € TTC / LP 1er semestre
  tarif_s2    : € TTC / LP 2e semestre
  t12         : € TTC 1er et 2e Trimestre (calculé : tarif_s1 * logements / 4)
  t34         : € TTC 3e et 4e Trimestre (calculé : tarif_s2 * logements / 4)
  total_ttc   : Total € TTC (calculé : t12 * 2 + t34 * 2)
  total_ht    : Total € HT (calculé : total_ttc / 1.2)
"""

HONORAIRE_DATA = [
    {'numero': 1, 'mise_copro': '2021-05-06', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 32, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 1296, 't34': 1344, 'total_ttc': 5280, 'total_ht': 4400},
    {'numero': 2, 'mise_copro': '2021-04-01', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 36, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 1458, 't34': 1512, 'total_ttc': 5940, 'total_ht': 4950},
    {'numero': 3, 'mise_copro': '2022-04-21', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 33, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 1336.5, 't34': 1386, 'total_ttc': 5445, 'total_ht': 4537.5},
    {'numero': 4, 'mise_copro': '2025-07-01', 'fin_contrat': '2024-06-30', 'type': 'ASL', 'logements': 12, 'tarif_s1': 45, 'tarif_s2': 45, 't12': 135, 't34': 135, 'total_ttc': 540, 'total_ht': 450},
    {'numero': 5, 'mise_copro': '2021-06-30', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 10, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 405, 't34': 420, 'total_ttc': 1650, 'total_ht': 1375},
    {'numero': 6, 'mise_copro': '2021-08-18', 'fin_contrat': '2023-06-30', 'type': 'Forfait', 'logements': 6, 'tarif_s1': 200, 'tarif_s2': 200, 't12': 300, 't34': 300, 'total_ttc': 1200, 'total_ht': 1000},
    {'numero': 7, 'mise_copro': '2022-03-24', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 30, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 1215, 't34': 1260, 'total_ttc': 4950, 'total_ht': 4125},
    {'numero': 8, 'mise_copro': '2021-12-21', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 15, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 607.5, 't34': 630, 'total_ttc': 2475, 'total_ht': 2062.5},
    {'numero': 9, 'mise_copro': '2022-05-13', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 17, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 688.5, 't34': 714, 'total_ttc': 2805, 'total_ht': 2337.5},
    {'numero': 10, 'mise_copro': '2022-04-29', 'fin_contrat': '2023-12-31', 'type': 'Classique', 'logements': 14, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 588, 't34': 588, 'total_ttc': 2352, 'total_ht': 1960},
    {'numero': 11, 'mise_copro': '2022-06-07', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 20, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 810, 't34': 840, 'total_ttc': 3300, 'total_ht': 2750},
    {'numero': 12, 'mise_copro': '2022-07-21', 'fin_contrat': '2023-12-31', 'type': 'Forfait', 'logements': 6, 'tarif_s1': 200, 'tarif_s2': 200, 't12': 300, 't34': 300, 'total_ttc': 1200, 'total_ht': 1000},
    {'numero': 13, 'mise_copro': '2022-08-29', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 15, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 607.5, 't34': 630, 'total_ttc': 2475, 'total_ht': 2062.5},
    {'numero': 14, 'mise_copro': '2022-09-02', 'fin_contrat': '2023-12-31', 'type': 'Forfait', 'logements': 4, 'tarif_s1': 300, 'tarif_s2': 300, 't12': 300, 't34': 300, 'total_ttc': 1200, 'total_ht': 1000},
    {'numero': 15, 'mise_copro': '2022-09-07', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 20, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 810, 't34': 840, 'total_ttc': 3300, 'total_ht': 2750},
    {'numero': 16, 'mise_copro': '2022-11-16', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 38, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 1539, 't34': 1596, 'total_ttc': 6270, 'total_ht': 5225},
    {'numero': 17, 'mise_copro': '2023-02-24', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 10, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 405, 't34': 420, 'total_ttc': 1650, 'total_ht': 1375},
    {'numero': 18, 'mise_copro': '2023-03-03', 'fin_contrat': '2023-12-31', 'type': 'Classique', 'logements': 9, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 378, 't34': 378, 'total_ttc': 1512, 'total_ht': 1260},
    {'numero': 19, 'mise_copro': '2023-03-10', 'fin_contrat': '2023-12-31', 'type': 'Forfait', 'logements': 2, 'tarif_s1': 600, 'tarif_s2': 600, 't12': 300, 't34': 300, 'total_ttc': 1200, 'total_ht': 1000},
    {'numero': 20, 'mise_copro': '2023-06-12', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 17, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 688.5, 't34': 714, 'total_ttc': 2805, 'total_ht': 2337.5},
    {'numero': 21, 'mise_copro': '2023-06-12', 'fin_contrat': '2023-12-31', 'type': 'Classique', 'logements': 12, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 504, 't34': 504, 'total_ttc': 2016, 'total_ht': 1680},
    {'numero': 22, 'mise_copro': '2023-06-15', 'fin_contrat': '2023-12-31', 'type': 'Forfait', 'logements': 4, 'tarif_s1': 300, 'tarif_s2': 300, 't12': 300, 't34': 300, 'total_ttc': 1200, 'total_ht': 1000},
    {'numero': 23, 'mise_copro': '2023-06-27', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 31, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 1255.5, 't34': 1302, 'total_ttc': 5115, 'total_ht': 4262.5},
    {'numero': 24, 'mise_copro': '2023-07-06', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 24, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 972, 't34': 1008, 'total_ttc': 3960, 'total_ht': 3300},
    {'numero': 25, 'mise_copro': '2023-07-10', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 17, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 688.5, 't34': 714, 'total_ttc': 2805, 'total_ht': 2337.5},
    {'numero': 26, 'mise_copro': '2023-07-14', 'fin_contrat': '2023-06-30', 'type': 'Spécifique', 'logements': None, 'tarif_s1': None, 'tarif_s2': None, 't12': 150, 't34': 150, 'total_ttc': 600, 'total_ht': 500},
    {'numero': 27, 'mise_copro': '2023-07-21', 'fin_contrat': '2023-06-30', 'type': 'Forfait', 'logements': 6, 'tarif_s1': 200, 'tarif_s2': 200, 't12': 300, 't34': 300, 'total_ttc': 1200, 'total_ht': 1000},
    {'numero': 28, 'mise_copro': '2023-07-24', 'fin_contrat': '2023-06-30', 'type': 'Forfait', 'logements': 6, 'tarif_s1': 200, 'tarif_s2': 200, 't12': 300, 't34': 300, 'total_ttc': 1200, 'total_ht': 1000},
    {'numero': 29, 'mise_copro': '2023-07-21', 'fin_contrat': '2023-06-30', 'type': 'ASL', 'logements': 5, 'tarif_s1': 108, 'tarif_s2': 108, 't12': 135, 't34': 135, 'total_ttc': 540, 'total_ht': 450},
    {'numero': 30, 'mise_copro': '2023-08-30', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 16, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 648, 't34': 672, 'total_ttc': 2640, 'total_ht': 2200},
    {'numero': 31, 'mise_copro': '2023-10-06', 'fin_contrat': '2023-06-30', 'type': 'Classique', 'logements': 34, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 1377, 't34': 1428, 'total_ttc': 5610, 'total_ht': 4675},
    {'numero': 32, 'mise_copro': '2024-02-26', 'fin_contrat': '2024-06-30', 'type': 'ASL', 'logements': 27, 'tarif_s1': 20, 'tarif_s2': 20, 't12': 135, 't34': 135, 'total_ttc': 540, 'total_ht': 450},
    {'numero': 33, 'mise_copro': '2023-11-21', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 22, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 891, 't34': 924, 'total_ttc': 3630, 'total_ht': 3025},
    {'numero': 34, 'mise_copro': '2023-12-18', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 28, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 1134, 't34': 1176, 'total_ttc': 4620, 'total_ht': 3850},
    {'numero': 35, 'mise_copro': '2024-01-12', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 9, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 364.5, 't34': 378, 'total_ttc': 1485, 'total_ht': 1237.5},
    {'numero': 36, 'mise_copro': '2024-01-16', 'fin_contrat': '2023-12-31', 'type': 'Forfait', 'logements': 6, 'tarif_s1': 200, 'tarif_s2': 200, 't12': 300, 't34': 300, 'total_ttc': 1200, 'total_ht': 1000},
    {'numero': 37, 'mise_copro': '2024-05-15', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 24, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 972, 't34': 1008, 'total_ttc': 3960, 'total_ht': 3300},
    {'numero': 38, 'mise_copro': '2024-06-20', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 26, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 1053, 't34': 1092, 'total_ttc': 4290, 'total_ht': 3575},
    {'numero': 39, 'mise_copro': '2024-07-02', 'fin_contrat': '2023-12-31', 'type': 'Forfait', 'logements': 6, 'tarif_s1': 200, 'tarif_s2': 200, 't12': 300, 't34': 300, 'total_ttc': 1200, 'total_ht': 1000},
    {'numero': 40, 'mise_copro': '2024-08-20', 'fin_contrat': '2023-12-31', 'type': 'Classique', 'logements': 2, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 84, 't34': 84, 'total_ttc': 336, 'total_ht': 280},
    {'numero': 41, 'mise_copro': '2024-08-22', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 20, 'tarif_s1': 162, 'tarif_s2': 168, 't12': 810, 't34': 840, 'total_ttc': 3300, 'total_ht': 2750},
    {'numero': 42, 'mise_copro': '2024-08-23', 'fin_contrat': '2023-12-31', 'type': 'Classique', 'logements': 8, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 336, 't34': 336, 'total_ttc': 1344, 'total_ht': 1120},
    {'numero': 44, 'mise_copro': '2024-09-27', 'fin_contrat': '2024-06-30', 'type': 'Forfait', 'logements': 6, 'tarif_s1': 200, 'tarif_s2': 200, 't12': 300, 't34': 300, 'total_ttc': 1200, 'total_ht': 1000},
    {'numero': 45, 'mise_copro': '2024-09-30', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 13, 'tarif_s1': 41.53846153846154, 'tarif_s2': 41.53846153846154, 't12': 135, 't34': 135, 'total_ttc': 540, 'total_ht': 450},
    {'numero': 46, 'mise_copro': '2024-10-14', 'fin_contrat': '2023-12-31', 'type': 'Classique', 'logements': 2, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 84, 't34': 84, 'total_ttc': 336, 'total_ht': 280},
    {'numero': 47, 'mise_copro': '2024-10-31', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 11, 'tarif_s1': 49.09090909090909, 'tarif_s2': 49.09090909090909, 't12': 135, 't34': 135, 'total_ttc': 540, 'total_ht': 450},
    {'numero': 48, 'mise_copro': '2024-11-13', 'fin_contrat': '2023-12-31', 'type': 'Classique', 'logements': 12, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 504, 't34': 504, 'total_ttc': 2016, 'total_ht': 1680},
    {'numero': 49, 'mise_copro': '2024-12-18', 'fin_contrat': '2023-12-31', 'type': 'Classique', 'logements': 2, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 84, 't34': 84, 'total_ttc': 336, 'total_ht': 280},
    {'numero': 50, 'mise_copro': '2025-02-19', 'fin_contrat': '2023-12-31', 'type': 'Classique', 'logements': 10, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 420, 't34': 420, 'total_ttc': 1680, 'total_ht': 1400},
    {'numero': 51, 'mise_copro': '2025-03-12', 'fin_contrat': '2023-12-31', 'type': 'Classique', 'logements': 15, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 630, 't34': 630, 'total_ttc': 2520, 'total_ht': 2100},
    {'numero': 52, 'mise_copro': '2025-04-17', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 24, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 1008, 't34': 1008, 'total_ttc': 4032, 'total_ht': 3360},
    {'numero': 53, 'mise_copro': '2025-05-16', 'fin_contrat': '2024-06-30', 'type': 'Forfait', 'logements': 6, 'tarif_s1': 200, 'tarif_s2': 200, 't12': 300, 't34': 300, 'total_ttc': 1200, 'total_ht': 1000},
    {'numero': 54, 'mise_copro': '2025-05-31', 'fin_contrat': '2023-12-31', 'type': 'Classique', 'logements': 12, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 504, 't34': 504, 'total_ttc': 2016, 'total_ht': 1680},
    {'numero': 55, 'mise_copro': '2025-07-04', 'fin_contrat': '2023-12-31', 'type': 'Classique', 'logements': 12, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 504, 't34': 504, 'total_ttc': 2016, 'total_ht': 1680},
    {'numero': 56, 'mise_copro': '2025-07-17', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 32, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 1344, 't34': 1344, 'total_ttc': 5376, 'total_ht': 4480},
    {'numero': 57, 'mise_copro': '2025-07-21', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 14, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 588, 't34': 588, 'total_ttc': 2352, 'total_ht': 1960},
    {'numero': 58, 'mise_copro': '2025-07-22', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 30, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 1260, 't34': 1260, 'total_ttc': 5040, 'total_ht': 4200},
    {'numero': 59, 'mise_copro': '2025-07-30', 'fin_contrat': '2023-12-31', 'type': 'Classique', 'logements': 12, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 504, 't34': 504, 'total_ttc': 2016, 'total_ht': 1680},
    {'numero': 60, 'mise_copro': '2025-07-31', 'fin_contrat': '2023-12-31', 'type': 'Forfait', 'logements': 6, 'tarif_s1': 200, 'tarif_s2': 200, 't12': 300, 't34': 300, 'total_ttc': 1200, 'total_ht': 1000},
    {'numero': 61, 'mise_copro': '2025-09-30', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 36, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 1512, 't34': 1512, 'total_ttc': 6048, 'total_ht': 5040},
    {'numero': 62, 'mise_copro': '2025-10-28', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 49, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 2058, 't34': 2058, 'total_ttc': 8232, 'total_ht': 6860},
    {'numero': 63, 'mise_copro': '2025-11-04', 'fin_contrat': '2024-06-30', 'type': 'ASL', 'logements': 17, 'tarif_s1': 31.764705882352942, 'tarif_s2': 31.764705882352942, 't12': 135, 't34': 135, 'total_ttc': 540, 'total_ht': 450},
    {'numero': 64, 'mise_copro': '2025-11-24', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 21, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 882, 't34': 882, 'total_ttc': 3528, 'total_ht': 2940},
    {'numero': 65, 'mise_copro': '2025-12-09', 'fin_contrat': '2023-12-31', 'type': 'Classique', 'logements': 10, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 420, 't34': 420, 'total_ttc': 1680, 'total_ht': 1400},
    {'numero': 66, 'mise_copro': '2025-12-15', 'fin_contrat': '2023-12-31', 'type': 'Classique', 'logements': 10, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 420, 't34': 420, 'total_ttc': 1680, 'total_ht': 1400},
    {'numero': 67, 'mise_copro': '2025-12-16', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 24, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 1008, 't34': 1008, 'total_ttc': 4032, 'total_ht': 3360},
    {'numero': 68, 'mise_copro': '2025-12-19', 'fin_contrat': '2023-12-31', 'type': 'Classique', 'logements': 12, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 504, 't34': 504, 'total_ttc': 2016, 'total_ht': 1680},
    {'numero': 69, 'mise_copro': '2025-12-30', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 28, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 1176, 't34': 1176, 'total_ttc': 4704, 'total_ht': 3920},
    {'numero': 70, 'mise_copro': '2025-01-21', 'fin_contrat': '2024-06-30', 'type': 'Classique', 'logements': 20, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 840, 't34': 840, 'total_ttc': 3360, 'total_ht': 2800},
    {'numero': 71, 'mise_copro': '2025-01-01', 'fin_contrat': '2024-06-30', 'type': 'ASL', 'logements': 3, 'tarif_s1': 180, 'tarif_s2': 180, 't12': 135, 't34': 135, 'total_ttc': 540, 'total_ht': 450},
    {'numero': 72, 'mise_copro': '2026-04-30', 'fin_contrat': '2023-12-31', 'type': 'Classique', 'logements': 14, 'tarif_s1': 168, 'tarif_s2': 168, 't12': 588, 't34': 588, 'total_ttc': 2352, 'total_ht': 1960},
]
