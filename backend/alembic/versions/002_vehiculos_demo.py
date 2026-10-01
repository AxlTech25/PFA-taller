"""Vehículos de demostración de la flota (ENB-003).

Revision ID: 002_vehiculos_demo
Revises: 001_esquema_inicial
Create Date: 2026-09-30
"""

from collections.abc import Sequence

from alembic import op

revision: str = "002_vehiculos_demo"
down_revision: str | None = "001_esquema_inicial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PLACAS = ("DMO-101", "DMO-102", "DMO-201", "DMO-301")


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO vehiculo (
            placa, tipo, capacidad_kg, capacidad_m3, consumo_km_l,
            factor_emision_co2, anio_fabricacion, estado
        ) VALUES
            ('DMO-101', 'CAMIONETA', 1500.00, 8.00, 12.500, 0.2700, 2022, 'ACTIVO'),
            ('DMO-102', 'CAMIONETA', 1200.00, 6.50, 11.000, 0.2650, 2020, 'ACTIVO'),
            ('DMO-201', 'FURGON',    900.00, 10.00,  9.500, 0.3100, 2019, 'ACTIVO'),
            ('DMO-301', 'MOTO',       50.00,  0.20, 35.000, 0.0900, 2023, 'ACTIVO')
        ON CONFLICT (placa) DO NOTHING
        """
    )


def downgrade() -> None:
    placas = ", ".join(f"'{placa}'" for placa in PLACAS)
    op.execute(f"DELETE FROM vehiculo WHERE placa IN ({placas})")
