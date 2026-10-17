"""Jornada máxima y descansos (US-007, Ley N.º 30224, RN-007 y RN-008)."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

JORNADA_MAX_MIN = 8 * 60
CONTINUO_MAX_MIN = 4 * 60
DESCANSO_MIN = 60

MENSAJE_JORNADA = (
    "Incumplimiento de la Ley N.º 30224: la conducción asignada supera "
    "las 8 horas de jornada máxima."
)


@dataclass
class Descanso:
    despues_de_secuencia: int
    duracion_min: int = DESCANSO_MIN


@dataclass
class EstadoJornada:
    minutos_conduccion: float = 0
    continuo: float = 0
    secuencia: int = 0
    descansos: list[Descanso] = field(default_factory=list)

    def puede_conducir(self, minutos: float) -> bool:
        return self.minutos_conduccion + minutos <= JORNADA_MAX_MIN + 1e-6

    def conducir(self, reloj: datetime, minutos: float) -> datetime:
        if minutos < 0:
            raise ValueError("Los minutos de conducción no pueden ser negativos")
        if not self.puede_conducir(minutos):
            raise ValueError(MENSAJE_JORNADA)
        restante = minutos
        while restante > 1e-6:
            espacio = CONTINUO_MAX_MIN - self.continuo
            if restante > espacio + 1e-6:
                if espacio > 1e-6:
                    reloj += timedelta(minutes=espacio)
                    self.minutos_conduccion += espacio
                    self.continuo = float(CONTINUO_MAX_MIN)
                    restante -= espacio
                self.descansos.append(Descanso(self.secuencia))
                reloj += timedelta(minutes=DESCANSO_MIN)
                self.continuo = 0
            else:
                reloj += timedelta(minutes=restante)
                self.minutos_conduccion += restante
                self.continuo += restante
                restante = 0
        if self.continuo >= CONTINUO_MAX_MIN - 1e-6:
            self.descansos.append(Descanso(self.secuencia))
            reloj += timedelta(minutes=DESCANSO_MIN)
            self.continuo = 0
        return reloj

    def esperar(self, reloj: datetime, minutos: float) -> datetime:
        if minutos >= DESCANSO_MIN:
            self.continuo = 0
        return reloj + timedelta(minutes=max(minutos, 0))

    def proyectar(self, reloj: datetime, minutos: float) -> tuple[datetime, "EstadoJornada"]:
        copia = EstadoJornada(
            minutos_conduccion=self.minutos_conduccion,
            continuo=self.continuo,
            secuencia=self.secuencia,
            descansos=list(self.descansos),
        )
        return copia.conducir(reloj, minutos), copia

    def adoptar(self, otro: "EstadoJornada") -> None:
        self.minutos_conduccion = otro.minutos_conduccion
        self.continuo = otro.continuo
        self.secuencia = otro.secuencia
        self.descansos = list(otro.descansos)

    def registrar_parada(self) -> None:
        self.secuencia += 1


def descansos_requeridos(minutos_conduccion: float) -> int:
    if minutos_conduccion + 1e-6 < CONTINUO_MAX_MIN:
        return 0
    return int(minutos_conduccion // CONTINUO_MAX_MIN)
