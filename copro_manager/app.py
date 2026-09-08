from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from sqlalchemy.orm import joinedload
from database import COPROPRIETES_DATA, db, Copropriete, Civilite # <-- Ajoute COPROPRIETES_DATA

# ========== CONFIGURATION ==========
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///copro_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# ===== CONTEXT PROCESSOR (pour rendre Civilite accessible dans les templates) =====
@app.context_processor
def inject_models():
    return dict(Civilite=Civilite)

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
    civilite_id = db.Column(db.Integer, db.ForeignKey('civilites.id'), nullable=True)
    civilite = db.relationship('Civilite', backref='coproprietaires', foreign_keys=[civilite_id])
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

    locataire_nom = db.Column(db.String(100))
    locataire_civilite_id = db.Column(db.Integer, db.ForeignKey('civilites.id'), nullable=True)
    locataire_prenom = db.Column(db.String(100))
    locataire_email = db.Column(db.String(200))
    locataire_telephone = db.Column(db.String(50))

    lots = db.relationship('LotCoproprietaire', backref='coproprietaire', lazy=True, cascade="all, delete-orphan")
    emails = db.relationship('EmailCoproprietaire', backref='coproprietaire', lazy=True, cascade="all, delete-orphan")
    telephones = db.relationship('TelephoneCoproprietaire', backref='coproprietaire', lazy=True, cascade="all, delete-orphan")

class Civilite(db.Model):
    __tablename__ = 'civilites'
    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(20), unique=True, nullable=False)

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

class AssembleeGenerale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    copropriete_id = db.Column(db.Integer, db.ForeignKey('copropriete.id'), nullable=False)
    date = db.Column(db.Date)
    horaire_debut = db.Column(db.String(20))
    lieu = db.Column(db.String(200))
    type_ag = db.Column(db.String(100))  # Nouveau champ: Type d'AG

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
@app.route('/contrats')
def contrats():
    types_contrats = [
        "Assurance",
        "Nettoyage",
        "Espaces verts",
        "Sécurité incendie",
        "Sous-compteurs d'eau",
        "VMC",
        "Ascenseurs",
        "Électricité",
        "Eau",
        "Chaufferie",
        "Gaz",
        "Portes automatiques"
    ]
    
    descriptions = {
        "Assurance": "Contrats d'assurance pour les copropriétés",
        "Nettoyage": "Contrats de nettoyage des parties communes",
        "Espaces verts": "Contrats d'entretien des espaces verts",
        "Sécurité incendie": "Contrats de maintenance des systèmes de sécurité incendie",
        "Sous-compteurs d'eau": "Contrats de gestion des sous-compteurs d'eau",
        "VMC": "Contrats de maintenance des ventilations mécaniques contrôlées",
        "Ascenseurs": "Contrats de maintenance des ascenseurs",
        "Électricité": "Contrats d'approvisionnement et maintenance électrique",
        "Eau": "Contrats d'approvisionnement en eau",
        "Chaufferie": "Contrats de maintenance des systèmes de chauffage",
        "Gaz": "Contrats d'approvisionnement en gaz",
        "Portes automatiques": "Contrats de maintenance des portes automatiques"
    }
    
    types_contrats.sort()
    return render_template('contrats.html', types_contrats=types_contrats, descriptions=descriptions)

@app.route('/contrats/<type_contrat>')
def type_contrat_page(type_contrat):
    return render_template('type_contrat.html', type_contrat=type_contrat)

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
        joinedload(Copropriete.coproprietaires).joinedload(Coproprietaire.lots),
        joinedload(Copropriete.coproprietaires).joinedload(Coproprietaire.emails),
        joinedload(Copropriete.coproprietaires).joinedload(Coproprietaire.telephones),
        joinedload(Copropriete.contrats).joinedload(Contrat.prestations),
        joinedload(Copropriete.assemblees_generales).joinedload(AssembleeGenerale.points_a_retenir),
        joinedload(Copropriete.assemblees_generales).joinedload(AssembleeGenerale.budgets_travaux).joinedload(BudgetTravaux.appels_fonds),
        joinedload(Copropriete.resolutions_futures)
    ).get_or_404(copro_id)

    types_contrats = ["Assurance", "Nettoyage", "Entretien", "Sécurité", "Autre"]
    civilites = Civilite.query.all()

    return render_template(
        'copropriete.html',
        copropriete=copropriete,
        contrats=copropriete.contrats,
        coproprietaires=copropriete.coproprietaires,
        assemblees=copropriete.assemblees_generales,
        resolutions=copropriete.resolutions_futures,
        types_contrats=types_contrats,
        civilites=civilites
    )

