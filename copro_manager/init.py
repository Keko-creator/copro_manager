from app import app, db
from database import Copropriete, populate_coproprietes

with app.app_context():
    db.create_all()
    populate_coproprietes(app)