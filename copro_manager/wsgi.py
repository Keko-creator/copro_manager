"""Point d'entrée pour l'hébergement multi-utilisateurs.

Initialise la base de données au démarrage puis sert l'application avec
waitress (serveur de production Windows, sans dépendances externes).
"""
import os

from dotenv import load_dotenv
from waitress import serve

from app import (
    app, db, Copropriete, Civilite, COPROPRIETES_DATA, parse_date,
    _migrer_colonnes_coproprietaires, _migrer_coproprietaires,
    _migrer_lots_categories,
    _importer_coproprietaires_excel, _importer_honoraires,
    _importer_visites, _importer_travaux,
)


def initialiser_base():
    with app.app_context():
        db.create_all()
        _migrer_colonnes_coproprietaires()

        for libelle in ["Monsieur", "Madame", "Monsieur et Madame", "Société"]:
            if not Civilite.query.filter_by(libelle=libelle).first():
                db.session.add(Civilite(libelle=libelle))
        db.session.commit()

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

        _migrer_coproprietaires()
        _migrer_lots_categories()
        _importer_coproprietaires_excel()
        _importer_honoraires()
        _importer_visites()
        _importer_travaux()


if __name__ == '__main__':
    load_dotenv()
    initialiser_base()
    host = os.environ.get('COPRO_HOST', '0.0.0.0')
    port = int(os.environ.get('COPRO_PORT', '5000'))
    print(f"Copro Manager démarré sur http://{host}:{port} (CTRL+C pour arrêter)")
    serve(app, host=host, port=port)
