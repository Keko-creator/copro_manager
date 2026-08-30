from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configuration de la base de données (SQLite locale)
app.config['SECRET_KEY'] = 'ta_cle_secrete_ici_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///copro_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de la base de données
from database import db, Copropriete, FicheImmeuble, Contrat, Prestation, Coproprietaire, AssembleeGenerale, PointARetenir, BudgetTravaux, AppelFonds, ResolutionFuture

db.init_app(app)

# Liste des types de contrats par défaut
TYPES_CONTRATS = [
    "Nettoyage", "Assurance", "Eau", "Électricité", "Ascenseur",
    "Chauffage", "Gardiennage", "Jardinage", "Désinfection", "Autres"
]

# Liste des fréquences par défaut
FREQUENCES = [
    "Hebdomadaire", "Mensuel", "Trimestriel", "Annuel", "Ponctuel", "Quotidien", "Bimestriel"
]

# ==================== ROUTES PRINCIPALES ====================

@app.route('/')
def index():
    """Page d'accueil avec la liste des copropriétés"""
    coproprietes = Copropriete.query.order_by(Copropriete.numero).all()
    return render_template('index.html', coproprietes=coproprietes)

@app.route('/copropriete/<int:copro_id>')
def copropriete(copro_id):
    """Page détaillée d'une copropriété avec 4 onglets"""
    copropriete = Copropriete.query.get_or_404(copro_id)

    # Récupérer les données pour chaque onglet
    fiche_immeuble = copropriete.fiche_immeuble
    contrats = Contrat.query.filter_by(copropriete_id=copro_id).all()
    coproprietaires = Coproprietaire.query.filter_by(copropriete_id=copro_id).all()
    assemblees = AssembleeGenerale.query.filter_by(copropriete_id=copro_id).all()
    resolutions = ResolutionFuture.query.filter_by(copropriete_id=copro_id).all()

    # Préparer les données pour les tableaux
    contrats_data = []
    for contrat in contrats:
        prestations = Prestation.query.filter_by(contrat_id=contrat.id).all()
        contrats_data.append({
            'contrat': contrat,
            'prestations': prestations
        })

    ag_data = []
    for ag in assemblees:
        points = PointARetenir.query.filter_by(ag_id=ag.id).all()
        budgets = BudgetTravaux.query.filter_by(ag_id=ag.id).all()
        budgets_data = []
        for budget in budgets:
            appels = AppelFonds.query.filter_by(budget_travaux_id=budget.id).all()
            budgets_data.append({
                'budget': budget,
                'appels': appels
            })
        ag_data.append({
            'ag': ag,
            'points': points,
            'budgets': budgets_data
        })

    return render_template('copropriete.html',
                         copropriete=copropriete,
                         fiche_immeuble=fiche_immeuble,
                         contrats=contrats_data,
                         coproprietaires=coproprietaires,
                         assemblees=ag_data,
                         resolutions=resolutions,
                         types_contrats=TYPES_CONTRATS,
                         frequences=FREQUENCES)

# ==================== FICHE IMMEUBLE ====================

