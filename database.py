from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

# ========== INITIALISATION DE LA BASE DE DONNÉES ==========
db = SQLAlchemy()

def parse_date(value):
    """Convertit une date au format DD/MM/YYYY en objet date."""
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(value, "%d/%m/%Y").date()
    except (ValueError, TypeError):
        return None

# ========== MODÈLES ==========

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
    est_active = db.Column(db.Boolean, default=True)

    # Relations
    fiche_immeuble = db.relationship('FicheImmeuble', backref='copropriete', uselist=False)
    contrats = db.relationship('Contrat', backref='copropriete', lazy=True)
    coproprietaires = db.relationship('Coproprietaire', backref='copropriete', lazy=True)
    assemblees_generales = db.relationship('AssembleeGenerale', backref='copropriete', lazy=True)
    resolutions_futures = db.relationship('ResolutionFuture', backref='copropriete', lazy=True)

# Modèle pour la fiche immeuble
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

# Modèle pour les contrats
class Contrat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    copropriete_id = db.Column(db.Integer, db.ForeignKey('copropriete.id'), nullable=False)
    type_contrat = db.Column(db.String(100))
    nature = db.Column(db.String(200))
    fournisseur = db.Column(db.String(200))
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)
    montant_annuel = db.Column(db.Float)
    prestations = db.relationship('Prestation', backref='contrat', lazy=True, cascade="all, delete-orphan")

# Modèle pour les prestations
class Prestation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contrat_id = db.Column(db.Integer, db.ForeignKey('contrat.id'), nullable=False)
    libelle = db.Column(db.String(200))
    frequence = db.Column(db.String(50))
    prix_unitaire = db.Column(db.Float)
    quantite = db.Column(db.Integer)
    total = db.Column(db.Float)

# Modèle pour les copropriétaires
class Coproprietaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    copropriete_id = db.Column(db.Integer, db.ForeignKey('copropriete.id'), nullable=False)
    civilite_id = db.Column(db.Integer, db.ForeignKey('civilites.id'), nullable=True)
    civilite = db.relationship('Civilite', backref='coproprietaires', foreign_keys=[civilite_id])
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
    lien_espace_client = db.Column(db.String(500))

    locataire_civilite_id = db.Column(db.Integer, db.ForeignKey('civilites.id'), nullable=True)
    locataire_nom = db.Column(db.String(100))
    locataire_prenom = db.Column(db.String(100))
    locataire_email = db.Column(db.String(200))
    locataire_telephone = db.Column(db.String(50))

    lots = db.relationship('LotCoproprietaire', backref='coproprietaire', lazy=True, cascade="all, delete-orphan")
    emails = db.relationship('EmailCoproprietaire', backref='coproprietaire', lazy=True, cascade="all, delete-orphan")
    telephones = db.relationship('TelephoneCoproprietaire', backref='coproprietaire', lazy=True, cascade="all, delete-orphan")

# Modèle pour les civilités
class Civilite(db.Model):
    __tablename__ = 'civilites'
    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(20), unique=True, nullable=False)

# Modèles pour les lots/emails/téléphones des copropriétaires
class LotCoproprietaire(db.Model):
    __tablename__ = 'lots_coproprietaires'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), nullable=False)
    nature = db.Column(db.String(100))
    coproprietaire_id = db.Column(db.Integer, db.ForeignKey('coproprietaire.id'), nullable=False)

class EmailCoproprietaire(db.Model):
    __tablename__ = 'emails_coproprietaires'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(200), nullable=False)
    principal = db.Column(db.Boolean, default=False)
    coproprietaire_id = db.Column(db.Integer, db.ForeignKey('coproprietaire.id'), nullable=False)

class TelephoneCoproprietaire(db.Model):
    __tablename__ = 'telephones_coproprietaires'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(50), nullable=False)
    principal = db.Column(db.Boolean, default=False)
    coproprietaire_id = db.Column(db.Integer, db.ForeignKey('coproprietaire.id'), nullable=False)

# Modèle pour les Assemblées Générales
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

# Modèle pour les points à retenir
class PointARetenir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ag_id = db.Column(db.Integer, db.ForeignKey('assemblee_generale.id'), nullable=False)
    description = db.Column(db.String(500))

# Modèle pour les budgets travaux
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

