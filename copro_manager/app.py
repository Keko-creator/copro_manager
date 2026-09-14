from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import io
import os
import json
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
    comptable = db.Column(db.String(100))
    responsable_secteur = db.Column(db.String(200))
    commercial = db.Column(db.String(200))
    notaire = db.Column(db.String(200))
    est_active = db.Column(db.Boolean, default=True)

    # Relationships
    fiche_immeuble = db.relationship('FicheImmeuble', backref='copropriete', uselist=False)
    contrats = db.relationship('Contrat', backref='copropriete', lazy=True)
    coproprietaires = db.relationship('Coproprietaire', backref='copropriete', lazy=True)
    assemblees_generales = db.relationship('AssembleeGenerale', backref='copropriete', lazy=True)
    resolutions_futures = db.relationship('ResolutionFuture', backref='copropriete', lazy=True)
    demandes = db.relationship('Demande', backref='copropriete', lazy=True, cascade="all, delete-orphan")

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
    # Adresse postale du copropriétaire (pour correspondre au fichier Excel
    # « Copropriétaires.xlsx » et à l'onglet Copropriétaires).
    adresse = db.Column(db.String(300))
    code_postal = db.Column(db.String(20))
    ville = db.Column(db.String(100))

    locataire_nom = db.Column(db.String(100))
    locataire_civilite_id = db.Column(db.Integer, db.ForeignKey('civilites.id'), nullable=True)
    locataire_prenom = db.Column(db.String(100))
    locataire_email = db.Column(db.String(200))
    locataire_telephone = db.Column(db.String(50))

    lots = db.relationship('LotCoproprietaire', backref='coproprietaire', lazy=True, cascade="all, delete-orphan")
    emails = db.relationship('EmailCoproprietaire', backref='coproprietaire', lazy=True, cascade="all, delete-orphan")
    telephones = db.relationship('TelephoneCoproprietaire', backref='coproprietaire', lazy=True, cascade="all, delete-orphan")

    @property
    def nom_affiche(self):
        parts = [p for p in (self.nom, self.prenom) if p]
        return ' '.join(parts) or f'Copropriétaire #{self.id}'

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

class Demande(db.Model):
    __tablename__ = 'demandes'
    id = db.Column(db.Integer, primary_key=True)
    copropriete_id = db.Column(db.Integer, db.ForeignKey('copropriete.id'), nullable=False)
    date = db.Column(db.Date)
    demandeur = db.Column(db.String(200))
    type_action = db.Column(db.String(50))
    details = db.Column(db.Text)
    echeance = db.Column(db.String(200))
    suivi = db.Column(db.String(20), default='a_faire')  # a_faire | en_cours | fait

# ========== MODÈLES POUR LE TABLEAU ASSURANCE (dynamique) ==========
# Approche entité-attribut-valeur pour permettre l'ajout/suppression
# libre de lignes (copropriétés) et de colonnes (années/indicateurs).

class AssuranceColonne(db.Model):
    __tablename__ = 'assurance_colonnes'
    id = db.Column(db.Integer, primary_key=True)
    groupe = db.Column(db.String(50), nullable=False, default='Tarif')
    en_tete = db.Column(db.String(200), nullable=False)
    ordre = db.Column(db.Integer, nullable=False, default=0)
    # formule: type de calcul automatique, vide si colonne saisie à la main.
    #   prix_m2        : valeur = cotisation_annee / superficie
    #   evolution_n   : valeur = (cotisation_N - cotisation_N-1) / cotisation_N-1
    #   evolution_base: valeur = (cotisation_N - cotisation_base) / cotisation_base
    formule = db.Column(db.String(50), nullable=True)
    # parametres formule (JSON) : ex {"annee":12,"ref":11} pour l'année/colonne de référence
    formule_params = db.Column(db.Text, nullable=True)
    cellules = db.relationship('AssuranceCellule', backref='colonne', lazy=True, cascade="all, delete-orphan")

class AssuranceLigne(db.Model):
    __tablename__ = 'assurance_lignes'
    id = db.Column(db.Integer, primary_key=True)
    ordre = db.Column(db.Integer, nullable=False, default=0)
    est_total = db.Column(db.Boolean, default=False)
    cellules = db.relationship('AssuranceCellule', backref='ligne', lazy=True, cascade="all, delete-orphan")

