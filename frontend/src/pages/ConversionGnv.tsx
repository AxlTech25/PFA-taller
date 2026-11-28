import { TablaDesplazable } from "../avisos";
import { numero, porcentaje, soles } from "../numeros";
import type { ConversionGnv as Gnv, EscenarioGnv } from "../types";

function recuperacion(gnv: Gnv, escenario: EscenarioGnv): string {
  if (gnv.inversion_soles == null || escenario.ahorro_anual_soles == null) return "Pendiente";
  if (gnv.inversion_soles === 0) return "Sin inversión";
  if (escenario.recuperacion_meses == null) return "No se recupera";
  return `${numero(escenario.recuperacion_meses, 1)} meses`;
}

export function ConversionGnv({ gnv }: Readonly<{ gnv: Gnv }>) {
  if (!gnv.calculable) {
    return <output className="aviso">{gnv.mensaje}</output>;
  }
  return (
    <div className="conversion-gnv">
      <h3 id="titulo-gnv">Conversión de la flota a GNV (ROI a {gnv.anios_roi} años)</h3>
      {gnv.aviso_proyeccion ? <output className="aviso">{gnv.aviso_proyeccion}</output> : null}
      <dl className="metricas" aria-labelledby="titulo-gnv">
        <div className="panel metrica">
          <dt>Vehículos a convertir</dt>
          <dd>{gnv.vehiculos}</dd>
        </div>
        <div className="panel metrica">
          <dt>Inversión</dt>
          <dd>{soles(gnv.inversion_soles)}</dd>
        </div>
        <div className="panel metrica">
          <dt>Equivalencia diésel-GNV</dt>
          <dd>
            {gnv.equivalencia_m3_por_galon == null
              ? "Pendiente"
              : `${numero(gnv.equivalencia_m3_por_galon, 2)} m³ por galón`}
          </dd>
        </div>
        <div className="panel metrica">
          <dt>CO₂ evitado al año</dt>
          <dd>
            {gnv.co2_evitado_anual_kg == null
              ? "Pendiente"
              : `${numero(gnv.co2_evitado_anual_kg, 1)} kg (${porcentaje(gnv.reduccion_co2_pct)})`}
          </dd>
        </div>
      </dl>
      <TablaDesplazable etiqueta="Ahorro, recuperación y ROI a 3 años de convertir a GNV">
        <table>
          <caption>Ahorro, recuperación y ROI a 3 años de convertir a GNV</caption>
          <thead>
            <tr>
              <th scope="col">Escenario de precio</th>
              <th scope="col">Precio del GNV</th>
              <th scope="col">Ahorro anual</th>
              <th scope="col">Recuperación</th>
              <th scope="col">ROI a 3 años</th>
            </tr>
          </thead>
          <tbody>
            {gnv.escenarios.map((escenario) => (
              <tr key={escenario.clave_precio}>
                <th scope="row">{escenario.nombre}</th>
                <td>
                  {escenario.precio_gnv_m3 == null
                    ? "Pendiente"
                    : `S/ ${numero(escenario.precio_gnv_m3, 2)} por m³`}
                </td>
                <td>{soles(escenario.ahorro_anual_soles)}</td>
                <td>
                  {recuperacion(gnv, escenario)}
                </td>
                <td>{porcentaje(escenario.roi_3_anios_pct)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </TablaDesplazable>
      {gnv.notas.map((nota) => (
        <p key={nota} className="ayuda">
          {nota}
        </p>
      ))}
      <p className="ayuda">
        Equivalencia y factores de emisión: US EPA, GHG Emission Factors Hub 2025 (factores de
        EE. UU., poder calorífico superior). Conversión de S/ 5,000 por vehículo y GNV a S/ 12.50
        por m³: consigna del proyecto. Precio de mercado: Osinergmin Facilito, promedio de Lima al
        21/11/2026. Supone el mismo rendimiento del motor con ambos combustibles.
      </p>
    </div>
  );
}
