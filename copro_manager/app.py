from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from sqlalchemy.orm import joinedload

# ========== CONFIGURATION ==========
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///copro_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ========== MODELS ==========
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
    exercice_comptable = db.Column(db.String(20))
    gestionnaire = db.Column(db.String(50))
    est_active = db.Column(db.Boolean, default=True)

    # Relationships
    fiche_immeuble = db.relationship('FicheImmeuble', backref='copropriete', uselist=False)
    contrats = db.relationship('Contrat', backref='copropriete', lazy=True)
    coproprietaires = db.relationship('Coproprietaire', backref='copropriete', lazy=True)
    assemblees_generales = db.relationship('AssembleeGenerale', backref='copropriete', lazy=True)
    resolutions_futures = db.relationship('ResolutionFuture', backref='copropriete', lazy=True)

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

class Prestation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contrat_id = db.Column(db.Integer, db.ForeignKey('contrat.id'), nullable=False)
    libelle = db.Column(db.String(200))
    frequence = db.Column(db.String(50))
    prix_unitaire = db.Column(db.Float)
    quantite = db.Column(db.Integer)
    total = db.Column(db.Float)

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
    lien_espace_client = db.Column(db.String(500))

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

class PointARetenir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ag_id = db.Column(db.Integer, db.ForeignKey('assemblee_generale.id'), nullable=False)
    description = db.Column(db.String(500))

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

class AppelFonds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    budget_travaux_id = db.Column(db.Integer, db.ForeignKey('budget_travaux.id'), nullable=False)
    date_appel = db.Column(db.Date)
    montant_exige_pourcentage = db.Column(db.Float)

class ResolutionFuture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    copropriete_id = db.Column(db.Integer, db.ForeignKey('copropriete.id'), nullable=False)
    titre = db.Column(db.String(200))
    projet = db.Column(db.String(500))

# ========== UTILITY FUNCTIONS ==========
def parse_date(date_str):
    """Parse date in DD/MM/YYYY or YYYY-MM-DD format"""
    if not date_str:
        return None
    try:
        if '/' in date_str:
            return datetime.strptime(date_str, '%d/%m/%Y').date()
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None

# ========== INITIAL DATA (73 copropriétés) ==========
COPROPRIETES_DATA = [
    {"numero": 1, "date_mise_copropriete": "06/05/2021", "programme_neolia": "154 / 811", "adresse": "1 et 2 Place de la Mairie", "ville": "FESCHES LE CHATEL", "immatriculation": "AG8-500-167", "nombre_logements": 32, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 2, "date_mise_copropriete": "01/04/2021", "programme_neolia": "186 / 851", "adresse": "13 et 15 rue Lamarck", "ville": "MONTBELIARD", "immatriculation": "AG7-425-283", "nombre_logements": 36, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 3, "date_mise_copropriete": "21/04/2022", "programme_neolia": "200", "adresse": "1 à 17 rue des Chintres", "ville": "VALENTIGNEY", "immatriculation": "AG7-857-253", "nombre_logements": 33, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 4, "date_mise_copropriete": "27/01/2021", "programme_neolia": "401", "adresse": "ASL Rue et Place du Moulin", "ville": "FOUSSEMAGNE", "immatriculation": "Pas concerné", "nombre_logements": 12, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 5, "date_mise_copropriete": "30/06/2021", "programme_neolia": "144", "adresse": "1 à 19 rue des Vergers", "ville": "BART", "immatriculation": "AG9-668-799", "nombre_logements": 10, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 6, "date_mise_copropriete": "18/08/2021", "programme_neolia": "115 ens 2", "adresse": "9 rue des Jardins", "ville": "PONT DE ROIDE", "immatriculation": "AG9-782-392", "nombre_logements": 6, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 7, "date_mise_copropriete": "24/03/2022", "programme_neolia": "332 / 909", "adresse": "1, 3, 5 rue Jaquet", "ville": "SOCHAUX", "immatriculation": "AH4-364-691", "nombre_logements": 30, "exercice_comptable": "31-déc", "gestionnaire": "KS", "est_active": True},
    {"numero": 8, "date_mise_copropriete": "21/12/2021", "programme_neolia": "6012", "adresse": "23 à 51 bld Renaud de Bourgogne", "ville": "BELFORT", "immatriculation": "AH1-487-347", "nombre_logements": 15, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 9, "date_mise_copropriete": "13/05/2022", "programme_neolia": "6025", "adresse": "6 rue des capucins", "ville": "BELFORT", "immatriculation": "AH6-056-832", "nombre_logements": 17, "exercice_comptable": "31-déc", "gestionnaire": "AJ", "est_active": True},
    {"numero": 10, "date_mise_copropriete": "29/04/2022", "programme_neolia": "265 / 887", "adresse": "1 et 3 impasse des bleuets", "ville": "MEZIRE", "immatriculation": "AH5-052-972", "nombre_logements": 14, "exercice_comptable": "30-juin", "gestionnaire": "AJ", "est_active": True}
]

