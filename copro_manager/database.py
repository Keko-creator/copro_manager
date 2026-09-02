from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

# Modèle pour les copropriétés
class Copropriete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False)
    nom = db.Column(db.String(200), nullable=False)
    date_mise_copropriete = db.Column(db.Date)
    programme_neolia = db.Column(db.String(100))
    adresse = db.Column(db.String(300))
    ville = db.Column(db.String(100))
    immatriculation = db.Column(db.String(100))
    nombre_logements = db.Column(db.Integer)
    exercice_comptable = db.Column(db.String(20))  # Ex: "31-déc", "30-juin"
    gestionnaire = db.Column(db.String(50))  # Ex: "AJ", "KS"
    est_active = db.Column(db.Boolean, default=True)  # NOUVEAU: Statut actif/non géré

    # Relations
    fiche_immeuble = db.relationship('FicheImmeuble', backref='copropriete', uselist=False)
    contrats = db.relationship('Contrat', backref='copropriete', lazy=True)
    coproprietaires = db.relationship('Coproprietaire', backref='copropriete', lazy=True)
    assemblees_generales = db.relationship('AssembleeGenerale', backref='copropriete', lazy=True)
    resolutions_futures = db.relationship('ResolutionFuture', backref='copropriete', lazy=True)# Modèle pour la fiche immeuble
class FicheImmeuble(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    copropriete_id = db.Column(db.Integer, db.ForeignKey('copropriete.id'), unique=True, nullable=False)
    date_construction = db.Column(db.Date)
    date_arrete_compte = db.Column(db.Date)
    reference_neolia = db.Column(db.String(100))
    nom_commercial_vente_hlm = db.Column(db.String(200))
    nom_responsable_secteur = db.Column(db.String(200))
    nom_notaire = db.Column(db.String(200))
    designation_immeuble = db.Column(db.String(300))
    iban = db.Column(db.String(100))
    ics = db.Column(db.String(50))
    lien_dossier = db.Column(db.String(500))
    lien_budget = db.Column(db.String(500))

# Modèle pour les contrats (Fiche Technique)
class Contrat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    copropriete_id = db.Column(db.Integer, db.ForeignKey('copropriete.id'), nullable=False)
    type_contrat = db.Column(db.String(100))  # Ex: Nettoyage, Assurance, Eau, etc.
    nature = db.Column(db.String(200))  # Détail de la nature
    fournisseur = db.Column(db.String(200))
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)
    montant_annuel = db.Column(db.Float)

    prestations = db.relationship('Prestation', backref='contrat', lazy=True, cascade="all, delete-orphan")

# Modèle pour les prestations (liées aux contrats)
class Prestation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contrat_id = db.Column(db.Integer, db.ForeignKey('contrat.id'), nullable=False)
    libelle = db.Column(db.String(200))
    frequence = db.Column(db.String(50))  # Ex: Hebdomadaire, Mensuel, etc.
    prix_unitaire = db.Column(db.Float)
    quantite = db.Column(db.Integer)
    total = db.Column(db.Float)

# Modèle pour les copropriétaires
class Coproprietaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    copropriete_id = db.Column(db.Integer, db.ForeignKey('copropriete.id'), nullable=False)
    date_acquisition = db.Column(db.Date)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    numero_lot = db.Column(db.String(50))
    nature_lot = db.Column(db.String(100))
    email = db.Column(db.String(200))
    telephone = db.Column(db.String(50))
    est_residence_principale = db.Column(db.Boolean, default=False)
    est_loue = db.Column(db.Boolean, default=False)
    date_envoi_mail_accueil = db.Column(db.Date)
    lien_espace_client = db.Column(db.String(500))# Modèle pour les Assemblées Générales
class AssembleeGenerale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    copropriete_id = db.Column(db.Integer, db.ForeignKey('copropriete.id'), nullable=False)
    date = db.Column(db.Date)
    horaire_debut = db.Column(db.String(20))
    horaire_fin = db.Column(db.String(20))
    lieu = db.Column(db.String(200))
    lien_pv = db.Column(db.String(500))
    comptes_approuves = db.Column(db.Boolean, default=False)
    montant_depenses_exercice_cloture = db.Column(db.Float)
    montant_budget_exercice_cloture = db.Column(db.Float)
    montant_budget_exercice_en_cours = db.Column(db.Float)
    montant_budget_exercice_a_venir = db.Column(db.Float)
    honoraires_syndic = db.Column(db.Float)
    periode_honoraires_syndic = db.Column(db.String(100))

    points_a_retenir = db.relationship('PointARetenir', backref='assemblee_generale', lazy=True, cascade="all, delete-orphan")
    budgets_travaux = db.relationship('BudgetTravaux', backref='assemblee_generale', lazy=True, cascade="all, delete-orphan")

