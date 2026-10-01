import { useEffect } from "react";

export function ModoConductorPage() {
  useEffect(() => {
    document.title = "Modo conductor · EcoLogística Lima";
  }, []);

  return (
    <>
      <header>
        <h1>Modo conductor</h1>
        <p className="ayuda">
          Este perfil consulta la ruta del día. La secuencia de paradas llega en un sprint
          posterior. Mientras tanto puede revisar la flota, sin editarla ni administrar usuarios.
        </p>
      </header>
      <section className="panel">
        <h2>Su jornada</h2>
        <p>No tiene una ruta confirmada para hoy.</p>
      </section>
    </>
  );
}
