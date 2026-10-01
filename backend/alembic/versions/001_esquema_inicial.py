"""Esquema inicial PostgreSQL + PostGIS (documento 11, ENB-003).

Revision ID: 001_esquema_inicial
Revises:
Create Date: 2026-09-30
"""

from collections.abc import Sequence

from alembic import op

revision: str = "001_esquema_inicial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SENTENCIAS: tuple[str, ...] = (
    "CREATE EXTENSION IF NOT EXISTS postgis",
    'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"',
    """
    CREATE TABLE usuario (
        id_usuario          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        email               VARCHAR(255) NOT NULL UNIQUE,
        password_hash       VARCHAR(255) NOT NULL,
        rol                 VARCHAR(30)  NOT NULL CHECK (rol IN ('ADMIN', 'GERENTE', 'OPERADOR', 'CONDUCTOR', 'AUDITOR')),
        estado              VARCHAR(20)  NOT NULL DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'INACTIVO', 'BLOQUEADO')),
        intentos_fallidos   INT          NOT NULL DEFAULT 0,
        bloqueado_hasta     TIMESTAMPTZ,
        creado_en           TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
        actualizado_en      TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX idx_usuario_email ON usuario(email)",
    "CREATE INDEX idx_usuario_rol ON usuario(rol)",
    """
    CREATE TABLE cliente (
        id_cliente            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        nombre                VARCHAR(150) NOT NULL,
        telefono              VARCHAR(20),
        email                 VARCHAR(255),
        consentimiento_datos  BOOLEAN      NOT NULL DEFAULT FALSE,
        creado_en             TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE preferencia_cliente (
        id_preferencia        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        id_cliente            UUID         NOT NULL UNIQUE REFERENCES cliente(id_cliente) ON DELETE CASCADE,
        hora_inicio_preferida TIME,
        hora_fin_preferida    TIME,
        punto_referencia      VARCHAR(255),
        restricciones_acceso  TEXT,
        creado_en             TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT chk_horario_preferido CHECK (hora_inicio_preferida < hora_fin_preferida)
    )
    """,
    """
    CREATE TABLE vehiculo (
        id_vehiculo           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        placa                 VARCHAR(10)  NOT NULL UNIQUE,
        tipo                  VARCHAR(30)  NOT NULL CHECK (tipo IN ('CAMIONETA', 'FURGON', 'MOTO')),
        capacidad_kg          DECIMAL(10,2) NOT NULL CHECK (capacidad_kg > 0),
        capacidad_m3          DECIMAL(10,2) NOT NULL CHECK (capacidad_m3 > 0),
        consumo_km_l          DECIMAL(8,3)  NOT NULL CHECK (consumo_km_l > 0),
        factor_emision_co2    DECIMAL(8,4)  NOT NULL CHECK (factor_emision_co2 > 0),
        anio_fabricacion      INT          NOT NULL CHECK (anio_fabricacion >= 1990),
        estado                VARCHAR(20)  NOT NULL DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'MANTENIMIENTO', 'INACTIVO')),
        creado_en             TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX idx_vehiculo_placa ON vehiculo(placa)",
    "CREATE INDEX idx_vehiculo_estado ON vehiculo(estado)",
    """
    CREATE TABLE conductor (
        id_conductor          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        id_usuario            UUID         UNIQUE REFERENCES usuario(id_usuario),
        dni                   VARCHAR(15)  NOT NULL UNIQUE,
        nombre                VARCHAR(150) NOT NULL,
        licencia_categoria    VARCHAR(10)  NOT NULL,
        anios_experiencia     INT          NOT NULL DEFAULT 0 CHECK (anios_experiencia >= 0),
        disponibilidad_inicio TIME         NOT NULL,
        disponibilidad_fin    TIME         NOT NULL,
        lat_punto_partida     DECIMAL(10,7),
        lon_punto_partida     DECIMAL(10,7),
        estado                VARCHAR(20)  NOT NULL DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'INACTIVO', 'VACACIONES')),
        creado_en             TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT chk_disponibilidad CHECK (disponibilidad_inicio < disponibilidad_fin)
    )
    """,
    "CREATE INDEX idx_conductor_dni ON conductor(dni)",
    "CREATE INDEX idx_conductor_estado ON conductor(estado)",
    """
    CREATE TABLE pedido (
        id_pedido             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        id_cliente            UUID         NOT NULL REFERENCES cliente(id_cliente),
        direccion             VARCHAR(255),
        punto_referencia      VARCHAR(255),
        latitud               DECIMAL(10,7) NOT NULL,
        longitud              DECIMAL(10,7) NOT NULL,
        peso_kg               DECIMAL(10,2) NOT NULL CHECK (peso_kg > 0),
        volumen_m3            DECIMAL(10,3) NOT NULL CHECK (volumen_m3 > 0),
        ventana_inicio        TIMESTAMPTZ  NOT NULL,
        ventana_fin           TIMESTAMPTZ  NOT NULL,
        prioridad             VARCHAR(20)  NOT NULL DEFAULT 'ESTANDAR' CHECK (prioridad IN ('EXPRESS', 'ESTANDAR', 'ECONOMICO')),
        tipo_producto         VARCHAR(30)  NOT NULL CHECK (tipo_producto IN ('PERECEDERO', 'NO_PERECEDERO')),
        estado                VARCHAR(20)  NOT NULL DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'ASIGNADO', 'EN_TRANSITO', 'ENTREGADO', 'CANCELADO')),
        creado_en             TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT chk_ventana CHECK (ventana_inicio < ventana_fin)
    )
    """,
    "CREATE INDEX idx_pedido_estado ON pedido(estado)",
    "CREATE INDEX idx_pedido_cliente ON pedido(id_cliente)",
    "CREATE INDEX idx_pedido_ventana ON pedido(ventana_inicio, ventana_fin)",
    "CREATE INDEX idx_pedido_ubicacion ON pedido(latitud, longitud)",
    """
    CREATE TABLE ruta (
        id_ruta               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        fecha                 DATE         NOT NULL,
        estado                VARCHAR(20)  NOT NULL DEFAULT 'BORRADOR' CHECK (estado IN ('BORRADOR', 'CONFIRMADA', 'EN_EJECUCION', 'FINALIZADA', 'CANCELADA')),
        distancia_total_km    DECIMAL(10,2),
        tiempo_total_min      DECIMAL(10,2),
        combustible_estimado_l DECIMAL(10,2),
        co2_estimado_kg       DECIMAL(10,3),
        generada_en           TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX idx_ruta_fecha ON ruta(fecha)",
    "CREATE INDEX idx_ruta_estado ON ruta(estado)",
    """
    CREATE TABLE asignacion_ruta (
        id_asignacion         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        id_ruta               UUID NOT NULL UNIQUE REFERENCES ruta(id_ruta) ON DELETE CASCADE,
        id_vehiculo           UUID NOT NULL REFERENCES vehiculo(id_vehiculo),
        id_conductor          UUID NOT NULL REFERENCES conductor(id_conductor),
        asignada_en           TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX idx_asignacion_vehiculo ON asignacion_ruta(id_vehiculo)",
    "CREATE INDEX idx_asignacion_conductor ON asignacion_ruta(id_conductor)",
    """
    CREATE TABLE detalle_ruta (
        id_detalle            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        id_ruta               UUID NOT NULL REFERENCES ruta(id_ruta) ON DELETE CASCADE,
        id_pedido             UUID NOT NULL REFERENCES pedido(id_pedido),
        secuencia             INT  NOT NULL CHECK (secuencia > 0),
        eta                   TIMESTAMPTZ,
        estado_entrega        VARCHAR(20) DEFAULT 'PENDIENTE' CHECK (estado_entrega IN ('PENDIENTE', 'ENTREGADO', 'FALLIDO', 'REPROGRAMADO')),
        UNIQUE (id_ruta, id_pedido),
        UNIQUE (id_ruta, secuencia)
    )
    """,
    "CREATE INDEX idx_detalle_ruta_pedido ON detalle_ruta(id_pedido)",
    """
    CREATE TABLE zona_restriccion (
        id_zona               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        nombre                VARCHAR(150) NOT NULL,
        tipo                  VARCHAR(30)  NOT NULL CHECK (tipo IN ('RIESGO_SEGURIDAD', 'RESERVA_ECOLOGICA', 'RESTRICCION_HORARIA', 'CENTRO_HISTORICO', 'VIA_NO_PAVIMENTADA', 'BAJA_VISIBILIDAD')),
        geometria             GEOMETRY(Polygon, 4326) NOT NULL,
        severidad             VARCHAR(20)  NOT NULL DEFAULT 'MEDIA' CHECK (severidad IN ('BAJA', 'MEDIA', 'ALTA')),
        activo                BOOLEAN      NOT NULL DEFAULT TRUE
    )
    """,
    "CREATE INDEX idx_zona_geometria ON zona_restriccion USING GIST (geometria)",
    """
    CREATE TABLE emision_co2 (
        id_emision            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        id_ruta               UUID NOT NULL UNIQUE REFERENCES ruta(id_ruta) ON DELETE CASCADE,
        co2_emitido_kg        DECIMAL(12,3) NOT NULL,
        co2_ahorrado_kg       DECIMAL(12,3),
        equivalente_arboles   DECIMAL(10,2),
        calculado_en          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE reporte (
        id_reporte            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        periodo_inicio        DATE NOT NULL,
        periodo_fin           DATE NOT NULL,
        tipo                  VARCHAR(50) NOT NULL,
        ruta_archivo          VARCHAR(500),
        generado_en           TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        generado_por          UUID REFERENCES usuario(id_usuario)
    )
    """,
    """
    CREATE TABLE incidencia (
        id_incidencia         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        tipo                  VARCHAR(30)  NOT NULL CHECK (tipo IN ('NUEVO_PEDIDO', 'CANCELACION', 'ACCIDENTE_TRANSITO', 'AVERIA_VEHICULO', 'CONGESTION')),
        origen                VARCHAR(20)  NOT NULL DEFAULT 'MANUAL' CHECK (origen IN ('MANUAL', 'API_TRAFICO')),
        id_ruta               UUID REFERENCES ruta(id_ruta),
        id_vehiculo           UUID REFERENCES vehiculo(id_vehiculo),
        id_pedido             UUID REFERENCES pedido(id_pedido),
        descripcion           VARCHAR(255),
        latitud               DECIMAL(10,7),
        longitud              DECIMAL(10,7),
        estado                VARCHAR(20)  NOT NULL DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'REOPTIMIZADA', 'SIN_SOLUCION', 'DESCARTADA')),
        reportada_en          TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
        resuelta_en           TIMESTAMPTZ
    )
    """,
    "CREATE INDEX idx_incidencia_estado ON incidencia(estado)",
    "CREATE INDEX idx_incidencia_ruta ON incidencia(id_ruta)",
    """
    CREATE TABLE configuracion_sistema (
        clave                 VARCHAR(60) PRIMARY KEY,
        valor                 VARCHAR(255) NOT NULL,
        unidad                VARCHAR(30),
        descripcion           VARCHAR(255),
        actualizado_por       UUID REFERENCES usuario(id_usuario),
        actualizado_en        TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    INSERT INTO configuracion_sistema (clave, valor, unidad, descripcion) VALUES
      ('tiempo_max_optimizacion_s',   '45',    'segundos',   'Tope de cómputo de la generación inicial de rutas (RN-014)'),
      ('tiempo_max_reoptimizacion_s', '30',    'segundos',   'Tope de cómputo de la re-optimización dinámica (RN-014)'),
      ('precio_diesel_galon',         '17.50', 'S/ / galón', 'Precio de referencia del diésel en Lima al 2026 (RN-017)'),
      ('costo_mantenimiento_km',      '1.20',  'S/ / km',    'Costo promedio de mantenimiento por km recorrido (RN-017)')
    """,
    """
    CREATE TABLE log_auditoria (
        id_log                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        id_usuario            UUID REFERENCES usuario(id_usuario),
        accion                VARCHAR(100) NOT NULL,
        tabla_afectada        VARCHAR(50),
        registro_id           UUID,
        datos_anteriores      JSONB,
        datos_nuevos          JSONB,
        ip_origen             INET,
        creado_en             TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX idx_log_usuario ON log_auditoria(id_usuario)",
    "CREATE INDEX idx_log_fecha ON log_auditoria(creado_en)",
)

TABLAS = (
    "log_auditoria",
    "configuracion_sistema",
    "incidencia",
    "reporte",
    "emision_co2",
    "zona_restriccion",
    "detalle_ruta",
    "asignacion_ruta",
    "ruta",
    "pedido",
    "conductor",
    "vehiculo",
    "preferencia_cliente",
    "cliente",
    "usuario",
)


def upgrade() -> None:
    for sentencia in SENTENCIAS:
        op.execute(sentencia)


def downgrade() -> None:
    for tabla in TABLAS:
        op.execute(f"DROP TABLE IF EXISTS {tabla} CASCADE")
