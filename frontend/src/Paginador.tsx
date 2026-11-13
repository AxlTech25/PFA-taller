type Props = Readonly<{
  page: number;
  totalPages: number;
  onPage: (page: number) => void;
}>;

export function Paginador({ page, totalPages, onPage }: Props) {
  if (totalPages <= 1) return null;
  return (
    <nav className="paginador" aria-label="Paginación">
      <button
        type="button"
        className="secundario"
        onClick={() => onPage(page - 1)}
        disabled={page <= 1}
      >
        Anterior
      </button>
      <span>
        Página {page} de {totalPages}
      </span>
      <button
        type="button"
        className="secundario"
        onClick={() => onPage(page + 1)}
        disabled={page >= totalPages}
      >
        Siguiente
      </button>
    </nav>
  );
}
