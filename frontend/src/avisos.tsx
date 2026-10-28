import { useEffect, useRef, type ReactNode } from "react";

export function Alerta({ id, children }: Readonly<{ id: string; children: ReactNode }>) {
  const ref = useRef<HTMLAnchorElement>(null);

  useEffect(() => {
    ref.current?.focus();
  }, [children]);

  return (
    <p id={id} className="alerta" role="alert">
      <a ref={ref} href={`#${id}`}>
        {children}
      </a>
    </p>
  );
}

export function Exito({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <output className="exito" aria-atomic="true">
      {children}
    </output>
  );
}

export function TablaDesplazable({
  etiqueta,
  children,
}: Readonly<{ etiqueta: string; children: ReactNode }>) {
  const zona = useRef<HTMLDivElement>(null);
  const izquierda = "Desplazar la tabla a la izquierda";
  const derecha = "Desplazar la tabla a la derecha";

  function desplazar(delta: number) {
    const nodo = zona.current;
    if (!nodo) return;
    nodo.scrollLeft += delta;
  }

  return (
    <section aria-label={etiqueta}>
      <div className="fila-acciones">
        <button
          type="button"
          className="secundario"
          aria-label={`${izquierda}. ${etiqueta}`}
          onClick={() => desplazar(-160)}
        >
          {izquierda}
        </button>
        <button
          type="button"
          className="secundario"
          aria-label={`${derecha}. ${etiqueta}`}
          onClick={() => desplazar(160)}
        >
          {derecha}
        </button>
      </div>
      <div ref={zona} className="tabla-contenedor">
        {children}
      </div>
    </section>
  );
}