# ========== STATISTICS FUNCTION ==========
def get_statistiques():
    from sqlalchemy import func
    total_copros = Copropriete.query.count()
    total_active = Copropriete.query.filter_by(est_active=True).count()
    total_inactive = total_copros - total_active
    total_logements = db.session.query(func.coalesce(func.sum(Copropriete.nombre_logements), 0)).scalar() or 0

    stats_gestionnaires = db.session.query(
        Copropriete.gestionnaire,
        func.count(Copropriete.id).label('count'),
        func.sum(Copropriete.nombre_logements).label('logements')
    ).filter(
        Copropriete.gestionnaire.isnot(None),
        Copropriete.est_active == True
    ).group_by(Copropriete.gestionnaire).all()

    gestionnaires = {}
    for g in stats_gestionnaires:
        gestionnaires[g.gestionnaire] = {
            'count': g.count,
            'logements': g.logements,
            'percentage': round((g.count / total_active) * 100, 1) if total_active > 0 else 0
        }

    stats_periodes = db.session.query(
        Copropriete.exercice_comptable,
        func.count(Copropriete.id).label('count')
    ).filter(
        Copropriete.exercice_comptable.isnot(None),
        Copropriete.est_active == True
    ).group_by(Copropriete.exercice_comptable).all()

    periodes = {}
    for p in stats_periodes:
        periodes[p.exercice_comptable] = {
            'count': p.count,
            'percentage': round((p.count / total_active) * 100, 1) if total_active > 0 else 0
        }

    return {
        'total_logements': total_logements,
        'gestionnaires': gestionnaires,
        'periodes': periodes,
        'total_active': total_active,
        'total_inactive': total_inactive
    }

# ========== ROUTES ==========
@app.route('/')
def index():
    search_query = request.args.get('q', '')
    search_type = request.args.get('type', 'tout')

    query = Copropriete.query.order_by(Copropriete.numero)

    if search_query:
        if search_type == 'tout':
            query = query.filter(
                (Copropriete.numero.ilike(f'%{search_query}%')) |
                (Copropriete.nom.ilike(f'%{search_query}%')) |
                (Copropriete.adresse.ilike(f'%{search_query}%')) |
                (Copropriete.ville.ilike(f'%{search_query}%')) |
                (Copropriete.gestionnaire.ilike(f'%{search_query}%')) |
                (Copropriete.immatriculation.ilike(f'%{search_query}%'))
            )
        elif search_type == 'ville':
            query = query.filter(Copropriete.ville.ilike(f'%{search_query}%'))
        elif search_type == 'gestionnaire':
            query = query.filter(Copropriete.gestionnaire.ilike(f'%{search_query}%'))
        elif search_type == 'immatriculation':
            query = query.filter(Copropriete.immatriculation.ilike(f'%{search_query}%'))

    coproprietes = query.all()
    stats = get_statistiques()
    return render_template('index.html', coproprietes=coproprietes, search_query=search_query, search_type=search_type, stats=stats)

@app.route('/copropriete/<int:copro_id>')
def copropriete(copro_id):
    copropriete = Copropriete.query.options(
        joinedload(Copropriete.fiche_immeuble),
        joinedload(Copropriete.coproprietaires),
        joinedload(Copropriete.contrats).joinedload(Contrat.prestations),
        joinedload(Copropriete.assemblees_generales).joinedload(AssembleeGenerale.points_a_retenir),
        joinedload(Copropriete.assemblees_generales).joinedload(AssembleeGenerale.budgets_travaux).joinedload(BudgetTravaux.appels_fonds),
        joinedload(Copropriete.resolutions_futures)
    ).get_or_404(copro_id)
    return render_template('copropriete.html', copropriete=copropriete)

