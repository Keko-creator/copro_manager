"""Ajout adresse, code_postal, ville pour les coproprietaires

Revision ID: c1a2b3c4d5e6
Revises: 7b7f2948cc18
Create Date: 2026-09-14 07:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1a2b3c4d5e6'
down_revision = '7b7f2948cc18'
branch_labels = None
depends_on = None


def upgrade():
    # La table des copropriétaires peut s'appeler « coproprietaire » (schéma
    # créé par db.create_all) ou « coproprietaires » (migration Alembic).
    # On gère les deux cas pour rester robuste.
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    table = 'coproprietaire' if 'coproprietaire' in tables else 'coproprietaires'
    if table not in tables:
        return

    existing_cols = {c['name'] for c in inspector.get_columns(table)}
    with op.batch_alter_table(table, schema=None) as batch_op:
        if 'adresse' not in existing_cols:
            batch_op.add_column(sa.Column('adresse', sa.String(length=300), nullable=True))
        if 'code_postal' not in existing_cols:
            batch_op.add_column(sa.Column('code_postal', sa.String(length=20), nullable=True))
        if 'ville' not in existing_cols:
            batch_op.add_column(sa.Column('ville', sa.String(length=100), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()
    table = 'coproprietaire' if 'coproprietaire' in tables else 'coproprietaires'
    if table not in tables:
        return
    with op.batch_alter_table(table, schema=None) as batch_op:
        batch_op.drop_column('ville')
        batch_op.drop_column('code_postal')
        batch_op.drop_column('adresse')