@app.route('/fiche-immeuble/save', methods=['POST'])
def save_fiche_immeuble():
    """Sauvegarder ou mettre à jour la fiche immeuble"""
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

    if not fiche.copropriete_id:
        fiche.copropriete_id = copro_id
        db.session.add(fiche)

    db.session.commit()
    flash('Fiche immeuble sauvegardée avec succès !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

# ==================== CONTRATS ====================

@app.route('/contrat/add', methods=['POST'])
def add_contrat():
    copro_id = request.form.get('copro_id')
    contrat = Contrat(
        copropriete_id=copro_id,
        type_contrat=request.form.get('type_contrat'),
        nature=request.form.get('nature'),
        fournisseur=request.form.get('fournisseur'),
        date_debut=parse_date(request.form.get('date_debut')),
        date_fin=parse_date(request.form.get('date_fin')),
        montant_annuel=float(request.form.get('montant_annuel') or 0)
    )
    db.session.add(contrat)
    db.session.commit()
    flash('Contrat ajouté avec succès !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

@app.route('/contrat/<int:contrat_id>/update', methods=['POST'])
def update_contrat(contrat_id):
    contrat = Contrat.query.get(contrat_id)
    if not contrat:
        flash('Contrat non trouvé', 'error')
        return redirect(url_for('index'))
    contrat.type_contrat = request.form.get('type_contrat')
    contrat.nature = request.form.get('nature')
    contrat.fournisseur = request.form.get('fournisseur')
    contrat.date_debut = parse_date(request.form.get('date_debut'))
    contrat.date_fin = parse_date(request.form.get('date_fin'))
    contrat.montant_annuel = float(request.form.get('montant_annuel') or 0)
    db.session.commit()
    flash('Contrat mis à jour !', 'success')
    return redirect(url_for('copropriete', copro_id=contrat.copropriete_id))

@app.route('/contrat/<int:contrat_id>/delete', methods=['POST'])
def delete_contrat(contrat_id):
    contrat = Contrat.query.get(contrat_id)
    if contrat:
        copro_id = contrat.copropriete_id
        db.session.delete(contrat)
        db.session.commit()
        flash('Contrat supprimé !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

# ==================== PRESTATIONS ====================

@app.route('/prestation/add', methods=['POST'])
def add_prestation():
    contrat_id = request.form.get('contrat_id')
    contrat = Contrat.query.get(contrat_id)
    if not contrat:
        flash('Contrat non trouvé', 'error')
        return redirect(url_for('index'))
    libelle = request.form.get('libelle')
    frequence = request.form.get('frequence')
    prix_unitaire = float(request.form.get('prix_unitaire') or 0)
    quantite = int(request.form.get('quantite') or 0)
    total = prix_unitaire * quantite
    prestation = Prestation(
        contrat_id=contrat_id,
        libelle=libelle,
        frequence=frequence,
        prix_unitaire=prix_unitaire,
        quantite=quantite,
        total=total
    )
    db.session.add(prestation)
    db.session.commit()
    flash('Prestation ajoutée !', 'success')
    return redirect(url_for('copropriete', copro_id=contrat.copropriete_id))

@app.route('/prestation/<int:prestation_id>/delete', methods=['POST'])
def delete_prestation(prestation_id):
    prestation = Prestation.query.get(prestation_id)
    if prestation:
        copro_id = prestation.contrat.copropriete_id
        db.session.delete(prestation)
        db.session.commit()
        flash('Prestation supprimée !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

# ==================== COPROPRIETAIRES ====================

@app.route('/coproprietaire/add', methods=['POST'])
def add_coproprietaire():
    copro_id = request.form.get('copro_id')
    coproprietaire = Coproprietaire(
        copropriete_id=copro_id,
        date_acquisition=parse_date(request.form.get('date_acquisition')),
        nom=request.form.get('nom'),
        prenom=request.form.get('prenom'),
        numero_lot=request.form.get('numero_lot'),
        nature_lot=request.form.get('nature_lot'),
        email=request.form.get('email'),
        telephone=request.form.get('telephone'),
        est_residence_principale=request.form.get('est_residence_principale') == 'on',
        est_loue=request.form.get('est_loue') == 'on',
        date_envoi_mail_accueil=parse_date(request.form.get('date_envoi_mail_accueil')),
        lien_espace_client=request.form.get('lien_espace_client')
    )
    db.session.add(coproprietaire)
    db.session.commit()
    flash('Copropriétaire ajouté !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

@app.route('/coproprietaire/<int:copro_id>/update', methods=['POST'])
def update_coproprietaire(copro_id):
    coproprietaire = Coproprietaire.query.get(copro_id)
    if not coproprietaire:
        flash('Copropriétaire non trouvé', 'error')
        return redirect(url_for('index'))
    coproprietaire.date_acquisition = parse_date(request.form.get('date_acquisition'))
    coproprietaire.nom = request.form.get('nom')
    coproprietaire.prenom = request.form.get('prenom')
    coproprietaire.numero_lot = request.form.get('numero_lot')
    coproprietaire.nature_lot = request.form.get('nature_lot')
    coproprietaire.email = request.form.get('email')
    coproprietaire.telephone = request.form.get('telephone')
    coproprietaire.est_residence_principale = request.form.get('est_residence_principale') == 'on'
    coproprietaire.est_loue = request.form.get('est_loue') == 'on'
    coproprietaire.date_envoi_mail_accueil = parse_date(request.form.get('date_envoi_mail_accueil'))
    coproprietaire.lien_espace_client = request.form.get('lien_espace_client')
    db.session.commit()
    flash('Copropriétaire mis à jour !', 'success')
    return redirect(url_for('copropriete', copro_id=coproprietaire.copropriete_id))

@app.route('/coproprietaire/<int:copro_id>/delete', methods=['POST'])
def delete_coproprietaire(copro_id):
    coproprietaire = Coproprietaire.query.get(copro_id)
    if coproprietaire:
        copropriete_id = coproprietaire.copropriete_id
        db.session.delete(coproprietaire)
        db.session.commit()
        flash('Copropriétaire supprimé !', 'success')
    return redirect(url_for('copropriete', copro_id=copropriete_id))

# ==================== ASSEMBLEES GENERALES ====================

@app.route('/ag/add', methods=['POST'])
def add_ag():
    copro_id = request.form.get('copro_id')
    ag = AssembleeGenerale(
        copropriete_id=copro_id,
        date=parse_date(request.form.get('date')),
        horaire_debut=request.form.get('horaire_debut'),
        horaire_fin=request.form.get('horaire_fin'),
        lieu=request.form.get('lieu'),
        lien_pv=request.form.get('lien_pv'),
        comptes_approuves=request.form.get('comptes_approuves') == 'on',
        montant_depenses_exercice_cloture=float(request.form.get('montant_depenses_exercice_cloture') or 0),
        montant_budget_exercice_cloture=float(request.form.get('montant_budget_exercice_cloture') or 0),
        montant_budget_exercice_en_cours=float(request.form.get('montant_budget_exercice_en_cours') or 0),
        montant_budget_exercice_a_venir=float(request.form.get('montant_budget_exercice_a_venir') or 0),
        honoraires_syndic=float(request.form.get('honoraires_syndic') or 0),
        periode_honoraires_syndic=request.form.get('periode_honoraires_syndic')
    )
    db.session.add(ag)
    db.session.commit()
    flash('Assemblée générale ajoutée !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

@app.route('/ag/<int:ag_id>/delete', methods=['POST'])
def delete_ag(ag_id):
    ag = AssembleeGenerale.query.get(ag_id)
    if ag:
        copro_id = ag.copropriete_id
        db.session.delete(ag)
        db.session.commit()
        flash('AG supprimée !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

# ==================== RESOLUTIONS FUTURES ====================

@app.route('/resolution/add', methods=['POST'])
def add_resolution():
    copro_id = request.form.get('copro_id')
    resolution = ResolutionFuture(
        copropriete_id=copro_id,
        titre=request.form.get('titre'),
        projet=request.form.get('projet')
    )
    db.session.add(resolution)
    db.session.commit()
    flash('Résolution future ajoutée !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

@app.route('/resolution/<int:resolution_id>/delete', methods=['POST'])
def delete_resolution(resolution_id):
    resolution = ResolutionFuture.query.get(resolution_id)
    if resolution:
        copro_id = resolution.copropriete_id
        db.session.delete(resolution)
        db.session.commit()
        flash('Résolution supprimée !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

# ==================== UTILITAIRES ====================

def parse_date(date_str):
    """Parser une date au format DD/MM/YYYY ou YYYY-MM-DD"""
    if not date_str:
        return None
    try:
        if '/' in date_str:
            return datetime.strptime(date_str, '%d/%m/%Y').date()
        else:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

# ==================== INITIALISATION ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)# ======================
# FONCTIONS STATISTIQUES
# ======================
def get_statistiques():
    from models import Copropriete, Coproprietaire, Contrat

    # 1. Nombre total de logements (uniquement copropriétés ACTIVES)
    total_logements = db.session.query(
        db.func.sum(Copropriete.nombre_logements)
    ).filter(Copropriete.est_active == True).scalar() or 0

    # 2. Répartition par gestionnaire (AJ/KS) - COPRO ACTIVES SEULEMENT
    stats_gestionnaires = db.session.query(
        Copropriete.gestionnaire,
        db.func.count(Copropriete.id).label('count'),
        db.func.sum(Copropriete.nombre_logements).label('logements')
    ).filter(
        Copropriete.est_active == True,
        Copropriete.gestionnaire.isnot(None)
    ).group_by(Copropriete.gestionnaire).all()

    gestionnaires = {}
    for g in stats_gestionnaires:
        gestionnaires[g.gestionnaire] = {
            'count': g.count,
            'logements': g.logements,
            'percentage': round((g.count / db.session.query(Copropriete).filter(Copropriete.est_active == True).count() * 100), 1) if db.session.query(Copropriete).filter(Copropriete.est_active == True).count() > 0 else 0
        }

    # 3. Répartition par période comptable (30-juin/31-déc) - COPRO ACTIVES SEULEMENT
    stats_periodes = db.session.query(
        Copropriete.exercice_comptable,
        db.func.count(Copropriete.id).label('count')
    ).filter(
        Copropriete.est_active == True,
        Copropriete.exercice_comptable.isnot(None)
    ).group_by(Copropriete.exercice_comptable).all()

    periodes = {}
    for p in stats_periodes:
        periodes[p.exercice_comptable] = {
            'count': p.count,
            'percentage': round((p.count / db.session.query(Copropriete).filter(Copropriete.est_active == True).count() * 100), 1) if db.session.query(Copropriete).filter(Copropriete.est_active == True).count() > 0 else 0
        }

    # 4. Nombre total de copropriétés ACTIVES
    total_copros_active = db.session.query(Copropriete).filter(Copropriete.est_active == True).count()
    total_copros_inactive = db.session.query(Copropriete).filter(Copropriete.est_active == False).count()

    return {
        'total_logements': total_logements,
        'gestionnaires': gestionnaires,
        'periodes': periodes,
        'total_active': total_copros_active,
        'total_inactive': total_copros_inactive
    }# ======================
# ROUTES NOUVELLES
# ======================

# --- Route pour la page d'accueil (avec stats) ---
@app.route('/')
def index():
    stats = get_statistiques()
    coproprietes = Copropriete.query.order_by(Copropriete.numero).all()
    return render_template('index.html', coproprietes=coproprietes, stats=stats)

# --- Désactiver/Réactiver une copropriété ---
@app.route('/copropriete/<int:copropriete_id>/toggle_active', methods=['POST'])
def toggle_active(copropriete_id):
    copro = Copropriete.query.get_or_404(copropriete_id)
    new_status = not copro.est_active
    copro.est_active = new_status
    db.session.commit()

    action = "désactivée" if not new_status else "réactivée"
    flash(f"Copropriété #{copro.numero} a été {action} avec succès.", "success")
    return redirect(url_for('index'))

# --- Ajouter une nouvelle copropriété (GET: formulaire, POST: traitement) ---
@app.route('/copropriete/new', methods=['GET', 'POST'])
def new_copropriete():
    if request.method == 'POST':
        # Récupération des données du formulaire
        numero = int(request.form.get('numero'))
        date_mise_copropriete = parse_date(request.form.get('date_mise_copropriete'))
        programme_neolia = request.form.get('programme_neolia')
        adresse = request.form.get('adresse')
        ville = request.form.get('ville')
        immatriculation = request.form.get('immatriculation')
        nombre_logements = int(request.form.get('nombre_logements', 0))
        exercice_comptable = request.form.get('exercice_comptable')
        gestionnaire = request.form.get('gestionnaire')

        # Vérification que le numéro n'existe pas déjà
        existing = Copropriete.query.filter_by(numero=numero).first()
        if existing:
            flash(f"Une copropriété avec le numéro {numero} existe déjà.", "error")
            return redirect(url_for('new_copropriete'))

        # Création de la nouvelle copropriété
        new_copro = Copropriete(
            numero=numero,
            date_mise_copropriete=date_mise_copropriete,
            programme_neolia=programme_neolia,
            adresse=adresse,
            ville=ville,
            immatriculation=immatriculation,
            nombre_logements=nombre_logements,
            exercice_comptable=exercice_comptable,
            gestionnaire=gestionnaire,
            est_active=True  # Par défaut active
        )
        db.session.add(new_copro)
        db.session.commit()

        flash(f"Copropriété #{numero} ajoutée avec succès.", "success")
        return redirect(url_for('index'))

    # GET: Afficher le formulaire
    return render_template('new_copropriete.html')

# --- Recherche avancée ---
@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form.get('query', '').strip()
    search_type = request.form.get('search_type', 'copropriete')  # copropriete | coproprietaire | contrat | fournisseur

    results = []
    if query:
        if search_type == 'copropriete':
            # Recherche par numéro, adresse, ville, etc.
            results = Copropriete.query.filter(
                Copropriete.est_active == True,
                or_(
                    Copropriete.numero.ilike(f'%{query}%'),
                    Copropriete.adresse.ilike(f'%{query}%'),
                    Copropriete.ville.ilike(f'%{query}%'),
                    Copropriete.programme_neolia.ilike(f'%{query}%')
                )
            ).order_by(Copropriete.numero).all()
        elif search_type == 'coproprietaire':
            # Recherche dans les copropriétaires (nécessite une jointure)
            from models import Coproprietaire
            copro_ids = db.session.query(Coproprietaire.copropriete_id).filter(
                or_(
                    Coproprietaire.nom.ilike(f'%{query}%'),
                    Coproprietaire.email.ilike(f'%{query}%')
                )
            ).distinct().all()
            results = Copropriete.query.filter(
                Copropriete.id.in_([cid for (cid,) in copro_ids]),
                Copropriete.est_active == True
            ).order_by(Copropriete.numero).all()
        elif search_type == 'contrat':
            # Recherche dans les contrats
            from models import Contrat
            copro_ids = db.session.query(Contrat.copropriete_id).filter(
                or_(
                    Contrat.type_contrat.ilike(f'%{query}%'),
                    Contrat.nature.ilike(f'%{query}%')
                )
            ).distinct().all()
            results = Copropriete.query.filter(
                Copropriete.id.in_([cid for (cid,) in copro_ids]),
                Copropriete.est_active == True
            ).order_by(Copropriete.numero).all()
        elif search_type == 'fournisseur':
            # Recherche par fournisseur
            from models import Contrat
            copro_ids = db.session.query(Contrat.copropriete_id).filter(
                Contrat.fournisseur.ilike(f'%{query}%')
            ).distinct().all()
            results = Copropriete.query.filter(
                Copropriete.id.in_([cid for (cid,) in copro_ids]),
                Copropriete.est_active == True
            ).order_by(Copropriete.numero).all()

    return render_template('index.html', coproprietes=results, stats=get_statistiques(), search_query=query, search_type=search_type)