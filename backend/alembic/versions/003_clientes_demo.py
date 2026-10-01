"""Clientes de demostración para el alta de pedidos (US-008 A).

Revision ID: 003_clientes_demo
Revises: 002_vehiculos_demo
Create Date: 2026-10-01
"""

from collections.abc import Sequence

from alembic import op

revision: str = "003_clientes_demo"
down_revision: str | None = "002_vehiculos_demo"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CORREOS = (
    "demo.consentido@distrirapido.example.com",
    "demo.sin.consentimiento@distrirapido.example.com",
)


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO cliente (nombre, telefono, email, consentimiento_datos)
        SELECT 'Bodega El Ahorro', '987654321',
               'demo.consentido@distrirapido.example.com', TRUE
        WHERE NOT EXISTS (
            SELECT 1 FROM cliente
            WHERE email = 'demo.consentido@distrirapido.example.com'
        )
        """
    )
    op.execute(
        """
        INSERT INTO cliente (nombre, telefono, email, consentimiento_datos)
        SELECT 'Bodega Los Pinos', '912000111',
               'demo.sin.consentimiento@distrirapido.example.com', FALSE
        WHERE NOT EXISTS (
            SELECT 1 FROM cliente
            WHERE email = 'demo.sin.consentimiento@distrirapido.example.com'
        )
        """
    )


def downgrade() -> None:
    correos = ", ".join(f"'{correo}'" for correo in CORREOS)
    op.execute(f"DELETE FROM cliente WHERE email IN ({correos})")
