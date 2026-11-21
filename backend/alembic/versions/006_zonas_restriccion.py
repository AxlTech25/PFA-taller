"""Trazado de la ruta y zonas de restricción de demostración (US-013).

Revision ID: 006_zonas_restriccion
Revises: 005_indices_listados
Create Date: 2026-11-21

Los dos polígonos son cajas ilustrativas dentro de las envolventes operativas
de Lima Este (migración 004). No son el catastro del INEI ni el límite oficial
de Pantanos de Villa, Lomas de Lachay ni de ninguna zona de riesgo.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "006_zonas_restriccion"
down_revision: str | None = "005_indices_listados"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE ruta
            ADD COLUMN trazado_geojson JSONB,
            ADD COLUMN evita_riesgo BOOLEAN NOT NULL DEFAULT FALSE
        """
    )
    # ST_MakeEnvelope(xmin, ymin, xmax, ymax) = (lon oeste, lat sur, lon este, lat norte).
    op.execute(
        """
        INSERT INTO zona_restriccion (nombre, tipo, geometria, severidad, activo)
        SELECT
            'DEMO · riesgo ilustrativo en Santa Anita sur',
            'RIESGO_SEGURIDAD',
            ST_MakeEnvelope(-76.975, -12.078, -76.955, -12.062, 4326),
            'ALTA',
            TRUE
        WHERE NOT EXISTS (
            SELECT 1 FROM zona_restriccion
            WHERE nombre = 'DEMO · riesgo ilustrativo en Santa Anita sur'
        )
        """
    )
    op.execute(
        """
        INSERT INTO zona_restriccion (nombre, tipo, geometria, severidad, activo)
        SELECT
            'DEMO · reserva ecológica ilustrativa en Ate sur',
            'RESERVA_ECOLOGICA',
            ST_MakeEnvelope(-76.910, -12.105, -76.885, -12.090, 4326),
            'ALTA',
            TRUE
        WHERE NOT EXISTS (
            SELECT 1 FROM zona_restriccion
            WHERE nombre = 'DEMO · reserva ecológica ilustrativa en Ate sur'
        )
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM zona_restriccion
        WHERE nombre IN (
            'DEMO · riesgo ilustrativo en Santa Anita sur',
            'DEMO · reserva ecológica ilustrativa en Ate sur'
        )
        """
    )
    op.execute("ALTER TABLE ruta DROP COLUMN IF EXISTS trazado_geojson")
    op.execute("ALTER TABLE ruta DROP COLUMN IF EXISTS evita_riesgo")
