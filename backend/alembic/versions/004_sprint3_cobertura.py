"""Cobertura Lima Este, jornada y cola de optimización (Sprint 3).

Revision ID: 004_sprint3_cobertura
Revises: 003_clientes_demo
Create Date: 2026-10-17

Las geometrías son envolventes operativas de los cuatro distritos de cobertura
(RN-005). No son el catastro oficial del INEI; alcanzan para aceptar o rechazar
pedidos de demostración dentro de San Juan de Lurigancho, El Agustino,
Santa Anita y Ate.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "004_sprint3_cobertura"
down_revision: str | None = "003_clientes_demo"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE pedido
            ADD COLUMN georreferencia_aproximada BOOLEAN NOT NULL DEFAULT FALSE
        """
    )
    op.execute(
        """
        CREATE TABLE distrito_cobertura (
            id_distrito   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            nombre        VARCHAR(80) NOT NULL UNIQUE,
            geometria     GEOMETRY(Polygon, 4326) NOT NULL,
            activo        BOOLEAN NOT NULL DEFAULT TRUE
        )
        """
    )
    op.execute(
        "CREATE INDEX idx_distrito_geometria ON distrito_cobertura USING GIST (geometria)"
    )
    # ST_MakeEnvelope(xmin, ymin, xmax, ymax) = (lon oeste, lat sur, lon este, lat norte).
    op.execute(
        """
        INSERT INTO distrito_cobertura (nombre, geometria) VALUES
            ('San Juan de Lurigancho', ST_MakeEnvelope(-77.025, -12.050, -76.920, -11.905, 4326)),
            ('El Agustino',            ST_MakeEnvelope(-77.005, -12.068, -76.958, -12.028, 4326)),
            ('Santa Anita',            ST_MakeEnvelope(-76.980, -12.085, -76.925, -12.038, 4326)),
            ('Ate',                    ST_MakeEnvelope(-76.960, -12.110, -76.820, -12.000, 4326))
        """
    )
    op.execute(
        """
        CREATE TABLE job_optimizacion (
            id_job          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            estado          VARCHAR(20) NOT NULL DEFAULT 'ENCOLADO'
                            CHECK (estado IN ('ENCOLADO', 'EN_PROCESO', 'COMPLETADO', 'FALLIDO')),
            id_usuario      UUID REFERENCES usuario(id_usuario),
            fecha           DATE NOT NULL,
            mensaje         TEXT,
            resultado       JSONB,
            creado_en       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            actualizado_en  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    op.execute("CREATE INDEX idx_job_estado ON job_optimizacion(estado)")
    op.execute(
        """
        ALTER TABLE ruta
            ADD COLUMN minutos_conduccion DECIMAL(10,2),
            ADD COLUMN id_job UUID REFERENCES job_optimizacion(id_job)
        """
    )
    op.execute(
        """
        CREATE TABLE descanso_ruta (
            id_descanso            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            id_ruta                UUID NOT NULL REFERENCES ruta(id_ruta) ON DELETE CASCADE,
            despues_de_secuencia   INT NOT NULL CHECK (despues_de_secuencia >= 0),
            duracion_min           INT NOT NULL CHECK (duracion_min >= 60),
            motivo                 VARCHAR(80) NOT NULL DEFAULT 'LEY_30224'
        )
        """
    )
    op.execute("CREATE INDEX idx_descanso_ruta ON descanso_ruta(id_ruta)")
    op.execute(
        """
        INSERT INTO configuracion_sistema (clave, valor, unidad, descripcion) VALUES
            ('velocidad_urbana_km_h', '25', 'km/h',
             'Velocidad media de reparto en Lima Este para la heurística (US-010)'),
            ('factor_congestion', '1.00', 'adimensional',
             'Multiplicador de tiempo de viaje por overlay de congestión (US-010)')
        ON CONFLICT (clave) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM configuracion_sistema
        WHERE clave IN ('velocidad_urbana_km_h', 'factor_congestion')
        """
    )
    op.execute("DROP TABLE IF EXISTS descanso_ruta")
    op.execute("ALTER TABLE ruta DROP COLUMN IF EXISTS id_job")
    op.execute("ALTER TABLE ruta DROP COLUMN IF EXISTS minutos_conduccion")
    op.execute("DROP TABLE IF EXISTS job_optimizacion")
    op.execute("DROP TABLE IF EXISTS distrito_cobertura")
    op.execute("ALTER TABLE pedido DROP COLUMN IF EXISTS georreferencia_aproximada")