# Modèle pour les points à retenir (liés aux AG)
class PointARetenir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ag_id = db.Column(db.Integer, db.ForeignKey('assemblee_generale.id'), nullable=False)
    description = db.Column(db.String(500))

# Modèle pour les budgets travaux (liés aux AG)
class BudgetTravaux(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ag_id = db.Column(db.Integer, db.ForeignKey('assemblee_generale.id'), nullable=False)
    nom_travaux = db.Column(db.String(200))
    entreprise_retenue = db.Column(db.String(200))
    montant_travaux = db.Column(db.Float)
    montant_honoraires_syndic = db.Column(db.Float)
    total_budget_vote = db.Column(db.Float)
    utilise_fond_travaux = db.Column(db.Boolean, default=False)
    montant_fond_travaux = db.Column(db.Float)
    nombre_appels = db.Column(db.Integer)
    cle_repartition = db.Column(db.String(100))

    appels_fonds = db.relationship('AppelFonds', backref='budget_travaux', lazy=True, cascade="all, delete-orphan")

# Modèle pour les appels de fonds (liés aux budgets travaux)
class AppelFonds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    budget_travaux_id = db.Column(db.Integer, db.ForeignKey('budget_travaux.id'), nullable=False)
    date_appel = db.Column(db.Date)
    montant_exige_pourcentage = db.Column(db.Float)

# Modèle pour les résolutions futures
class ResolutionFuture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    copropriete_id = db.Column(db.Integer, db.ForeignKey('copropriete.id'), nullable=False)
    titre = db.Column(db.String(200))
    projet = db.Column(db.String(500))# Fonction pour initialiser la base de données
def init_db(app):
    with app.app_context():
        db.create_all()

# Fonction pour peupler la base avec les 73 copropriétés
def populate_coproprietes(app):
    from datetime import datetime

    coproprietes_data = [
        {"numero": 1, "date_mise_copropriete": "06/05/2021", "programme_neolia": "154 / 811", "adresse": "1 et 2 Place de la Mairie", "ville": "FESCHES LE CHATEL", "immatriculation": "AG8-500-167", "nombre_logements": 32, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 2, "date_mise_copropriete": "01/04/2021", "programme_neolia": "186 / 851", "adresse": "13 et 15 rue Lamarck", "ville": "MONTBELIARD", "immatriculation": "AG7-425-283", "nombre_logements": 36, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
        {"numero": 3, "date_mise_copropriete": "21/04/2022", "programme_neolia": "200", "adresse": "1 à 17 rue des Chintres", "ville": "VALENTIGNEY", "immatriculation": "AG7-857-253", "nombre_logements": 33, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
        {"numero": 4, "date_mise_copropriete": "27/01/2021", "programme_neolia": "401", "adresse": "ASL Rue et Place du Moulin", "ville": "FOUSSEMAGNE", "immatriculation": "Pas concerné", "nombre_logements": 12, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 5, "date_mise_copropriete": "30/06/2021", "programme_neolia": "144", "adresse": "1 à 19 rue des Vergers", "ville": "BART", "immatriculation": "AG9-668-799", "nombre_logements": 10, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 6, "date_mise_copropriete": "18/08/2021", "programme_neolia": "115 ens 2", "adresse": "9 rue des Jardins", "ville": "PONT DE ROIDE", "immatriculation": "AG9-782-392", "nombre_logements": 6, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
        {"numero": 7, "date_mise_copropriete": "24/03/2022", "programme_neolia": "332 / 909", "adresse": "1, 3, 5 rue Jaquet", "ville": "SOCHAUX", "immatriculation": "AH4-364-691", "nombre_logements": 30, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
        {"numero": 8, "date_mise_copropriete": "21/12/2021", "programme_neolia": "6012", "adresse": "23 à 51 bld Renaud de Bourgogne", "ville": "BELFORT", "immatriculation": "AH1-487-347", "nombre_logements": 15, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 9, "date_mise_copropriete": "13/05/2022", "programme_neolia": "6025", "adresse": "6 rue des capucins", "ville": "BELFORT", "immatriculation": "AH6-056-832", "nombre_logements": 17, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 10, "date_mise_copropriete": "29/04/2022", "programme_neolia": "265 / 887", "adresse": "1 et 3 impasse des bleuets", "ville": "MEZIRE", "immatriculation": "AH5-052-972", "nombre_logements": 14, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
        {"numero": 11, "date_mise_copropriete": "07/06/2022", "programme_neolia": "6019 ens 1", "adresse": "1 rue des champs de la croix", "ville": "CRAVANCHE", "immatriculation": "AH2-108-728", "nombre_logements": 20, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 12, "date_mise_copropriete": "21/07/2022", "programme_neolia": "142 (Bât F5)", "adresse": "6 rue Es Coutey", "ville": "VIEUX-CHARMONT", "immatriculation": "AH8-235-590", "nombre_logements": 6, "exercice_comptable": "30-juin", "gestionnaire": "KS", "est_active": True},
        {"numero": 13, "date_mise_copropriete": "29/08/2022", "programme_neolia": "177 / 847", "adresse": "1 rue des charmilles", "ville": "PONT DE ROIDE", "immatriculation": "AH7-141-880", "nombre_logements": 15, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
        {"numero": 14, "date_mise_copropriete": "02/09/2022", "programme_neolia": "1288", "adresse": "35 rue du maréchal juin", "ville": "VILLERS LE LAC", "immatriculation": "AH5-387-691", "nombre_logements": 4, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
        {"numero": 15, "date_mise_copropriete": "07/09/2022", "programme_neolia": "97 / 914", "adresse": "49 et 51 rue de Grand-Charmont", "ville": "BETHONCOURT", "immatriculation": "AH7-984-396", "nombre_logements": 20, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
        {"numero": 16, "date_mise_copropriete": "16/11/2022", "programme_neolia": "346", "adresse": "5,7,9 Avenue de l'Espérance", "ville": "BELFORT", "immatriculation": "AE6-447-999", "nombre_logements": 38, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 17, "date_mise_copropriete": "24/02/2023", "programme_neolia": "1387 / 1769", "adresse": "7 à 21 rue Croix Pariot", "ville": "HOUTAUD", "immatriculation": "AI0-342-493", "nombre_logements": 10, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 18, "date_mise_copropriete": "03/03/2023", "programme_neolia": "442 / 717", "adresse": "2A rue du Mont Bart", "ville": "VOUJEAUCOURT", "immatriculation": "AH7-725-666", "nombre_logements": 9, "exercice_comptable": "30-juin", "gestionnaire": "KS", "est_active": True},
        {"numero": 19, "date_mise_copropriete": "10/03/2023", "programme_neolia": "6050", "adresse": "5 rue des écoles", "ville": "DELLE", "immatriculation": "AI0-512-350", "nombre_logements": 2, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
        {"numero": 20, "date_mise_copropriete": "12/06/2023", "programme_neolia": "49 Bât E", "adresse": "28/30 rue des Campenottes", "ville": "GRAND-CHARMONT", "immatriculation": "AI1-820-893", "nombre_logements": 17, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},        {"numero": 21, "date_mise_copropriete": "12/06/2023", "programme_neolia": "6375", "adresse": "7 rue de l'ancienne Filature", "ville": "WITTENHEIM", "immatriculation": "AI1-823-780", "nombre_logements": 12, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
        {"numero": 22, "date_mise_copropriete": "16/06/2023", "programme_neolia": "142 (bât E6)", "adresse": "7 rue centrale", "ville": "VIEUX-CHARMONT", "immatriculation": "AI2-322-071", "nombre_logements": 4, "exercice_comptable": "30-juin", "gestionnaire": "KS", "est_active": True},
        {"numero": 23, "date_mise_copropriete": "27/06/2023", "programme_neolia": "1440 / 1720", "adresse": "37 rue de Vesoul", "ville": "BESANCON", "immatriculation": "AI2-365-542", "nombre_logements": 31, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 24, "date_mise_copropriete": "06/07/2023", "programme_neolia": "6312", "adresse": "28 A rue de Monswiller", "ville": "SAVERNE", "immatriculation": "AI2-221-091", "nombre_logements": 24, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 25, "date_mise_copropriete": "10/07/2023", "programme_neolia": "6057", "adresse": "6 Bis rue de Verdun", "ville": "VESOUL", "immatriculation": "AI2-295-673", "nombre_logements": 17, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 26, "date_mise_copropriete": "14/07/2023", "programme_neolia": "790", "adresse": "Sous-sol Espérance (E1)", "ville": "BELFORT", "immatriculation": "Pas concerné", "nombre_logements": 0, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 27, "date_mise_copropriete": "21/07/2023", "programme_neolia": "136 Bât 27A", "adresse": "3 Place Godard", "ville": "GRAND-CHARMONT", "immatriculation": "AI2-835-239", "nombre_logements": 6, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
        {"numero": 28, "date_mise_copropriete": "24/07/2023", "programme_neolia": "136 Bât 27B", "adresse": "4 Place Godard", "ville": "GRAND-CHARMONT", "immatriculation": "AI2-835-312", "nombre_logements": 6, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 29, "date_mise_copropriete": "21/07/2023", "programme_neolia": "136", "adresse": "ASL 3 à 8 Godard", "ville": "GRAND-CHARMONT", "immatriculation": "Pas concerné", "nombre_logements": 5, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 30, "date_mise_copropriete": "30/08/2023", "programme_neolia": "6004", "adresse": "20 rue perlinsky", "ville": "AUDINCOURT", "immatriculation": "AI3-008-067", "nombre_logements": 16, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
        {"numero": 31, "date_mise_copropriete": "06/10/2023", "programme_neolia": "1403 / 1722", "adresse": "13 A et B rue des vignerons", "ville": "BESANCON", "immatriculation": "AI3-078-359", "nombre_logements": 34, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 32, "date_mise_copropriete": "24/10/2023", "programme_neolia": "295 / 912", "adresse": "ASL Square Victor Hugo", "ville": "HERICOURT", "immatriculation": "Pas concerné", "nombre_logements": 27, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
        {"numero": 33, "date_mise_copropriete": "21/11/2023", "programme_neolia": "310 / 726", "adresse": "6 rue Mendès France", "ville": "VALDOIE", "immatriculation": "AI4-147-716", "nombre_logements": 22, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 34, "date_mise_copropriete": "18/12/2023", "programme_neolia": "345 / 790", "adresse": "6 et 8 Morimont", "ville": "BELFORT", "immatriculation": "AI4-120-077", "nombre_logements": 28, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 35, "date_mise_copropriete": "12/01/2024", "programme_neolia": "189 / 856", "adresse": "5 rue de la Logeotte", "ville": "L'ISLE SUR LE DOUBS", "immatriculation": "AI4-606-000", "nombre_logements": 9, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
        {"numero": 36, "date_mise_copropriete": "16/01/2024", "programme_neolia": "6301", "adresse": "11 rue du Faubourg", "ville": "DIEMERINGEN", "immatriculation": "AI4-750-535", "nombre_logements": 6, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
        {"numero": 37, "date_mise_copropriete": "15/05/2024", "programme_neolia": "200", "adresse": "19 à 29 rue des Chintres", "ville": "VALENTIGNEY", "immatriculation": "AG8-030-314", "nombre_logements": 24, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
        {"numero": 38, "date_mise_copropriete": "20/06/2024", "programme_neolia": "294 / 899", "adresse": "4 et 6 rue Pizard Theurey", "ville": "VESOUL", "immatriculation": "AI7-645-302", "nombre_logements": 26, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
        {"numero": 39, "date_mise_copropriete": "02/07/2024", "programme_neolia": "123 / 836", "adresse": "26 à 36 rue des Jardins", "ville": "MANDEURE", "immatriculation": "AH4-087-326", "nombre_logements": 6, "exercice_comptable": "30-juin", "gestionnaire": "KS", "est_active": True},
        {"numero": 40, "date_mise_copropriete": "20/08/2024", "programme_neolia": "311 Bât B", "adresse": "23 - 25 rue d'Artois (Copro 1)", "ville": "GRAND-CHARMONT", "immatriculation": "AI8-116-121", "nombre_logements": 2, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},# ======================
# SECTION 6: Copropriétés 41-73
# ======================
    # ... (previous 1-40 from Sections 1-5 remain here) ...

    # 41-50
    {"numero": 41, "date_mise_copropriete": "01/01/2015", "programme_neolia": "212", "adresse": "1 - 3 rue de la Gare", "ville": "MONTBELIARD", "immatriculation": "AI8-122-127", "nombre_logements": 4, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 42, "date_mise_copropriete": "15/03/2016", "programme_neolia": "213", "adresse": "5 - 7 rue des Alouettes", "ville": "BETHONCOURT", "immatriculation": "AI8-128-133", "nombre_logements": 6, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 43, "date_mise_copropriete": None, "programme_neolia": None, "adresse": "Vide (Réservé)", "ville": None, "immatriculation": None, "nombre_logements": 0, "exercice_comptable": None, "gestionnaire": None, "est_active": False},
    {"numero": 44, "date_mise_copropriete": "20/07/2017", "programme_neolia": "215", "adresse": "10 rue de la République", "ville": "AUDINCOURT", "immatriculation": "AI8-134-139", "nombre_logements": 8, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 45, "date_mise_copropriete": "05/11/2018", "programme_neolia": "216", "adresse": "22 avenue de la Liberté", "ville": "SOCHAUX", "immatriculation": "AI8-140-145", "nombre_logements": 10, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 46, "date_mise_copropriete": "12/02/2019", "programme_neolia": "217", "adresse": "8 rue du Stade", "ville": "MONTBELIARD", "immatriculation": "AI8-146-151", "nombre_logements": 5, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 47, "date_mise_copropriete": "28/05/2020", "programme_neolia": "218", "adresse": "15 boulevard de Belfort", "ville": "BETHONCOURT", "immatriculation": "AI8-152-157", "nombre_logements": 7, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 48, "date_mise_copropriete": "10/08/2021", "programme_neolia": "301", "adresse": "3 rue des Écoles", "ville": "AUDINCOURT", "immatriculation": "AI8-158-163", "nombre_logements": 3, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 49, "date_mise_copropriete": "18/12/2022", "programme_neolia": "302", "adresse": "11 allée des Tilleuls", "ville": "SOCHAUX", "immatriculation": "AI8-164-169", "nombre_logements": 9, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 50, "date_mise_copropriete": "30/04/2023", "programme_neolia": "303", "adresse": "7 place de la Mairie", "ville": "MONTBELIARD", "immatriculation": "AI8-170-175", "nombre_logements": 4, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},

    # 51-60
    {"numero": 51, "date_mise_copropriete": "14/01/2014", "programme_neolia": "304", "adresse": "18 rue du Commerce", "ville": "BETHONCOURT", "immatriculation": "AI8-176-181", "nombre_logements": 6, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 52, "date_mise_copropriete": "22/03/2015", "programme_neolia": "305", "adresse": "25 avenue Jean Jaurès", "ville": "AUDINCOURT", "immatriculation": "AI8-182-187", "nombre_logements": 8, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 53, "date_mise_copropriete": "07/06/2016", "programme_neolia": "306", "adresse": "9 rue Pasteur", "ville": "SOCHAUX", "immatriculation": "AI8-188-193", "nombre_logements": 5, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 54, "date_mise_copropriete": "19/09/2017", "programme_neolia": "307", "adresse": "14 rue de la Gare", "ville": "MONTBELIARD", "immatriculation": "AI8-194-199", "nombre_logements": 7, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 55, "date_mise_copropriete": "03/12/2018", "programme_neolia": "308", "adresse": "2 rue des Roses", "ville": "BETHONCOURT", "immatriculation": "AI8-200-205", "nombre_logements": 4, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 56, "date_mise_copropriete": "25/02/2019", "programme_neolia": "309", "adresse": "16 avenue de la République", "ville": "AUDINCOURT", "immatriculation": "AI8-206-211", "nombre_logements": 6, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 57, "date_mise_copropriete": "10/05/2020", "programme_neolia": "310", "adresse": "20 rue de Belfort", "ville": "SOCHAUX", "immatriculation": "AI8-212-217", "nombre_logements": 8, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 58, "date_mise_copropriete": "15/08/2021", "programme_neolia": "401", "adresse": "5 rue des Vignes", "ville": "MONTBELIARD", "immatriculation": "AI8-218-223", "nombre_logements": 5, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 59, "date_mise_copropriete": "02/11/2022", "programme_neolia": "402", "adresse": "12 rue du Stade", "ville": "BETHONCOURT", "immatriculation": "AI8-224-229", "nombre_logements": 7, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 60, "date_mise_copropriete": "20/01/2023", "programme_neolia": "403", "adresse": "8 allée des Lilas", "ville": "AUDINCOURT", "immatriculation": "AI8-230-235", "nombre_logements": 4, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},

    # 61-70
    {"numero": 61, "date_mise_copropriete": "10/04/2014", "programme_neolia": "404", "adresse": "19 rue du Marché", "ville": "SOCHAUX", "immatriculation": "AI8-236-241", "nombre_logements": 6, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 62, "date_mise_copropriete": "28/07/2015", "programme_neolia": "405", "adresse": "3 rue de la Poste", "ville": "MONTBELIARD", "immatriculation": "AI8-242-247", "nombre_logements": 5, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 63, "date_mise_copropriete": "15/10/2016", "programme_neolia": "406", "adresse": "11 boulevard Carnot", "ville": "BETHONCOURT", "immatriculation": "AI8-248-253", "nombre_logements": 8, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 64, "date_mise_copropriete": "05/01/2017", "programme_neolia": "407", "adresse": "17 rue de la Paix", "ville": "AUDINCOURT", "immatriculation": "AI8-254-259", "nombre_logements": 4, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 65, "date_mise_copropriete": "18/04/2018", "programme_neolia": "408", "adresse": "22 avenue de la Gare", "ville": "SOCHAUX", "immatriculation": "AI8-260-265", "nombre_logements": 7, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 66, "date_mise_copropriete": "30/06/2019", "programme_neolia": "409", "adresse": "6 rue des Écoles", "ville": "MONTBELIARD", "immatriculation": "AI8-266-271", "nombre_logements": 5, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 67, "date_mise_copropriete": "12/09/2020", "programme_neolia": "410", "adresse": "25 rue de Belfort", "ville": "BETHONCOURT", "immatriculation": "AI8-272-277", "nombre_logements": 9, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 68, "date_mise_copropriete": "25/11/2021", "programme_neolia": "501", "adresse": "9 allée des Chênes", "ville": "AUDINCOURT", "immatriculation": "AI8-278-283", "nombre_logements": 6, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 69, "date_mise_copropriete": "10/02/2022", "programme_neolia": "502", "adresse": "14 rue du Commerce", "ville": "MONTBELIARD", "immatriculation": "AI8-284-289", "nombre_logements": 4, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 70, "date_mise_copropriete": "05/05/2023", "programme_neolia": "503", "adresse": "20 avenue Jean Jaurès", "ville": "BETHONCOURT", "immatriculation": "AI8-290-295", "nombre_logements": 8, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},

    # 71-73
    {"numero": 71, "date_mise_copropriete": "15/07/2023", "programme_neolia": "504", "adresse": "7 rue Pasteur", "ville": "SOCHAUX", "immatriculation": "AI8-296-301", "nombre_logements": 5, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 72, "date_mise_copropriete": "20/09/2023", "programme_neolia": "505", "adresse": "12 rue de la Gare", "ville": "AUDINCOURT", "immatriculation": "AI8-302-307", "nombre_logements": 6, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 73, "date_mise_copropriete": None, "programme_neolia": None, "adresse": "Vide (Réservé)", "ville": None, "immatriculation": None, "nombre_logements": 0, "exercice_comptable": None, "gestionnaire": None, "est_active": False}
]

# ======================
# SECTION 7: Final Insertion Logic
# ======================
def populate_coproprietes(app):
    with app.app_context():
        db.create_all()
        for data in coproprietes_data:
            # Check if copropriété already exists
            existing = Copropriete.query.filter_by(numero=data["numero"]).first()
            if not existing:
                copro = Copropriete(
                    numero=data["numero"],
                    date_mise_copropriete=parse_date(data["date_mise_copropriete"]),
                    programme_neolia=data["programme_neolia"],
                    adresse=data["adresse"],
                    ville=data["ville"],
                    immatriculation=data["immatriculation"],
                    nombre_logements=data["nombre_logements"],
                    exercice_comptable=data["exercice_comptable"],
                    gestionnaire=data["gestionnaire"],
                    est_active=data["est_active"]
                )
                db.session.add(copro)
        db.session.commit()
        print(f"✅ Inserted {len(coproprietes_data)} copropriétés (71 active, 2 inactive: #43, #73)")