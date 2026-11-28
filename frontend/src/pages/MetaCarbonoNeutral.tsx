import { TablaDesplazable } from "../avisos";
import { numero, porcentaje, soles } from "../numeros";
import type { PlanAnual } from "../types";

function entero(valor: number | null): string {
  return valor == null ? "Pendiente" : numero(valor, 0);
}

export function MetaCarbonoNeutral({ anual }: Readonly<{ anual: PlanAnual }>) {
  if (!anual.calculable) {
    return <output className="aviso">{anual.mensaje}</output>;
  }
  const avance = anual.avance;
  const conPlan = anual.escenarios.filter((escenario) => escenario.plan.length > 0);
  return (
    <div className="compensacion-anual">
      <h3 id="titulo-meta-anual">Compensación anual y meta de carbono neutral a {anual.anios_meta} años</h3>
      {anual.aviso ? <output className="aviso">{anual.aviso}</output> : null}
      <dl className="metricas" aria-labelledby="titulo-meta-anual">
        <div className="panel metrica">
          <dt>CO₂ anual proyectado</dt>
          <dd>{numero(anual.co2_anual_kg, 1)} kg</dd>
        </div>
        <div className="panel metrica">
          <dt>Avance hacia la meta</dt>
          <dd>
            {porcentaje(avance?.avance_pct)} ({numero(avance?.arboles_registrados ?? 0, 0)} árboles
            registrados)
          </dd>
        </div>
      </dl>
      {avance?.nota ? <p className="ayuda">{avance.nota}</p> : null}
      <TablaDesplazable etiqueta="Árboles y costo para compensar las emisiones anuales">
        <table>
          <caption>Árboles y costo para compensar las emisiones anuales</caption>
          <thead>
            <tr>
              <th scope="col">Escenario</th>
              <th scope="col">Captura por árbol</th>
              <th scope="col">Costo unitario</th>
              <th scope="col">Árboles al año</th>
              <th scope="col">Costo total</th>
              <th scope="col">Árboles por año</th>
            </tr>
          </thead>
          <tbody>
            {anual.escenarios.map((escenario) => (
              <tr key={escenario.clave_factor}>
                <th scope="row">{escenario.nombre}</th>
                <td>
                  {escenario.factor_kg_arbol_anio == null
                    ? "Pendiente"
                    : `${numero(escenario.factor_kg_arbol_anio, 0)} kg/árbol/año`}
                </td>
                <td>{soles(escenario.costo_por_arbol_soles)}</td>
                <td>{entero(escenario.arboles_anuales)}</td>
                <td>{soles(escenario.costo_total_soles)}</td>
                <td>{entero(escenario.arboles_por_anio)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </TablaDesplazable>
      {conPlan.map((escenario) => (
        <TablaDesplazable
          key={escenario.clave_factor}
          etiqueta={`Plan de plantación a ${anual.anios_meta} años, escenario ${escenario.nombre}`}
        >
          <table>
            <caption>
              Plan de plantación a {anual.anios_meta} años, escenario {escenario.nombre}
            </caption>
            <thead>
              <tr>
                <th scope="col">Año</th>
                <th scope="col">Árboles a plantar</th>
                <th scope="col">Árboles acumulados</th>
                <th scope="col">Cobertura del CO₂ anual</th>
                <th scope="col">Costo</th>
              </tr>
            </thead>
            <tbody>
              {escenario.plan.map((fila) => (
                <tr key={fila.anio}>
                  <th scope="row">Año {fila.anio}</th>
                  <td>{numero(fila.arboles_a_plantar, 0)}</td>
                  <td>{numero(fila.arboles_acumulados, 0)}</td>
                  <td>{porcentaje(fila.cobertura_pct)}</td>
                  <td>{soles(fila.costo_soles)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TablaDesplazable>
      ))}
      <p className="ayuda">
        Árboles = CO₂ anual ÷ factor de captura, redondeado hacia arriba. Factores: EPA 60 kg
        (árbol urbano, promedio de 10 años) y escenario pesimista de 15 kg (tesis UPN 2024, Los
        Olivos). Supone que las emisiones no cambian y que cada árbol captura el factor desde el
        año en que se planta.
      </p>
    </div>
  );
}
