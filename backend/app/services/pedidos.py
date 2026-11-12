from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, load_only

from app.models.entities import Cliente, Pedido, Usuario
from app.optimizacion.cobertura import MENSAJE_FUERA_COBERTURA, distrito_en, distritos_en
from app.schemas.pedido import PedidoCreate
from app.services.auditoria import registrar
from app.services.integridad import mensaje_integridad
from app.services.paginacion import normalizar, paginar_entidades, paginar_filas
from app.services.sanitizacion import exigir_textos_seguros

_SIN_DISTRITO = object()

MENSAJE_CONSENTIMIENTO = (
    "El cliente no ha otorgado el consentimiento para el tratamiento de sus datos. "
    "Solicite el consentimiento explícito."
)


def _decimal(valor: float) -> Decimal:
    return Decimal(str(valor))


def _float(valor) -> float | None:
    if valor is None:
        return None
    return float(valor)


def listar_clientes(db: Session, actor: Usuario, page: int, limite: int) -> dict:
    consulta = (
        select(Cliente)
        .options(
            load_only(
                Cliente.id_cliente,
                Cliente.nombre,
                Cliente.telefono,
                Cliente.email,
                Cliente.consentimiento_datos,
            )
        )
        .order_by(Cliente.nombre)
    )
    pagina = paginar_entidades(db, consulta, page, limite)
    anonimo = actor.rol == "AUDITOR"
    pagina["items"] = [
        {
            "id_cliente": fila.id_cliente,
            "nombre": fila.nombre,
            "telefono": None if anonimo else fila.telefono,
            "email": None if anonimo else fila.email,
            "consentimiento_datos": fila.consentimiento_datos,
        }
        for fila in pagina["items"]
    ]
    return pagina


def _nombre_cliente(db: Session, id_cliente) -> str | None:
    cliente = db.get(Cliente, id_cliente)
    return cliente.nombre if cliente else None


def salida_pedido(
    db: Session,
    pedido: Pedido,
    rol: str,
    nombre_cliente: str | None = None,
    distrito: object = _SIN_DISTRITO,
) -> dict:
    anonimo = rol == "AUDITOR"
    if nombre_cliente is None:
        nombre_cliente = _nombre_cliente(db, pedido.id_cliente)
    if distrito is _SIN_DISTRITO:
        distrito = None
        if not anonimo:
            distrito = distrito_en(db, float(pedido.latitud), float(pedido.longitud))
    return {
        "id_pedido": pedido.id_pedido,
        "id_cliente": pedido.id_cliente,
        "nombre_cliente": nombre_cliente,
        "direccion": None if anonimo else pedido.direccion,
        "punto_referencia": None if anonimo else pedido.punto_referencia,
        "latitud": None if anonimo else _float(pedido.latitud),
        "longitud": None if anonimo else _float(pedido.longitud),
        "peso_kg": float(pedido.peso_kg),
        "volumen_m3": float(pedido.volumen_m3),
        "ventana_inicio": pedido.ventana_inicio,
        "ventana_fin": pedido.ventana_fin,
        "prioridad": pedido.prioridad,
        "tipo_producto": pedido.tipo_producto,
        "estado": pedido.estado,
        "georreferencia_aproximada": pedido.georreferencia_aproximada,
        "distrito": None if anonimo else distrito,
    }


def listar_pedidos(db: Session, actor: Usuario, page: int, limite: int) -> dict:
    if actor.rol == "CONDUCTOR":
        pagina, tamano = normalizar(page, limite)
        return {
            "items": [],
            "total": 0,
            "page": pagina,
            "page_size": tamano,
            "total_pages": 0,
        }
    consulta = (
        select(Pedido, Cliente.nombre)
        .join(Cliente, Cliente.id_cliente == Pedido.id_cliente)
        .options(
            load_only(
                Pedido.id_pedido,
                Pedido.id_cliente,
                Pedido.direccion,
                Pedido.punto_referencia,
                Pedido.latitud,
                Pedido.longitud,
                Pedido.peso_kg,
                Pedido.volumen_m3,
                Pedido.ventana_inicio,
                Pedido.ventana_fin,
                Pedido.prioridad,
                Pedido.tipo_producto,
                Pedido.estado,
                Pedido.georreferencia_aproximada,
                Pedido.creado_en,
            )
        )
        .order_by(Pedido.creado_en.desc(), Pedido.id_pedido)
    )
    filas, meta = paginar_filas(db, consulta, page, limite)
    anonimo = actor.rol == "AUDITOR"
    puntos = [
        (float(pedido.latitud), float(pedido.longitud))
        for pedido, _nombre in filas
        if not anonimo
    ]
    zonas = [] if anonimo else distritos_en(db, puntos)
    items = []
    for indice, (pedido, nombre) in enumerate(filas):
        zona = None if anonimo else zonas[indice]
        items.append(
            salida_pedido(db, pedido, actor.rol, nombre_cliente=nombre, distrito=zona)
        )
    meta["items"] = items
    return meta


def crear_pedido(db: Session, datos: PedidoCreate, actor: Usuario, ip: str | None) -> Pedido:
    exigir_textos_seguros(
        db,
        id_usuario=actor.id_usuario,
        ip=ip,
        tabla="pedido",
        campos=[
            (datos.direccion, "direccion"),
            (datos.punto_referencia, "punto_referencia"),
        ],
    )
    cliente = db.get(Cliente, datos.id_cliente)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    if not cliente.consentimiento_datos:
        registrar(
            db,
            id_usuario=actor.id_usuario,
            accion="pedido_sin_consentimiento",
            tabla="pedido",
            registro_id=None,
            ip=ip,
            nuevos={"id_cliente": str(cliente.id_cliente)},
        )
        db.commit()
        raise HTTPException(status_code=422, detail=MENSAJE_CONSENTIMIENTO)

    distrito = distrito_en(db, datos.latitud, datos.longitud)
    if distrito is None:
        registrar(
            db,
            id_usuario=actor.id_usuario,
            accion="pedido_fuera_cobertura",
            tabla="pedido",
            registro_id=None,
            ip=ip,
            nuevos={"latitud": datos.latitud, "longitud": datos.longitud},
        )
        db.commit()
        raise HTTPException(status_code=422, detail=MENSAJE_FUERA_COBERTURA)

    aproximada = datos.punto_referencia is not None
    pedido = Pedido(
        id_cliente=datos.id_cliente,
        direccion=datos.direccion,
        punto_referencia=datos.punto_referencia,
        latitud=_decimal(datos.latitud),
        longitud=_decimal(datos.longitud),
        peso_kg=_decimal(datos.peso_kg),
        volumen_m3=_decimal(datos.volumen_m3),
        ventana_inicio=datos.ventana_inicio,
        ventana_fin=datos.ventana_fin,
        prioridad=datos.prioridad,
        tipo_producto=datos.tipo_producto,
        estado="PENDIENTE",
        georreferencia_aproximada=aproximada,
    )
    db.add(pedido)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        mensaje = mensaje_integridad(exc) or "No se pudo registrar el pedido"
        raise HTTPException(status_code=409, detail=mensaje) from exc
    db.refresh(pedido)
    registrar(
        db,
        id_usuario=actor.id_usuario,
        accion="crear_pedido",
        tabla="pedido",
        registro_id=pedido.id_pedido,
        ip=ip,
        nuevos={
            "id_cliente": str(pedido.id_cliente),
            "estado": pedido.estado,
            "peso_kg": float(pedido.peso_kg),
            "distrito": distrito,
            "georreferencia_aproximada": pedido.georreferencia_aproximada,
        },
    )
    db.commit()
    return pedido
