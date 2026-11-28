"""Valores referenciales ratificados para compensación y ciclo de vida.

Revision ID: 008_valores_referenciales
Revises: 007_confirmacion_entrega
Create Date: 2026-11-27

Carga en configuracion_sistema los valores investigados el 27/11/2026
(ver /workspace/entregas-datos-faltantes/fuentes.md). La tabla no tiene un
estado PENDIENTE: un dato no ratificado simplemente no tiene fila (o su
valor no es un número > 0). El downgrade borra estas claves y el sistema
vuelve a tratarlos como pendientes.

Fuentes (consulta del 27/11/2026, hora de Lima):
- factor_captura_arbol_kg = 60
  US EPA, Greenhouse Gas Equivalencies Calculator (Calculations and References),
  página actualizada el 04/08/2026:
  «36.4 lbs C/tree/year × (44/12) × 1 metric ton/2,204.6 lbs = 0.060 metric
  ton CO2 per urban tree planted per year». Árbol urbano de crecimiento
  medio, promedio de los primeros 10 años, ya descuenta supervivencia.
  La EPA advierte que es aproximado y no sirve para inventarios formales.
  https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator-calculations-and-references
- costo_compensacion_arbol_soles = 94
  SERPAR, programa «Raíces de Vida» (2021): S/ 94 por plantación y 5 años
  de mantenimiento (Un Árbol para Siempre cuesta S/ 188). No se halló
  una tarifa pública 2025-2026.
  https://www.serpar.gob.pe/noticias/raices-de-vida-planta-un-arbol-en-memoria-de-un-ser-querido-y-otros-motivos-especiales/
- depreciacion_anual_vehiculo_soles = 23988
  20 % anual sobre S/ 119,941. Precio de lista Toyota Hilux 4x2 D/C 2GD
  M/T SR US$ 34,490 (Grupo Pana, consultado el 27/11/2026) × tipo de cambio
  interbancario venta BCRP PD04638PD del 26/11/2026 (S/ 3,478).
  https://grupopana.com.pe/autos-nuevos/hilux
  https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04638PD/json/2026-11-01/2026-11-27/esp
- seguro_anual_vehiculo_soles = 8072
  6,73 % anual de S/ 119,941. Tarifario de crédito vehicular Interbank
  (seguro Rímac), categoría IV camionetas pick-up alto riesgo, Lima,
  actualizado a diciembre 2021. Es tarifa de uso particular; no hay una
  tarifa pública de uso comercial o de flota.
- soat_anual_vehiculo_soles = 150
  Tarifario SOAT La Positiva (PDF del corredor Confianza, agosto 2026):
  camioneta pick-up N1, uso carga, columna Lima, S/ 150 (referencial).
- sueldo_anual_conductor_soles = 18000
  S/ 1,500 al mes × 12, consigna del proyecto (no es una planilla real).
"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy import text as sa_text

revision: str = "008_valores_referenciales"
down_revision: str | None = "007_confirmacion_entrega"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CLAVES = (
    "factor_captura_arbol_kg",
    "costo_compensacion_arbol_soles",
    "depreciacion_anual_vehiculo_soles",
    "seguro_anual_vehiculo_soles",
    "soat_anual_vehiculo_soles",
    "sueldo_anual_conductor_soles",
)


def upgrade() -> None:
    filas = (
        (
            "factor_captura_arbol_kg",
            "60",
            "kg/año",
            "US EPA GHG Equivalencies: 0.060 t CO2/árbol urbano/año "
            "(36.4 lbs C × 44/12). Aprox., no para inventarios. Actualizado 04/08/2026.",
        ),
        (
            "costo_compensacion_arbol_soles",
            "94",
            "S/ / árbol",
            "SERPAR Raíces de Vida (2021): S/ 94 plantación + 5 años de mantenimiento. "
            "No se halló tarifa pública 2025-2026.",
        ),
        (
            "depreciacion_anual_vehiculo_soles",
            "23988",
            "S/ / año",
            "20% anual sobre S/ 119,941 (Hilux 4x2, US$ 34,490 × TC BCRP 3,478 "
            "al 26/11/2026). Lista Grupo Pana 27/11/2026.",
        ),
        (
            "seguro_anual_vehiculo_soles",
            "8072",
            "S/ / año",
            "6,73% anual de S/ 119,941. Interbank/Rímac pick-up Lima, tarifario "
            "dic. 2021 (uso particular; no hay tarifa pública de flota).",
        ),
        (
            "soat_anual_vehiculo_soles",
            "150",
            "S/ / año",
            "SOAT La Positiva, camioneta pick-up N1 uso carga, Lima, "
            "tarifario ago. 2026 (referencial).",
        ),
        (
            "sueldo_anual_conductor_soles",
            "18000",
            "S/ / año",
            "S/ 1,500 mensuales × 12 (consigna del proyecto). "
            "Referencial, no una planilla real.",
        ),
    )
    for clave, valor, unidad, descripcion in filas:
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
    op.execute(
        """
        DELETE FROM configuracion_sistema
        WHERE clave IN (
            'factor_captura_arbol_kg',
            'costo_compensacion_arbol_soles',
            'depreciacion_anual_vehiculo_soles',
            'seguro_anual_vehiculo_soles',
            'soat_anual_vehiculo_soles',
            'sueldo_anual_conductor_soles'
        )
        """
    )
