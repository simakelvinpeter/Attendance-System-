from alembic import op
import sqlalchemy as sa


revision = '196e0b7cd858'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'attendance',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('student_id', sa.String(50), nullable=False),
        sa.Column('fingerprint_template', sa.LargeBinary, nullable=False),
        sa.Column('scan_time', sa.DateTime, server_default=sa.func.current_timestamp(), nullable=False)
    )


def downgrade():
    op.drop_table('attendance')