@app.route('/coproprietaire/<int:coproprietaire_id>/delete', methods=['POST'])
def delete_coproprietaire(coproprietaire_id):
    coproprietaire = Coproprietaire.query.get_or_404(coproprietaire_id)
    copro_id = coproprietaire.copropriete_id
    db.session.delete(coproprietaire)
    db.session.commit()
    flash('Copropriétaire supprimé avec succès !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

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

@app.route('/copropriete/<int:copro_id>/edit', methods=['GET', 'POST'])
def edit_copropriete(copro_id):
    copropriete = Copropriete.query.get_or_404(copro_id)

    if request.method == 'POST':
        # Récupère les données du formulaire
        numero = int(request.form.get('numero'))
        nom = request.form.get('nom')
        date_mise_copropriete = parse_date(request.form.get('date_mise_copropriete'))
        programme_neolia = request.form.get('programme_neolia')
        adresse = request.form.get('adresse')
        ville = request.form.get('ville')
        immatriculation = request.form.get('immatriculation')
        nombre_logements = int(request.form.get('nombre_logements') or 0)
        exercice_comptable = request.form.get('exercice_comptable')
        gestionnaire = request.form.get('gestionnaire')
        est_active = 'est_active' in request.form

        # Vérifie si le numéro existe déjà (sauf pour la copropriété actuelle)
        existing = Copropriete.query.filter(
            Copropriete.numero == numero,
            Copropriete.id != copro_id
        ).first()
        if existing:
            flash(f'Le numéro {numero} existe déjà !', 'error')
            return redirect(url_for('edit_copropriete', copro_id=copro_id))

        # Met à jour les champs
        copropriete.numero = numero
        copropriete.nom = nom
        copropriete.date_mise_copropriete = date_mise_copropriete
        copropriete.programme_neolia = programme_neolia
        copropriete.adresse = adresse
        copropriete.ville = ville
        copropriete.immatriculation = immatriculation
        copropriete.nombre_logements = nombre_logements
        copropriete.exercice_comptable = exercice_comptable
        copropriete.gestionnaire = gestionnaire
        copropriete.est_active = est_active

        db.session.commit()
        flash(f'Copropriété #{numero} modifiée avec succès !', 'success')
        return redirect(url_for('copropriete', copro_id=copro_id))

    # Si GET, affiche le formulaire avec les données actuelles
    return render_template('edit_copropriete.html', copropriete=copropriete)

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

# ========== COPROPRIETAIRE ROUTES ==========
@app.route('/save_coproprietaire', methods=['POST'])
def save_coproprietaire():
    copro_id = request.form.get('copro_id')
    coproprietaire_id = request.form.get('coproprietaire_id')

    # --- Récupération des données simples ---
    nom = request.form.get('persons[0][nom]') or request.form.get('nom')
    prenom = request.form.get('persons[0][prenom]') or request.form.get('prenom')
    civilite_id = request.form.get('persons[0][civilite_id]') or request.form.get('civilite_id')
    date_acquisition = parse_date(request.form.get('date_acquisition'))
    est_residence_principale = 'est_residence_principale' in request.form
    est_loue = 'est_loue' in request.form
    date_envoi_mail_accueil = parse_date(request.form.get('date_envoi_mail_accueil'))
    lien_espace_client = request.form.get('lien_espace_client')

    # --- Récupération des infos du locataire ---
    locataire_nom = request.form.get('locataire_nom')
    locataire_civilite_id = request.form.get('locataire_civilite_id')
    locataire_prenom = request.form.get('locataire_prenom')
    locataire_email = request.form.get('locataire_email')
    locataire_telephone = request.form.get('locataire_telephone')

    # --- Validation ---
    if est_residence_principale and est_loue:
        flash("Un copropriétaire ne peut pas être à la fois en résidence principale et avoir un lot loué.", "error")
        return redirect(url_for('copropriete', copro_id=copro_id))

    if est_loue and not locataire_nom:
        flash("Le nom du locataire est obligatoire si le lot est loué.", "error")
        return redirect(url_for('copropriete', copro_id=copro_id))

    # --- Récupération des LOTS (nouveau format) ---
    lots_data = []
    for key in request.form:
        if key.startswith('lots[') and key.endswith('][numero]'):
            index = key.split('[')[1].split(']')[0]
            numero = request.form.get(f'lots[{index}][numero]')
            nature = request.form.get(f'lots[{index}][nature]', '')
            if numero:
                lots_data.append({'numero': numero, 'nature': nature})

    if not lots_data:
        flash("Au moins un lot est obligatoire.", "error")
        return redirect(url_for('copropriete', copro_id=copro_id))

    # --- Récupération des EMAILS ---
    emails_data = []
    principal_email_count = 0
    for key in request.form:
        if key.startswith('emails[') and key.endswith('][value]'):
            index = key.split('[')[1].split(']')[0]
            value = request.form.get(f'emails[{index}][value]')
            principal = request.form.get(f'emails[{index}][principal]') == '1'
            if value:
                if principal:
                    principal_email_count += 1
                emails_data.append({'value': value, 'principal': principal})

    if principal_email_count > 1:
        flash("Un seul email peut être marqué comme principal.", "error")
        return redirect(url_for('copropriete', copro_id=copro_id))

    # --- Récupération des TÉLÉPHONES ---
    telephones_data = []
    principal_phone_count = 0
    for key in request.form:
        if key.startswith('telephones[') and key.endswith('][value]'):
            index = key.split('[')[1].split(']')[0]
            value = request.form.get(f'telephones[{index}][value]')
            principal = request.form.get(f'telephones[{index}][principal]') == '1'
            if value:
                if principal:
                    principal_phone_count += 1
                telephones_data.append({'value': value, 'principal': principal})

    if principal_phone_count > 1:
        flash("Un seul téléphone peut être marqué comme principal.", "error")
        return redirect(url_for('copropriete', copro_id=copro_id))

    # --- Sauvegarde ---
    try:
        if coproprietaire_id:
            cp = Coproprietaire.query.get(coproprietaire_id)
            if not cp:
                flash('Copropriétaire non trouvé', 'error')
                return redirect(url_for('copropriete', copro_id=copro_id))
        else:
            cp = Coproprietaire(copropriete_id=copro_id)

        cp.nom = nom
        cp.prenom = prenom
        cp.date_acquisition = date_acquisition
        cp.est_residence_principale = est_residence_principale
        cp.est_loue = est_loue
        cp.date_envoi_mail_accueil = date_envoi_mail_accueil
        cp.lien_espace_client = lien_espace_client
        cp.locataire_nom = locataire_nom
        cp.locataire_prenom = locataire_prenom
        cp.locataire_email = locataire_email
        cp.civilite_id = civilite_id
        cp.locataire_civilite_id = locataire_civilite_id
        cp.locataire_telephone = locataire_telephone

        cp.lots = [LotCoproprietaire(numero=lot['numero'], nature=lot['nature']) for lot in lots_data]
        cp.emails = [EmailCoproprietaire(value=email['value'], principal=email['principal']) for email in emails_data]
        cp.telephones = [TelephoneCoproprietaire(value=tel['value'], principal=tel['principal']) for tel in telephones_data]

        db.session.add(cp)
        db.session.commit()
        flash('Copropriétaire sauvegardé avec succès !', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la sauvegarde : {str(e)}", "error")
        app.logger.error(f"Erreur: {str(e)}")

    return redirect(url_for('copropriete', copro_id=copro_id))

# ========== AG ROUTES ==========
@app.route('/ag/save', methods=['POST'])
def save_ag():
    copro_id = request.form.get('copro_id')
    ag_id = request.form.get('ag_id')

    if ag_id:
        ag = AssembleeGenerale.query.get(ag_id)
        if not ag:
            flash('AG non trouvée', 'error')
            return redirect(url_for('copropriete', copro_id=copro_id))
    else:
        ag = AssembleeGenerale(copropriete_id=copro_id)

    ag.date = parse_date(request.form.get('date'))
    ag.horaire_debut = request.form.get('horaire_debut')
    ag.lieu = request.form.get('lieu')
    ag.type_ag = request.form.get('type_ag')

    db.session.add(ag)
    db.session.commit()
    flash('AG sauvegardée avec succès !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

# ========== NOUVELLES ROUTES POUR SUPPRIMER AG ET RESOLUTION ==========

@app.route('/ag/<int:ag_id>/delete', methods=['POST'])
def delete_ag(ag_id):
    ag = AssembleeGenerale.query.get_or_404(ag_id)
    copro_id = ag.copropriete_id
    db.session.delete(ag)
    db.session.commit()
    flash('Assemblée Générale supprimée avec succès !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

# ========== RESOLUTION ROUTES ==========
@app.route('/resolution/save', methods=['POST'])
def save_resolution():
    copro_id = request.form.get('copro_id')
    resolution_id = request.form.get('resolution_id')

    if resolution_id:
        resolution = ResolutionFuture.query.get(resolution_id)
        if not resolution:
            flash('Résolution non trouvée', 'error')
            return redirect(url_for('copropriete', copro_id=copro_id))
    else:
        resolution = ResolutionFuture(copropriete_id=copro_id)

    resolution.titre = request.form.get('titre')
    resolution.projet = request.form.get('projet')

    db.session.add(resolution)
    db.session.commit()
    flash('Résolution sauvegardée avec succès !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

@app.route('/resolution/<int:resolution_id>/delete', methods=['POST'])
def delete_resolution(resolution_id):
    resolution = ResolutionFuture.query.get_or_404(resolution_id)
    copro_id = resolution.copropriete_id
    db.session.delete(resolution)
    db.session.commit()
    flash('Résolution supprimée avec succès !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

# ========== MAIN ==========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Initialiser les civilités si elles n'existent pas
        civilites_data = ["Monsieur", "Madame", "Monsieur et Madame", "Société"]
        for libelle in civilites_data:
            if not Civilite.query.filter_by(libelle=libelle).first():
                civilite = Civilite(libelle=libelle)
                db.session.add(civilite)
        db.session.commit()
        print("✅ Civilités initialisées : Monsieur, Madame, Monsieur et Madame, Société")
        # Initialiser les copropriétés si elles n'existent pas
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
