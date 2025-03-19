"""Initial schema

Revision ID: 001
Create Date: 2025-03-19 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    # Create doctors table
    op.create_table(
        "doctors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("specialization", sa.String(), nullable=True),
        sa.Column("experience", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_doctors_id"), "doctors", ["id"], unique=False)

    # Create patients table
    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("doctor_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["doctor_id"],
            ["doctors.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_patients_id"), "patients", ["id"], unique=False)

    # Create assistants table
    op.create_table(
        "assistants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("specialization", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_assistants_id"), "assistants", ["id"], unique=False)

    # Create treatments table
    op.create_table(
        "treatments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("doctor_id", sa.Integer(), nullable=True),
        sa.Column("patient_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.ForeignKeyConstraint(
            ["doctor_id"],
            ["doctors.id"],
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_treatments_id"), "treatments", ["id"], unique=False)

    # Create patient_assistants table
    op.create_table(
        "patient_assistants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=True),
        sa.Column("assistant_id", sa.Integer(), nullable=True),
        sa.Column("assigned_by_doctor_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.ForeignKeyConstraint(
            ["assistant_id"],
            ["assistants.id"],
        ),
        sa.ForeignKeyConstraint(
            ["assigned_by_doctor_id"],
            ["doctors.id"],
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_patient_assistants_id"), "patient_assistants", ["id"], unique=False
    )

    # Create treatment_applications table
    op.create_table(
        "treatment_applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("treatment_id", sa.Integer(), nullable=True),
        sa.Column("assistant_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["assistant_id"],
            ["assistants.id"],
        ),
        sa.ForeignKeyConstraint(
            ["treatment_id"],
            ["treatments.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_treatment_applications_id"),
        "treatment_applications",
        ["id"],
        unique=False,
    )


def downgrade():
    op.drop_table("treatment_applications")
    op.drop_table("patient_assistants")
    op.drop_table("treatments")
    op.drop_table("assistants")
    op.drop_table("patients")
    op.drop_table("doctors")
    op.drop_table("users")