class AssuranceCellule(db.Model):
    __tablename__ = 'assurance_cellules'
    id = db.Column(db.Integer, primary_key=True)
    ligne_id = db.Column(db.Integer, db.ForeignKey('assurance_lignes.id'), nullable=False)
    colonne_id = db.Column(db.Integer, db.ForeignKey('assurance_colonnes.id'), nullable=False)
    valeur = db.Column(db.Text)

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
    # Page dédiée pour le suivi des contrats d'assurance
    if type_contrat == 'assurance':
        return redirect(url_for('assurance_page'))
    # Page générique : à terme, un template par type pourra être ajouté
    flash("Cette page n'est pas encore disponible pour ce type de contrat.", 'info')
    return redirect(url_for('contrats'))


def _assurance_context():
    """Construit le contexte de la page Assurance depuis la base."""
    colonnes = AssuranceColonne.query.order_by(AssuranceColonne.ordre).all()
    lignes = AssuranceLigne.query.order_by(AssuranceLigne.ordre).all()

    # group_headers: nom du groupe pour chaque colonne (pour le colspan)
    group_headers = [c.groupe for c in colonnes]
    sub_headers = [c.en_tete for c in colonnes]

    # Construction d'une matrice de cellules: rows[ligne][colonne]
    rows = []
    for ligne in lignes:
        cellules = {c.colonne_id: c.valeur for c in ligne.cellules}
        row = {
            'id': ligne.id,
            'est_total': ligne.est_total,
            'valeurs': [cellules.get(col.id, '') for col in colonnes],
        }
        rows.append(row)

    total_row = next((r for r in rows if r['est_total']), None)
    data_rows = [r for r in rows if not r['est_total']]

    # Map id->en-tête pour l'édition de cellule
    colonnes_map = {c.id: c.en_tete for c in colonnes}

    # Données des formules pour le recalcul JS temps réel
    import json as _json
    colonnes_formules = {}
    for c in colonnes:
        if c.formule:
            colonnes_formules[c.id] = {
                'formule': c.formule,
                'params': _json.loads(c.formule_params) if c.formule_params else {},
            }

    # Index des colonnes par id pour le JS
    colonnes_ordre = {c.id: i for i, c in enumerate(colonnes)}

    return {
        'group_headers': group_headers,
        'sub_headers': sub_headers,
        'rows': data_rows,
        'total_row': total_row,
        'colonnes': colonnes,
        'colonnes_map': colonnes_map,
        'colonnes_formules_json': _json.dumps(colonnes_formules),
        'colonnes_ordre_json': _json.dumps(colonnes_ordre),
    }


@app.route('/contrats/assurance', endpoint='assurance_page')
def assurance_page():
    """Affiche le tableau de suivi tarifaire des contrats d'assurance,
    chargé depuis la base de données (modèle dynamique)."""
    return render_template('assurance.html', **_assurance_context())