@app.route('/copropriete/new', methods=['GET', 'POST'])
def new_copropriete():
    if request.method == 'POST':
        numero = int(request.form.get('numero'))
        existing = Copropriete.query.filter_by(numero=numero).first()
        if existing:
            flash(f'Le numéro {numero} existe déjà !', 'error')
            return redirect(url_for('new_copropriete'))

        new_copro = Copropriete(
            numero=numero,
            nom=request.form.get('nom', f"Copropriété {numero}"),
            date_mise_copropriete=parse_date(request.form.get('date_mise_copropriete')),
            programme_neolia=request.form.get('programme_neolia'),
            adresse=request.form.get('adresse'),
            ville=request.form.get('ville'),
            immatriculation=request.form.get('immatriculation'),
            nombre_logements=int(request.form.get('nombre_logements') or 0),
            exercice_comptable=request.form.get('exercice_comptable'),
            gestionnaire=request.form.get('gestionnaire'),
            est_active=True
        )
        db.session.add(new_copro)
        db.session.commit()
        flash(f'Copropriété #{numero} ajoutée avec succès !', 'success')
        return redirect(url_for('index'))
    return render_template('new_copropriete.html')

@app.route('/copropriete/<int:copro_id>/toggle_active', methods=['POST'])
def toggle_active(copro_id):
    copro = Copropriete.query.get_or_404(copro_id)
    copro.est_active = not copro.est_active
    db.session.commit()
    action = "désactivée" if not copro.est_active else "réactivée"
    flash(f'Copropriété #{copro.numero} {action} avec succès !', 'success')
    return redirect(url_for('index'))

# ========== FICHE IMMEUBLE ROUTES ==========
@app.route('/fiche-immeuble/save', methods=['POST'])
def save_fiche_immeuble():
    copro_id = request.form.get('copro_id')
    copropriete = Copropriete.query.get(copro_id)
    if not copropriete:
        flash('Copropriété non trouvée', 'error')
        return redirect(url_for('index'))

    fiche = FicheImmeuble.query.filter_by(copropriete_id=copro_id).first()
    if not fiche:
        fiche = FicheImmeuble(copropriete_id=copro_id)

    fiche.date_construction = parse_date(request.form.get('date_construction'))
    fiche.date_arrete_compte = parse_date(request.form.get('date_arrete_compte'))
    fiche.reference_neolia = request.form.get('reference_neolia')
    fiche.nom_commercial_vente_hlm = request.form.get('nom_commercial_vente_hlm')
    fiche.nom_responsable_secteur = request.form.get('nom_responsable_secteur')
    fiche.nom_notaire = request.form.get('nom_notaire')
    fiche.designation_immeuble = request.form.get('designation_immeuble')
    fiche.iban = request.form.get('iban')
    fiche.ics = request.form.get('ics')
    fiche.lien_dossier = request.form.get('lien_dossier')
    fiche.lien_budget = request.form.get('lien_budget')

    db.session.add(fiche)
    db.session.commit()
    flash('Fiche immeuble sauvegardée avec succès !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

# ========== CONTRATS ROUTES ==========
@app.route('/contrat/save', methods=['POST'])
def save_contrat():
    contrat_id = request.form.get('contrat_id')
    copro_id = request.form.get('copro_id')

    if contrat_id:
        contrat = Contrat.query.get(contrat_id)
        if not contrat:
            flash('Contrat non trouvé', 'error')
            return redirect(url_for('copropriete', copro_id=copro_id))
    else:
        contrat = Contrat(copropriete_id=copro_id)

    contrat.type_contrat = request.form.get('type_contrat')
    contrat.nature = request.form.get('nature')
    contrat.fournisseur = request.form.get('fournisseur')
    contrat.date_debut = parse_date(request.form.get('date_debut'))
    contrat.date_fin = parse_date(request.form.get('date_fin'))
    contrat.montant_annuel = float(request.form.get('montant_annuel') or 0)

    db.session.add(contrat)
    db.session.commit()
    flash('Contrat sauvegardé avec succès !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

@app.route('/contrat/<int:contrat_id>/delete', methods=['POST'])
def delete_contrat(contrat_id):
    contrat = Contrat.query.get_or_404(contrat_id)
    copro_id = contrat.copropriete_id
    db.session.delete(contrat)
    db.session.commit()
    flash('Contrat supprimé avec succès !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

# ========== MAIN ==========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if Copropriete.query.count() == 0:
            for data in COPROPRIETES_DATA:
                copro = Copropriete(
                    numero=data["numero"],
                    nom=f"Copropriété {data['numero']}",
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
            print("✅ Base initialisée avec 10 copropriétés")
    app.run(debug=True, host='0.0.0.0', port=5000)