# Modèle pour les appels de fonds
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
    projet = db.Column(db.String(500))

# ========== DONNÉES DES 73 COPROPRIÉTÉS ==========
COPROPRIETES_DATA = [
    # 1-10
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

    # 11-20
    {"numero": 11, "date_mise_copropriete": "07/06/2022", "programme_neolia": "6019 ens 1", "adresse": "1 rue des champs de la croix", "ville": "CRAVANCHE", "immatriculation": "AH2-108-728", "nombre_logements": 20, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 12, "date_mise_copropriete": "21/07/2022", "programme_neolia": "142 (Bât F5)", "adresse": "6 rue Es Coutey", "ville": "VIEUX-CHARMONT", "immatriculation": "AH8-235-590", "nombre_logements": 6, "exercice_comptable": "30-juin", "gestionnaire": "KS", "est_active": True},
    {"numero": 13, "date_mise_copropriete": "29/08/2022", "programme_neolia": "177 / 847", "adresse": "1 rue des charmilles", "ville": "PONT DE ROIDE", "immatriculation": "AH7-141-880", "nombre_logements": 15, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 14, "date_mise_copropriete": "02/09/2022", "programme_neolia": "1288", "adresse": "35 rue du maréchal juin", "ville": "VILLERS LE LAC", "immatriculation": "AH5-387-691", "nombre_logements": 4, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 15, "date_mise_copropriete": "07/09/2022", "programme_neolia": "97 / 914", "adresse": "49 et 51 rue de Grand-Charmont", "ville": "BETHONCOURT", "immatriculation": "AH7-984-396", "nombre_logements": 20, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 16, "date_mise_copropriete": "16/11/2022", "programme_neolia": "346", "adresse": "5,7,9 Avenue de l'Espérance", "ville": "BELFORT", "immatriculation": "AE6-447-999", "nombre_logements": 38, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 17, "date_mise_copropriete": "24/02/2023", "programme_neolia": "1387 / 1769", "adresse": "7 à 21 rue Croix Pariot", "ville": "HOUTAUD", "immatriculation": "AI0-342-493", "nombre_logements": 10, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 18, "date_mise_copropriete": "03/03/2023", "programme_neolia": "442 / 717", "adresse": "2A rue du Mont Bart", "ville": "VOUJEAUCOURT", "immatriculation": "AH7-725-666", "nombre_logements": 9, "exercice_comptable": "30-juin", "gestionnaire": "KS", "est_active": True},
    {"numero": 19, "date_mise_copropriete": "10/03/2023", "programme_neolia": "6050", "adresse": "5 rue des écoles", "ville": "DELLE", "immatriculation": "AI0-512-350", "nombre_logements": 2, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 20, "date_mise_copropriete": "12/06/2023", "programme_neolia": "49 Bât E", "adresse": "28/30 rue des Campenottes", "ville": "GRAND-CHARMONT", "immatriculation": "AI1-820-893", "nombre_logements": 17, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},

    # 21-30
    {"numero": 21, "date_mise_copropriete": "12/06/2023", "programme_neolia": "6375", "adresse": "7 rue de l'ancienne Filature", "ville": "WITTENHEIM", "immatriculation": "AI1-823-780", "nombre_logements": 12, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 22, "date_mise_copropriete": "16/06/2023", "programme_neolia": "142 (bât E6)", "adresse": "7 rue centrale", "ville": "VIEUX-CHARMONT", "immatriculation": "AI2-322-071", "nombre_logements": 4, "exercice_comptable": "30-juin", "gestionnaire": "KS", "est_active": True},
    {"numero": 23, "date_mise_copropriete": "27/06/2023", "programme_neolia": "1440 / 1720", "adresse": "37 rue de Vesoul", "ville": "BESANCON", "immatriculation": "AI2-365-542", "nombre_logements": 31, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 24, "date_mise_copropriete": "06/07/2023", "programme_neolia": "6312", "adresse": "28 A rue de Monswiller", "ville": "SAVERNE", "immatriculation": "AI2-221-091", "nombre_logements": 24, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 25, "date_mise_copropriete": "10/07/2023", "programme_neolia": "6057", "adresse": "6 Bis rue de Verdun", "ville": "VESOUL", "immatriculation": "AI2-295-673", "nombre_logements": 17, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 26, "date_mise_copropriete": "14/07/2023", "programme_neolia": "790", "adresse": "Sous-sol Espérance (E1)", "ville": "BELFORT", "immatriculation": "Pas concerné", "nombre_logements": 0, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 27, "date_mise_copropriete": "21/07/2023", "programme_neolia": "136 Bât 27A", "adresse": "3 Place Godard", "ville": "GRAND-CHARMONT", "immatriculation": "AI2-835-239", "nombre_logements": 6, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 28, "date_mise_copropriete": "24/07/2023", "programme_neolia": "136 Bât 27B", "adresse": "4 Place Godard", "ville": "GRAND-CHARMONT", "immatriculation": "AI2-835-312", "nombre_logements": 6, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 29, "date_mise_copropriete": "21/07/2023", "programme_neolia": "136", "adresse": "ASL 3 à 8 Godard", "ville": "GRAND-CHARMONT", "immatriculation": "Pas concerné", "nombre_logements": 5, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 30, "date_mise_copropriete": "30/08/2023", "programme_neolia": "6004", "adresse": "20 rue perlinsky", "ville": "AUDINCOURT", "immatriculation": "AI3-008-067", "nombre_logements": 16, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},

    # 31-40
    {"numero": 31, "date_mise_copropriete": "06/10/2023", "programme_neolia": "1403 / 1722", "adresse": "13 A et B rue des vignerons", "ville": "BESANCON", "immatriculation": "AI3-078-359", "nombre_logements": 34, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 32, "date_mise_copropriete": "24/10/2023", "programme_neolia": "295 / 912", "adresse": "ASL Square Victor Hugo", "ville": "HERICOURT", "immatriculation": "Pas concerné", "nombre_logements": 27, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 33, "date_mise_copropriete": "21/11/2023", "programme_neolia": "310 / 726", "adresse": "6 rue Mendès France", "ville": "VALDOIE", "immatriculation": "AI4-147-716", "nombre_logements": 22, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 34, "date_mise_copropriete": "18/12/2023", "programme_neolia": "345 / 790", "adresse": "6 et 8 Morimont", "ville": "BELFORT", "immatriculation": "AI4-120-077", "nombre_logements": 28, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 35, "date_mise_copropriete": "12/01/2024", "programme_neolia": "189 / 856", "adresse": "5 rue de la Logeotte", "ville": "L'ISLE SUR LE DOUBS", "immatriculation": "AI4-606-000", "nombre_logements": 9, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 36, "date_mise_copropriete": "16/01/2024", "programme_neolia": "6301", "adresse": "11 rue du Faubourg", "ville": "DIEMERINGEN", "immatriculation": "AI4-750-535", "nombre_logements": 6, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 37, "date_mise_copropriete": "15/05/2024", "programme_neolia": "200", "adresse": "19 à 29 rue des Chintres", "ville": "VALENTIGNEY", "immatriculation": "AG8-030-314", "nombre_logements": 24, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 38, "date_mise_copropriete": "20/06/2024", "programme_neolia": "294 / 899", "adresse": "4 et 6 rue Pizard Theurey", "ville": "VESOUL", "immatriculation": "AI7-645-302", "nombre_logements": 26, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 39, "date_mise_copropriete": "02/07/2024", "programme_neolia": "123 / 836", "adresse": "26 à 36 rue des Jardins", "ville": "MANDEURE", "immatriculation": "AH4-087-326", "nombre_logements": 6, "exercice_comptable": "30-juin", "gestionnaire": "KS", "est_active": True},
    {"numero": 40, "date_mise_copropriete": "20/08/2024", "programme_neolia": "311 Bât B", "adresse": "23 - 25 rue d'Artois (Copro 1)", "ville": "GRAND-CHARMONT", "immatriculation": "AI8-116-121", "nombre_logements": 2, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},

    # 41-50
    {"numero": 41, "date_mise_copropriete": "22/08/2024", "programme_neolia": "152", "adresse": "1 cour de l'orangerie", "ville": "AUDINCOURT", "immatriculation": "AI-039-653", "nombre_logements": 20, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 42, "date_mise_copropriete": "23/08/2024", "programme_neolia": "116 / 833", "adresse": "15 à 29 Rue Louis Garnier", "ville": "AUDINCOURT", "immatriculation": "AI7-519-580", "nombre_logements": 8, "exercice_comptable": "30-juin", "gestionnaire": "KS", "est_active": True},
    {"numero": 43, "date_mise_copropriete": None, "programme_neolia": None, "adresse": "Vide (Réservé)", "ville": None, "immatriculation": None, "nombre_logements": 0, "exercice_comptable": None, "gestionnaire": None, "est_active": False},
    {"numero": 44, "date_mise_copropriete": "27/09/2024", "programme_neolia": "1120 ens 12 A", "adresse": "2 et 4 rue du Luxembourg", "ville": "BESANCON", "immatriculation": "Pas concerné", "nombre_logements": 6, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 45, "date_mise_copropriete": "30/09/2024", "programme_neolia": "1033 / 1605", "adresse": "ASL Villeminot - Terre Rouge", "ville": "BESANCON", "immatriculation": "Pas concerné", "nombre_logements": 13, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 46, "date_mise_copropriete": "14/10/2024", "programme_neolia": "311-315 / 906 - 917", "adresse": "1 et 3 rue d'Artois (Copro 2)", "ville": "GRAND-CHARMONT", "immatriculation": "AI8-815-086", "nombre_logements": 2, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 47, "date_mise_copropriete": "31/10/2024", "programme_neolia": "159 - 196 / 835 - 854", "adresse": "ASL 3 à 19 Perlinsky", "ville": "AUDINCOURT", "immatriculation": "Pas concerné", "nombre_logements": 11, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 48, "date_mise_copropriete": "13/11/2024", "programme_neolia": "6017", "adresse": "8 et 10 rue Engel", "ville": "BELFORT", "immatriculation": "AJ0-376-970", "nombre_logements": 12, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 49, "date_mise_copropriete": "18/12/2024", "programme_neolia": "311-315 / 906 - 917", "adresse": "19 et 21 rue d'Artois (Copro 2)", "ville": "GRAND-CHARMONT", "immatriculation": "AJ0-074-351", "nombre_logements": 2, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 50, "date_mise_copropriete": "19/02/2025", "programme_neolia": "433 / 728", "adresse": "4 rue du Vieil Armand", "ville": "BELFORT", "immatriculation": "AI9-690-066", "nombre_logements": 10, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},

    # 51-60
    {"numero": 51, "date_mise_copropriete": "12/03/2025", "programme_neolia": "6105", "adresse": "59 rue du Mont Roland", "ville": "DOLE", "immatriculation": "AJ1-701-184", "nombre_logements": 15, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 52, "date_mise_copropriete": "17/04/2025", "programme_neolia": "1001", "adresse": "1 à 7 allées des Campenottes", "ville": "BESANCON", "immatriculation": "AJ2-027-621", "nombre_logements": 24, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 53, "date_mise_copropriete": "16/05/2025", "programme_neolia": "295 / 912", "adresse": "11 Rue Paul Verlaine", "ville": "HERICOURT", "immatriculation": "AJ2-174-308", "nombre_logements": 6, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 54, "date_mise_copropriete": "31/05/2025", "programme_neolia": "87", "adresse": "5 à 7 rue des acacias", "ville": "VALENTIGNEY", "immatriculation": "AJ2-305-571", "nombre_logements": 12, "exercice_comptable": "30-juin", "gestionnaire": "KS", "est_active": True},
    {"numero": 55, "date_mise_copropriete": "04/07/2025", "programme_neolia": "37 / 806", "adresse": "28 à 30 rue Croizat", "ville": "BELFORT", "immatriculation": "AJ2-997-500", "nombre_logements": 12, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 56, "date_mise_copropriete": "17/07/2025", "programme_neolia": "150 / 810 / 863", "adresse": "4 et 6 rue Jules Emile Zingg", "ville": "EXINCOURT", "immatriculation": "AJ3-165-966", "nombre_logements": 32, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 57, "date_mise_copropriete": "21/07/2025", "programme_neolia": "349 / 752", "adresse": "6 et 10 Rue de la Souaberie", "ville": "MONTBELIARD", "immatriculation": "AJ3-108-396", "nombre_logements": 14, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 58, "date_mise_copropriete": "22/07/2025", "programme_neolia": "6328", "adresse": "3,5 Dr Schweitzer / 7 à 11 Lasch", "ville": "BIESHEIM", "immatriculation": "AJ2-829-059", "nombre_logements": 30, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 59, "date_mise_copropriete": "30/07/2025", "programme_neolia": "1007 / 1952", "adresse": "4 et 4B Rue midol", "ville": "BESANCON", "immatriculation": "AJ2-963-197", "nombre_logements": 12, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 60, "date_mise_copropriete": "31/07/2025", "programme_neolia": "32 / 379", "adresse": "117 Rue de Seloncourt", "ville": "AUDINCOURT", "immatriculation": "AJ3-900-883", "nombre_logements": 6, "exercice_comptable": "30-juin", "gestionnaire": "KS", "est_active": True},

    # 61-70
    {"numero": 61, "date_mise_copropriete": "30/09/2025", "programme_neolia": "1526 / 1671", "adresse": "1 à 3 rue Gascon", "ville": "BESANCON", "immatriculation": "AJ4-109-021", "nombre_logements": 36, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 62, "date_mise_copropriete": "28/10/2025", "programme_neolia": "276 / 897", "adresse": "5 à 9 quai du Dr Petitjean", "ville": "VESOUL", "immatriculation": "AJ4-636-049", "nombre_logements": 49, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 63, "date_mise_copropriete": "04/11/2025", "programme_neolia": "ONV", "adresse": "ASL 3A - 3B rue Anne Frank et 47A - 47B - 47C avenue de Paris", "ville": "COLMAR", "immatriculation": "Pas concerné", "nombre_logements": 17, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 64, "date_mise_copropriete": "24/11/2025", "programme_neolia": "557/558 et 634 (garages)", "adresse": "10 et 12 Rue de la Prospérité", "ville": "BELFORT", "immatriculation": "AJ4-953-253", "nombre_logements": 21, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 65, "date_mise_copropriete": "09/12/2025", "programme_neolia": "297 / 901", "adresse": "5 avenue Wilson", "ville": "BELFORT", "immatriculation": "AJ4-406-369", "nombre_logements": 10, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 66, "date_mise_copropriete": "12/12/2025", "programme_neolia": "1569 / 1612", "adresse": "39 rue des Flutes Agasses", "ville": "BESANCON", "immatriculation": "AJ5-046-214", "nombre_logements": 10, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 67, "date_mise_copropriete": "16/12/2025", "programme_neolia": "408 / 759 ONV", "adresse": "Batterie du parc", "ville": "MONTBELIARD", "immatriculation": "AJ4-569-885", "nombre_logements": 24, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 68, "date_mise_copropriete": "19/12/2025", "programme_neolia": "6320", "adresse": "10 rue de la Ganzau", "ville": "STRASBOURG", "immatriculation": "AJ4-987-418", "nombre_logements": 12, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 69, "date_mise_copropriete": "30/12/2025", "programme_neolia": "6047", "adresse": "13-15 rue des Rossignols 2 à 6 rue Dunant", "ville": "DELLE", "immatriculation": None, "nombre_logements": 28, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 70, "date_mise_copropriete": "21/01/2026", "programme_neolia": "1380", "adresse": "30 D Rue de l'Eglise", "ville": "BESANCON", "immatriculation": "AJ5-862-974", "nombre_logements": 20, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},

    # 71-73
    {"numero": 71, "date_mise_copropriete": "01/01/2026", "programme_neolia": "345 / 346 / 790", "adresse": "AFUL Espérance et Morimont", "ville": "BELFORT", "immatriculation": "Pas concerné", "nombre_logements": 3, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 72, "date_mise_copropriete": "30/04/2026", "programme_neolia": "296 / 911", "adresse": "40 Avenue du Lac", "ville": "VESOUL", "immatriculation": None, "nombre_logements": 14, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True},
    {"numero": 73, "date_mise_copropriete": "01/07/2026", "programme_neolia": None, "adresse": None, "ville": "VALDOIE", "immatriculation": None, "nombre_logements": 23, "exercice_comptable": None, "gestionnaire": None, "est_active": False}
]

# Fonction pour initialiser la base de données
def init_db(app):
    """Initialise les tables de la base de données."""
    with app.app_context():
        db.create_all()