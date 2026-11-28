"""Parámetros de compensación anual, ROI de GNV y créditos de carbono.

Revision ID: 009_anual_gnv_creditos
Revises: 008_valores_referenciales
Create Date: 2026-11-28

Carga en configuracion_sistema los parámetros de RF-10/RES-02 (escenario
pesimista y meta a 3 años), RES-01 (ROI de convertir a GNV) y RF-06 (créditos
de carbono). La tabla no tiene estado PENDIENTE: un dato sin fila (o con un
valor que no es un número > 0) se trata como pendiente. El upgrade es
idempotente (ON CONFLICT DO UPDATE); el downgrade borra estas claves.

Fuentes (consulta del 27-28/11/2026, hora de Lima):
- factor_captura_arbol_pesimista_kg = 15
  Tesis UPN 2024 (Heredia y Pablo), arbolado de Los Olivos con i-Tree Eco:
  ≈15,1 kg por árbol y año (47,46 t sobre 3 147 árboles). La tesis no deja
  claro si el valor es de C o de CO2; se usa como escenario pesimista.
  Ver /workspace/entregas-datos-faltantes/fuentes.md.
- precio_gnv_m3_soles = 12.50 y costo_conversion_gnv_vehiculo_soles = 5000
  Consigna del proyecto, RES-01: «GNV ... S/ 12.50 por metro cúbico ...
  conversión de vehículos (costo de S/ 5,000 por vehículo). Evaluar el ROI de
  migrar a GNV en un plazo de 3 años». Se usan tal cual vienen en la consigna.
- gnv_precio_mercado_m3_soles = 1.68
  Referencia de mercado, no de la consigna: promedio en Lima de S/ 1,68 por m³
  el 21/11/2026 según El Comercio con datos de Osinergmin (Facilito); el
  rango de marzo 2026 fue S/ 1,51 a S/ 2,19. Solo sirve para comparar.
  https://www.facilito.gob.pe/facilito/actions/PreciosGNVAction.do
- diesel_mmbtu_galon = 0.138 y diesel_co2_kg_mmbtu = 73.96
  US EPA, GHG Emission Factors Hub 2025 (15/01/2025), Tabla 1, Distillate
  Fuel Oil No. 2: 0.138 mmBtu/gal (poder calorífico superior) y 73.96 kg
  CO2/mmBtu (10.21 kg CO2/gal).
  https://www.epa.gov/climateleadership/ghg-emission-factors-hub
- gnv_mmbtu_scf = 0.001026 y gnv_co2_kg_mmbtu = 53.06
  Misma tabla, Natural Gas: 0.001026 mmBtu por pie cúbico estándar (scf) y
  53.06 kg CO2/mmBtu. El metro cúbico se convierte con 1 m³ = 35.3147 ft³.
  Son factores de EE. UU. con poder calorífico superior; se usan por falta de
  un factor oficial peruano publicado por Osinergmin o el MINEM.
- precio_credito_carbono_usd_t = 20.44
  Ecosystem Marketplace, State of the Voluntary Carbon Market 2025: precio
  medio de créditos de forestación y reforestación (ARR) en US$ por t CO2e.
- tipo_cambio_usd_pen = 3.478
  BCRP, serie PD04638PD (interbancario venta) del 26/11/2026.
"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "009_anual_gnv_creditos"
down_revision: str | None = "008_valores_referenciales"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

FILAS = (
    (
        "factor_captura_arbol_pesimista_kg",
        "15",
        "kg/año",
        "Escenario pesimista: tesis UPN 2024 (Heredia y Pablo), Los Olivos, i-Tree Eco, "
        "~15,1 kg/árbol/año. No aclara si es C o CO2.",
    ),
    (
        "precio_gnv_m3_soles",
        "12.50",
        "S/ / m³",
        "Consigna RES-01: GNV a S/ 12.50 por metro cúbico. Muy por encima del mercado "
        "(ver gnv_precio_mercado_m3_soles).",
    ),
    (
        "costo_conversion_gnv_vehiculo_soles",
        "5000",
        "S/ / vehículo",
        "Consigna RES-01: conversión a GNV de S/ 5,000 por vehículo.",
    ),
    (
        "gnv_precio_mercado_m3_soles",
        "1.68",
        "S/ / m³",
        "Referencia de mercado: promedio Lima 21/11/2026 (El Comercio, datos Osinergmin "
        "Facilito). No es de la consigna.",
    ),
    (
        "diesel_mmbtu_galon",
        "0.138",
        "mmBtu/gal",
        "US EPA GHG Emission Factors Hub 2025, Tabla 1: Distillate Fuel Oil No. 2, "
        "poder calorífico superior.",
    ),
    (
        "diesel_co2_kg_mmbtu",
        "73.96",
        "kg CO2/mmBtu",
        "US EPA GHG Emission Factors Hub 2025, Tabla 1: Distillate Fuel Oil No. 2 "
        "(10.21 kg CO2/gal).",
    ),
    (
        "gnv_mmbtu_scf",
        "0.001026",
        "mmBtu/scf",
        "US EPA GHG Emission Factors Hub 2025, Tabla 1: Natural Gas, poder calorífico "
        "superior por pie cúbico estándar. 1 m³ = 35.3147 ft³.",
    ),
    (
        "gnv_co2_kg_mmbtu",
        "53.06",
        "kg CO2/mmBtu",
        "US EPA GHG Emission Factors Hub 2025, Tabla 1: Natural Gas. Factor de EE. UU.; "
        "no hay factor oficial peruano publicado.",
    ),
    (
        "precio_credito_carbono_usd_t",
        "20.44",
        "US$ / t CO2e",
        "Ecosystem Marketplace, State of the Voluntary Carbon Market 2025: precio medio "
        "de créditos ARR (forestación y reforestación).",
    ),
    (
        "tipo_cambio_usd_pen",
        "3.478",
        "S/ por US$",
        "BCRP PD04638PD, interbancario venta, 26/11/2026.",
    ),
)


def upgrade() -> None:
    for clave, valor, unidad, descripcion in FILAS:
        op.execute(
            sa_text(
                """
                INSERT INTO configuracion_sistema (clave, valor, unidad, descripcion)
                VALUES (:clave, :valor, :unidad, :descripcion)
                ON CONFLICT (clave) DO UPDATE SET
                    valor = EXCLUDED.valor,
                    unidad = EXCLUDED.unidad,
                    descripcion = EXCLUDED.descripcion,
                    actualizado_en = CURRENT_TIMESTAMP
                """
            ).bindparams(clave=clave, valor=valor, unidad=unidad, descripcion=descripcion)
        )


def downgrade() -> None:
    claves = ", ".join(f"'{fila[0]}'" for fila in FILAS)
    op.execute(f"DELETE FROM configuracion_sistema WHERE clave IN ({claves})")
