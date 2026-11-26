"""Confirmación de entrega por parada (US-018).

Revision ID: 007_confirmacion_entrega
Revises: 006_zonas_restriccion
Create Date: 2026-11-25

Guarda quién confirmó la parada, cuándo y, si falló, el motivo. El estado
sigue en detalle_ruta.estado_entrega (PENDIENTE, ENTREGADO, FALLIDO,
REPROGRAMADO), que ya tenía su CHECK desde el esquema inicial.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "007_confirmacion_entrega"
down_revision: str | None = "006_zonas_restriccion"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE detalle_ruta
            ADD COLUMN motivo_fallo VARCHAR(250),
            ADD COLUMN confirmada_por UUID REFERENCES usuario(id_usuario),
            ADD COLUMN confirmada_en TIMESTAMPTZ
        """
    )
    # Un FALLIDO nuevo exige motivo. NOT VALID no revisa filas previas a US-018.
    op.execute(
        """
        ALTER TABLE detalle_ruta
            ADD CONSTRAINT ck_detalle_fallido_con_motivo
            CHECK (estado_entrega <> 'FALLIDO' OR motivo_fallo IS NOT NULL) NOT VALID
        """
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE detalle_ruta DROP CONSTRAINT IF EXISTS ck_detalle_fallido_con_motivo"
    )
    op.execute("ALTER TABLE detalle_ruta DROP COLUMN IF EXISTS confirmada_en")
    op.execute("ALTER TABLE detalle_ruta DROP COLUMN IF EXISTS confirmada_por")
    op.execute("ALTER TABLE detalle_ruta DROP COLUMN IF EXISTS motivo_fallo")
