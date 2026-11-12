"""Índices de columnas filtradas u ordenadas por los listados.

Revision ID: 005_indices_listados
Revises: 004_sprint3_cobertura
Create Date: 2026-11-12

La migración 001 ya indexa estado, placa, fecha y claves foráneas de pedido.
Estas columnas se usan en ORDER BY o en el filtro del detalle y no tenían índice.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "005_indices_listados"
down_revision: str | None = "004_sprint3_cobertura"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE INDEX idx_detalle_ruta_id_ruta ON detalle_ruta (id_ruta)")
    op.execute("CREATE INDEX idx_ruta_id_job ON ruta (id_job)")
    op.execute("CREATE INDEX idx_pedido_creado_en ON pedido (creado_en DESC)")
    op.execute("CREATE INDEX idx_conductor_nombre ON conductor (nombre)")
    op.execute("CREATE INDEX idx_ruta_listado ON ruta (fecha DESC, generada_en DESC)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_ruta_listado")
    op.execute("DROP INDEX IF EXISTS idx_conductor_nombre")
    op.execute("DROP INDEX IF EXISTS idx_pedido_creado_en")
    op.execute("DROP INDEX IF EXISTS idx_ruta_id_job")
    op.execute("DROP INDEX IF EXISTS idx_detalle_ruta_id_ruta")