@app.route('/contrats/assurance/export', endpoint='assurance_export')
def assurance_export():
    """Exporte le tableau d'assurance dans un fichier Excel (.xlsx).

    Reconstruit le tableau tel qu'affiché : une ligne d'en-têtes de groupe
    (Copropriété / Contrat / Tarif) fusionnée, une ligne d'en-têtes de
    colonnes, puis une ligne par copropriété (et la ligne TOTAL en dernier).
    """
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

    colonnes = AssuranceColonne.query.order_by(AssuranceColonne.ordre).all()
    lignes = AssuranceLigne.query.order_by(AssuranceLigne.ordre).all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Assurance"

    # Styles
    gras_blanc = Font(bold=True, color="FFFFFF")
    fond_groupe = PatternFill(start_color="212529", end_color="212529", fill_type="solid")
    fond_sous = PatternFill(start_color="495057", end_color="495057", fill_type="solid")
    bordure = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin"))
    centre = Alignment(horizontal="center", vertical="center", wrap_text=True)

    nb_colonnes = len(colonnes)
    if nb_colonnes == 0:
        flash("Aucune donnée à exporter.", "error")
        return redirect(url_for('assurance_page'))

    # Ligne 1 : en-têtes de groupe (fusion des colonnes d'un même groupe)
    idx = 0
    while idx < nb_colonnes:
        groupe = colonnes[idx].groupe
        debut = idx
        while idx < nb_colonnes and colonnes[idx].groupe == groupe:
            idx += 1
        ws.cell(row=1, column=debut + 1, value=groupe)
        if idx - debut > 1:
            ws.merge_cells(start_row=1, start_column=debut + 1,
                           end_row=1, end_column=idx)
        cell = ws.cell(row=1, column=debut + 1)
        cell.font = gras_blanc
        cell.fill = fond_groupe
        cell.alignment = centre
        cell.border = bordure

    # Ligne 2 : en-têtes de colonnes
    for c, col in enumerate(colonnes):
        cell = ws.cell(row=2, column=c + 1, value=col.en_tete)
        cell.font = gras_blanc
        cell.fill = fond_sous
        cell.alignment = centre
        cell.border = bordure

    # Lignes de données
    ligne_excel = 3
    for ligne in lignes:
        cellules = {cl.colonne_id: cl.valeur for cl in ligne.cellules}
        for c, col in enumerate(colonnes):
            valeur = cellules.get(col.id, '')
            if valeur == '' or valeur is None:
                continue
            # Tente de convertir en nombre quand c'est possible
            try:
                nombre = float(str(valeur).replace(' ', '').replace(',', '.'))
                if nombre == int(nombre):
                    nombre = int(nombre)
            except (ValueError, TypeError):
                nombre = str(valeur)
            cell = ws.cell(row=ligne_excel, column=c + 1, value=nombre)
            cell.border = bordure
        # Ligne TOTAL en gras
        if ligne.est_total:
            for c in range(nb_colonnes):
                cell = ws.cell(row=ligne_excel, column=c + 1)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="FFF3CD", end_color="FFF3CD", fill_type="solid")
        ligne_excel += 1

    # Largeurs de colonnes automatiques (approximation sur l'en-tête)
    for c, col in enumerate(colonnes):
        longueur = max(len(col.en_tete.split('\n')[0]) if col.en_tete else 0, 10)
        ws.column_dimensions[openpyxl.utils.get_column_letter(c + 1)].width = longueur + 2
    # Première colonne un peu plus large (n° de copro)
    if colonnes:
        ws.column_dimensions['A'].width = 14
    ws.freeze_panes = "B3"

    # Nom du fichier : assurance_AAAA-MM-JJ.xlsx
    nom_fichier = f"assurance_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    tampon = io.BytesIO()
    wb.save(tampon)
    tampon.seek(0)

    return send_file(
        tampon,
        as_attachment=True,
        download_name=nom_fichier,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def _recalculer_ligne(ligne):
    """Recalcule toutes les cellules formules d'une ligne d'assurance.
    À appeler après modification d'une cotisation ou de la superficie."""
    import json as _json
    colonnes = AssuranceColonne.query.order_by(AssuranceColonne.ordre).all()
    # Les paramètres de formule stockent des INDEX (0-N), pas des IDs.
    # On construit la correspondance index -> id de colonne.
    idx_vers_id = {i: c.id for i, c in enumerate(colonnes)}
    cellules = {c.colonne_id: c for c in ligne.cellules}

    def valeur_num(idx):
        col_id = idx_vers_id.get(idx)
        if col_id is None:
            return None
        cell = cellules.get(col_id)
        if not cell or not cell.valeur:
            return None
        try:
            v = float(str(cell.valeur).replace(',', '.').replace(' ', ''))
            return v
        except (ValueError, TypeError):
            return None

    def set_valeur(col_id, valeur):
        cell = cellules.get(col_id)
        if not cell:
            cell = AssuranceCellule(ligne_id=ligne.id, colonne_id=col_id, valeur=valeur)
            cellules[col_id] = cell
            db.session.add(cell)
        else:
            cell.valeur = valeur

    for col in colonnes:
        if not col.formule:
            continue
        params = _json.loads(col.formule_params) if col.formule_params else {}
        if col.formule == 'prix_m2':
            cotisation = valeur_num(params.get('cotisation'))
            superficie = valeur_num(params.get('superficie'))
            if cotisation is not None and superficie and superficie != 0:
                set_valeur(col.id, round(cotisation / superficie, 4))
            else:
                set_valeur(col.id, '')
        elif col.formule == 'evolution_n':
            annee = valeur_num(params.get('annee'))
            ref = valeur_num(params.get('ref'))
            if annee is not None and ref is not None and ref != 0:
                set_valeur(col.id, round((annee - ref) / ref, 4))
            else:
                set_valeur(col.id, '')
        elif col.formule == 'evolution_base':
            annee = valeur_num(params.get('annee'))
            base = valeur_num(params.get('base'))
            if annee is not None and base is not None and base != 0:
                set_valeur(col.id, round((annee - base) / base, 4))
            else:
                set_valeur(col.id, '')


@app.route('/contrats/assurance/ligne/add', methods=['POST'])
def assurance_add_ligne():
    """Ajoute une nouvelle ligne (copropriété-assurance)."""
    max_ordre = db.session.query(db.func.max(AssuranceLigne.ordre)).scalar() or 0
    # On insère avant la ligne TOTAL si elle existe
    total = AssuranceLigne.query.filter_by(est_total=True).first()
    if total:
        # décale la TOTAL à la fin
        total.ordre = max_ordre + 2
        new_ordre = max_ordre + 1
    else:
        new_ordre = max_ordre + 1
    ligne = AssuranceLigne(ordre=new_ordre, est_total=False)
    db.session.add(ligne)
    db.session.flush()
    db.session.commit()
    flash('Nouvelle ligne ajoutée. Cliquez sur les cellules pour la remplir.', 'success')
    return redirect(url_for('assurance_page'))


@app.route('/contrats/assurance/ligne/<int:ligne_id>/delete', methods=['POST'])
def assurance_delete_ligne(ligne_id):
    ligne = AssuranceLigne.query.get_or_404(ligne_id)
    db.session.delete(ligne)
    db.session.commit()
    flash('Ligne supprimée.', 'success')
    return redirect(url_for('assurance_page'))


@app.route('/contrats/assurance/colonne/add', methods=['POST'])
def assurance_add_colonne():
    """Ajoute une nouvelle colonne (année/indicateur)."""
    groupe = request.form.get('groupe') or 'Tarif'
    en_tete = request.form.get('en_tete', '').strip()
    if not en_tete:
        flash('Veuillez donner un nom à la nouvelle colonne.', 'error')
        return redirect(url_for('assurance_page'))
    max_ordre = db.session.query(db.func.max(AssuranceColonne.ordre)).scalar() or 0
    col = AssuranceColonne(groupe=groupe, en_tete=en_tete, ordre=max_ordre + 1)
    db.session.add(col)
    db.session.commit()
    flash(f'Colonne « {en_tete} » ajoutée.', 'success')
    return redirect(url_for('assurance_page'))


@app.route('/contrats/assurance/colonne/<int:colonne_id>/delete', methods=['POST'])
def assurance_delete_colonne(colonne_id):
    col = AssuranceColonne.query.get_or_404(colonne_id)
    db.session.delete(col)
    db.session.commit()
    flash('Colonne supprimée.', 'success')
    return redirect(url_for('assurance_page'))


@app.route('/contrats/assurance/cellule/save', methods=['POST'])
def assurance_save_cellule():
    """Sauvegarde la valeur d'une cellule (édition inline)."""
    ligne_id = request.form.get('ligne_id', type=int)
    colonne_id = request.form.get('colonne_id', type=int)
    valeur = request.form.get('valeur', '')
    if ligne_id is None or colonne_id is None:
        flash('Données invalides pour la cellule.', 'error')
        return redirect(url_for('assurance_page'))
    cellule = AssuranceCellule.query.filter_by(
        ligne_id=ligne_id, colonne_id=colonne_id).first()
    if cellule:
        cellule.valeur = valeur
    else:
        cellule = AssuranceCellule(ligne_id=ligne_id, colonne_id=colonne_id, valeur=valeur)
        db.session.add(cellule)
    # Recalcule les colonnes formules de cette ligne si la cellule modifiée
    # est une colonne saisie (cotisation / superficie / base).
    ligne = AssuranceLigne.query.get(ligne_id)
    if ligne and not ligne.est_total:
        _recalculer_ligne(ligne)
    db.session.commit()
    flash('Cellule sauvegardée et recalculée.', 'success')
    return redirect(url_for('assurance_page'))

@app.route('/')
def index():
    stats = get_statistiques()
    return render_template('index.html', stats=stats)


@app.route('/coproprietes', endpoint='coproprietes_liste')
def coproprietes_liste():
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
    return render_template('coproprietes_liste.html', coproprietes=coproprietes, search_query=search_query, search_type=search_type)

def _assurance_pour_copropriete(numero):
    """Récupère les données du contrat d'assurance d'une copropriété.

    La correspondance se fait sur la première colonne du tableau Assurance
    (« N° de copro ») qui contient le numéro de la copropriété.

    Renvoie un dict avec : entreprise, debut, numero_contrat, superficie,
    et le tarif + prix au m² de la dernière année tarifaire disponible
    (la plus à droite dont l'en-tête commence par « Tarif » et la cellule
    « Prix au m² » associée).
    Renvoie None si aucune ligne d'assurance ne correspond à ce numéro.
    """
    import re
    colonnes = AssuranceColonne.query.order_by(AssuranceColonne.ordre).all()
    if not colonnes:
        return None

    col_by_ordre = {i: c for i, c in enumerate(colonnes)}

    # Repère la ligne dont la première cellule vaut le numéro de la copro.
    cible = None
    for ligne in AssuranceLigne.query.order_by(AssuranceLigne.ordre).all():
        if ligne.est_total:
            continue
        cellules = {cl.colonne_id: cl.valeur for cl in ligne.cellules}
        premiere = cellules.get(colonnes[0].id, '')
        try:
            if premiere is not None and str(premiere).strip() == str(numero):
                cible = (ligne, cellules)
                break
        except (ValueError, TypeError):
            continue
    if cible is None:
        return None
    ligne, cellules = cible

    def val(ordre):
        col = col_by_ordre.get(ordre)
        if col is None:
            return ''
        return cellules.get(col.id, '') or ''

    entreprise = val(5)
    debut = val(6)
    numero_contrat = val(8)
    superficie = val(9)

    # Dernière colonne « Tarif AAAA » non vide = tarif de la dernière année.
    dernier_tarif_ordre = None
    dernier_tarif_annee = None
    for c in colonnes:
        m = re.match(r'^Tarif\s+(\d{4})$', c.en_tete.strip() if c.en_tete else '')
        if not m:
            continue
        v = cellules.get(c.id, '')
        if v not in (None, '', '0', 0):
            dernier_tarif_ordre = c.ordre
            dernier_tarif_annee = m.group(1)

    dernier_tarif = ''
    dernier_prix_m2 = ''
    if dernier_tarif_ordre is not None:
        dernier_tarif = val(dernier_tarif_ordre)
        # Colonne « Prix au m²/€TTC AAAA » située juste après le tarif de l'année.
        for c in colonnes:
            if (c.en_tete and c.formule == 'prix_m2'
                    and c.ordre > dernier_tarif_ordre
                    and dernier_tarif_annee and dernier_tarif_annee in c.en_tete):
                dernier_prix_m2 = cellules.get(c.id, '') or ''
                break

    return {
        'entreprise': entreprise,
        'debut': debut,
        'numero_contrat': numero_contrat,
        'superficie': superficie,
        'derniere_annee': dernier_tarif_annee,
        'dernier_tarif': dernier_tarif,
        'dernier_prix_m2': dernier_prix_m2,
    }


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
    assurance_contrat = _assurance_pour_copropriete(copropriete.numero)

    return render_template(
        'copropriete.html',
        copropriete=copropriete,
        contrats=copropriete.contrats,
        coproprietaires=copropriete.coproprietaires,
        assemblees=copropriete.assemblees_generales,
        resolutions=copropriete.resolutions_futures,
        demandes=copropriete.demandes,
        types_contrats=types_contrats,
        civilites=civilites,
        assurance_contrat=assurance_contrat
    )

@app.route('/coproprietaire/<int:coproprietaire_id>/delete', methods=['POST'])
def delete_coproprietaire(coproprietaire_id):
    coproprietaire = Coproprietaire.query.get_or_404(coproprietaire_id)
    copro_id = coproprietaire.copropriete_id
    db.session.delete(coproprietaire)
    db.session.commit()
    flash('Copropriétaire supprimé avec succès !', 'success')
    if request.form.get('from') == 'coproprietaires' or request.args.get('from') == 'coproprietaires':
        return redirect(url_for('coproprietaires_page'))
    return redirect(url_for('copropriete', copro_id=copro_id))

# ========== ONGLET COPROPRIÉTAIRES (vue globale) ==========
@app.route('/coproprietaires', endpoint='coproprietaires_page')
def coproprietaires_page():
    """Tableau dynamique de tous les copropriétaires, groupés par N° de copro."""
    search_query = request.args.get('q', '').strip()
    filter_copro = request.args.get('copro', '').strip()

    query = Coproprietaire.query.join(Copropriete)
    if filter_copro:
        try:
            num = int(filter_copro)
            query = query.filter(Copropriete.numero == num)
        except (ValueError, TypeError):
            query = query.filter(Copropriete.nom.ilike(f'%{filter_copro}%'))
    if search_query:
        like = f'%{search_query}%'
        query = query.filter(
            db.or_(
                Coproprietaire.nom.ilike(like),
                Coproprietaire.prenom.ilike(like),
                Coproprietaire.email.ilike(like),
                Coproprietaire.telephone.ilike(like),
                Coproprietaire.adresse.ilike(like),
                Coproprietaire.ville.ilike(like),
                Copropriete.nom.ilike(like),
            )
        )
    # Tri par N° de copro puis par id d'insertion : un copropriétaire ajouté
    # depuis la fiche copropriété apparaît après les copropriétaires existants
    # de la même copropriété (id croissant).
    query = query.order_by(Copropriete.numero, Coproprietaire.id)
    coproprietaires = query.all()

    copros = Copropriete.query.order_by(Copropriete.numero).all()
    civilites = Civilite.query.all()
    return render_template(
        'coproprietaires.html',
        coproprietaires=coproprietaires,
        copros=copros,
        civilites=civilites,
        search_query=search_query,
        filter_copro=filter_copro,
    )


@app.route('/coproprietaires/export', endpoint='coproprietaires_export')
def coproprietaires_export():
    """Exporte le tableau de l'onglet Copropriétaires en fichier Excel (.xlsx)."""
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

    query = Coproprietaire.query.join(Copropriete).order_by(Copropriete.numero, Coproprietaire.id)
    coproprietaires = query.all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Copropriétaires"

    headers = [
        'N° de copro', 'Civilité', 'Nom', 'Prénom', 'Lots',
        'Adresse', 'Code postal', 'Ville',
        'Téléphones Principal', 'Téléphone Secondaire', 'Emails Principal',
    ]
    gras_blanc = Font(bold=True, color="FFFFFF")
    fond = PatternFill(start_color="212529", end_color="212529", fill_type="solid")
    bordure = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin"))
    centre = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for c, h in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=c, value=h)
        cell.font = gras_blanc
        cell.fill = fond
        cell.alignment = centre
        cell.border = bordure

    ligne = 2
    for cp in coproprietaires:
        lots_str = ', '.join(
            f"{lot.numero}{(' ' + lot.nature) if lot.nature else ''}" for lot in cp.lots
        ) or (cp.numero_lot or 'NC')
        email_principal = next((e.value for e in cp.emails if e.principal), None) or cp.email or ''
        email_secondaire = ', '.join(e.value for e in cp.emails if not e.principal)
        tel_principal = next((t.value for t in cp.telephones if t.principal), None) or cp.telephone or ''
        tel_secondaire = ', '.join(t.value for t in cp.telephones if not t.principal)
        valeurs = [
            cp.copropriete.numero,
            cp.civilite.libelle if cp.civilite else '',
            cp.nom or '',
            cp.prenom or '',
            lots_str,
            cp.adresse or '',
            cp.code_postal or '',
            cp.ville or '',
            tel_principal,
            tel_secondaire,
            email_principal,
        ]
        for c, v in enumerate(valeurs, start=1):
            cell = ws.cell(row=ligne, column=c, value=v)
            cell.border = bordure
        ligne += 1

    largeurs = [12, 20, 24, 24, 18, 30, 12, 18, 22, 22, 30]
    for c, w in enumerate(largeurs, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(c)].width = w
    ws.freeze_panes = "A2"

    nom_fichier = f"coproprietaires_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    tampon = io.BytesIO()
    wb.save(tampon)
    tampon.seek(0)
    return send_file(
        tampon,
        as_attachment=True,
        download_name=nom_fichier,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route('/coproprietaire/<int:coproprietaire_id>/edit-inline', endpoint='coproprietaire_edit_inline')
def coproprietaire_edit_inline(coproprietaire_id):
    """Renvoie le contenu HTML d'une modale d'édition d'un copropriétaire,
    destiné à être chargé en AJAX depuis l'onglet Copropriétaires.
    """
    cp = Coproprietaire.query.get_or_404(coproprietaire_id)
    civilites = Civilite.query.all()
    return render_template('coproprietaire_edit_inline.html', cp=cp, civilites=civilites)


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
            comptable=request.form.get('comptable'),
            responsable_secteur=request.form.get('responsable_secteur'),
            commercial=request.form.get('commercial'),
            notaire=request.form.get('notaire'),
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
        comptable = request.form.get('comptable')
        responsable_secteur = request.form.get('responsable_secteur')
        commercial = request.form.get('commercial')
        notaire = request.form.get('notaire')
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
        copropriete.comptable = comptable
        copropriete.responsable_secteur = responsable_secteur
        copropriete.commercial = commercial
        copropriete.notaire = notaire
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
    statut = request.form.get('statut')
    # Compatibilité : la fiche copropriété utilise des radios « statut »
    # (residence/loue/autre), tandis que d'autres formulaires utilisent des
    # champs cachés est_residence_principale/est_loue. On déduit le statut
    # depuis les deux formats.
    if 'est_residence_principale' in request.form:
        est_residence_principale = True
    elif statut == 'residence':
        est_residence_principale = True
    else:
        est_residence_principale = False
    if 'est_loue' in request.form:
        est_loue = True
    elif statut == 'loue':
        est_loue = True
    else:
        est_loue = False
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
        # Conserve le lien espace client existant si le champ n'est pas
        # soumis (le champ a été retiré des formulaires).
        if 'lien_espace_client' in request.form:
            cp.lien_espace_client = lien_espace_client
        cp.locataire_nom = locataire_nom
        cp.locataire_prenom = locataire_prenom
        cp.locataire_email = locataire_email
        cp.civilite_id = civilite_id
        cp.locataire_civilite_id = locataire_civilite_id
        cp.locataire_telephone = locataire_telephone
        cp.adresse = request.form.get('adresse')
        cp.code_postal = request.form.get('code_postal')
        cp.ville = request.form.get('ville')

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

    if request.form.get('from') == 'coproprietaires':
        return redirect(url_for('coproprietaires_page'))
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

# ========== DEMANDES ROUTES ==========
@app.route('/demande/save', methods=['POST'])
def save_demande():
    copro_id = request.form.get('copro_id')
    demande_id = request.form.get('demande_id')

    if demande_id:
        demande = Demande.query.get(demande_id)
        if not demande:
            flash('Demande non trouvée', 'error')
            return redirect(url_for('copropriete', copro_id=copro_id))
    else:
        demande = Demande(copropriete_id=copro_id)

    demande.date = parse_date(request.form.get('date'))
    demande.demandeur = request.form.get('demandeur')
    if demande.demandeur == '__autre__':
        demande.demandeur = request.form.get('demandeur_autre', '').strip()
    demande.type_action = request.form.get('type_action')
    demande.details = request.form.get('details')
    demande.echeance = request.form.get('echeance')
    demande.suivi = request.form.get('suivi', 'a_faire')

    db.session.add(demande)
    db.session.commit()
    flash('Demande sauvegardée avec succès !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

@app.route('/demande/<int:demande_id>/delete', methods=['POST'])
def delete_demande(demande_id):
    demande = Demande.query.get_or_404(demande_id)
    copro_id = demande.copropriete_id
    db.session.delete(demande)
    db.session.commit()
    flash('Demande supprimée avec succès !', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

@app.route('/demande/<int:demande_id>/suivi', methods=['POST'])
def demande_suivi(demande_id):
    demande = Demande.query.get_or_404(demande_id)
    copro_id = demande.copropriete_id
    suivi = request.form.get('suivi', 'a_faire')
    if suivi not in ('a_faire', 'en_cours', 'fait'):
        suivi = 'a_faire'
    demande.suivi = suivi
    db.session.commit()
    flash('Suivi mis à jour.', 'success')
    return redirect(url_for('copropriete', copro_id=copro_id))

def _migrer_colonnes_coproprietaires():
    """Ajoute les colonnes adresse/code_postal/ville à la table des
    copropriétaires si elles manquent (db.create_all ne modifie pas une
    table existante). Compatible avec les noms de table « coproprietaire »
    et « coproprietaires ».
    """
    from sqlalchemy import inspect, text
    engine = db.engine
    insp = inspect(engine)
    tables = insp.get_table_names()
    table = 'coproprietaire' if 'coproprietaire' in tables else 'coproprietaires'
    if table not in tables:
        return
    cols = {c['name'] for c in insp.get_columns(table)}
    with engine.begin() as conn:
        if 'adresse' not in cols:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN adresse VARCHAR(300)"))
        if 'code_postal' not in cols:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN code_postal VARCHAR(20)"))
        if 'ville' not in cols:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN ville VARCHAR(100)"))


def _importer_coproprietaires_excel():
    """Importe les copropriétaires du fichier Copropriétaires.xlsx (une
    seule fois, si la table est vide). Associe chaque ligne à la copropriété
    dont le numéro correspond à la colonne « N° de copro ».
    """
    import openpyxl
    if Coproprietaire.query.count() > 0:
        return
    chemin = os.path.join(os.path.dirname(__file__), 'Copropriétaires.xlsx')
    if not os.path.exists(chemin):
        return
    try:
        wb = openpyxl.load_workbook(chemin, data_only=True, read_only=True)
    except Exception as e:
        app.logger.warning(f"Impossible de lire Copropriétaires.xlsx : {e}")
        return
    ws = wb.active
    rows = ws.iter_rows(values_only=True)
    headers = next(rows, None)
    if not headers:
        return
    idx = {h: i for i, h in enumerate(headers) if h}

    copros = {c.numero: c for c in Copropriete.query.all()}
    civilites = {c.libelle: c for c in Civilite.query.all()}

    def val(row, name):
        i = idx.get(name)
        if i is None or i >= len(row):
            return None
        v = row[i]
        return None if v is None else str(v).strip()

    nb = 0
    for row in rows:
        numero_copro = val(row, 'N° de copro')
        if not numero_copro:
            continue
        try:
            numero_copro = int(float(numero_copro))
        except (ValueError, TypeError):
            continue
        copro = copros.get(numero_copro)
        if not copro:
            continue
        civilite_lib = val(row, 'Civilité')
        civilite = civilites.get(civilite_lib) if civilite_lib else None
        lots_str = val(row, 'Lots') or ''
        cp = Coproprietaire(
            copropriete_id=copro.id,
            civilite_id=civilite.id if civilite else None,
            nom=val(row, 'Nom'),
            prenom=val(row, 'Prénom'),
            adresse=val(row, 'Adresse'),
            code_postal=str(val(row, 'Code postal')) if val(row, 'Code postal') else None,
            ville=val(row, 'Ville'),
            telephone=val(row, 'Téléphones Principal'),
            email=val(row, 'Emails Principal'),
        )
        premier_lot = next((p.strip() for p in lots_str.replace(';', ',').split(',') if p.strip()), None)
        if premier_lot and premier_lot.upper() != 'NC':
            cp.numero_lot = premier_lot
        db.session.add(cp)
        nb += 1
    db.session.commit()
    if nb:
        app.logger.info(f"{nb} copropriétaires importés depuis Copropriétaires.xlsx")


# ========== MAIN ==========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        _migrer_colonnes_coproprietaires()

        # Initialiser les civilités si elles n'existent pas
        civilites_data = ["Monsieur", "Madame", "Monsieur et Madame", "Société"]
        for libelle in civilites_data:
            if not Civilite.query.filter_by(libelle=libelle).first():
                civilite = Civilite(libelle=libelle)
                db.session.add(civilite)
        db.session.commit()
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

        # Importer les copropriétaires depuis le fichier Excel (une fois)
        _importer_coproprietaires_excel()

    app.run(debug=True, host='0.0.0.0', port=5000)
