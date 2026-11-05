"""Pydantic v2 schemas for the citizen-service API contracts.

Input models reject unknown fields (``extra="forbid"``) so a typo in a payload
fails fast instead of being silently ignored. Output models read from ORM
objects (``from_attributes=True``).
"""

from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    computed_field,
    model_validator,
)

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
SHA256_REGEX = r"^[a-f0-9]{64}$"
TELEFONO_REGEX = r"^[0-9+() -]{7,20}$"
RADICADO_PQRSD_REGEX = r"^PQRSD-[0-9]{4}-[0-9]{6}$"

Email = Annotated[str, StringConstraints(pattern=EMAIL_REGEX, max_length=254)]
Telefono = Annotated[str, StringConstraints(pattern=TELEFONO_REGEX)]
Sha256 = Annotated[str, StringConstraints(pattern=SHA256_REGEX, min_length=64, max_length=64)]


class EstadoPQRSD(str, Enum):
    RECIBIDA = "recibida"
    EN_TRAMITE = "en_tramite"
    RESPONDIDA = "respondida"
    VENCIDA = "vencida"
    CERRADA = "cerrada"
    ARCHIVADA = "archivada"


SUCCESSOR_STATES: dict[EstadoPQRSD, frozenset[EstadoPQRSD]] = {
    EstadoPQRSD.RECIBIDA: frozenset({EstadoPQRSD.EN_TRAMITE, EstadoPQRSD.VENCIDA, EstadoPQRSD.ARCHIVADA}),
    EstadoPQRSD.EN_TRAMITE: frozenset(
        {EstadoPQRSD.RESPONDIDA, EstadoPQRSD.VENCIDA, EstadoPQRSD.ARCHIVADA}
    ),
    EstadoPQRSD.RESPONDIDA: frozenset({EstadoPQRSD.CERRADA}),
    EstadoPQRSD.VENCIDA: frozenset({EstadoPQRSD.RESPONDIDA, EstadoPQRSD.CERRADA, EstadoPQRSD.ARCHIVADA}),
    EstadoPQRSD.CERRADA: frozenset(),
    EstadoPQRSD.ARCHIVADA: frozenset(),
}


class TipoCorrespondencia(str, Enum):
    RECIBIDA = "recibida"
    DESPACHADA = "despachada"


class _OrmModel(BaseModel):
    """Base for response models built from ORM instances."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class _InputModel(BaseModel):
    """Base for request models: rejects unknown fields."""

    model_config = ConfigDict(from_attributes=True, extra="forbid", str_strip_whitespace=True)


# ---------------------------------------------------------------------------
# Catalogs
# ---------------------------------------------------------------------------


class CanalRead(_OrmModel):
    id: int
    codigo: str
    nombre: str
    descripcion: str | None = None
    es_presencial: bool


class TipoPeticionRead(_OrmModel):
    id: int
    codigo: str
    nombre: str
    plazo_dias_habiles: int = Field(ge=1, le=60)
    base_legal: str


class DependenciaRead(_OrmModel):
    id: int
    codigo: str
    nombre: str
    activa: bool


class CategoriaDiferencialRead(_OrmModel):
    id: int
    codigo: str
    nombre: str
    descripcion: str | None = None


class GlosarioTerminoRead(_OrmModel):
    id: int
    termino_tecnico: str
    termino_ciudadano: str
    ejemplo: str | None = None


class TramiteRead(_OrmModel):
    id: int
    codigo: str
    nombre: str
    descripcion: str | None = None
    dependencia_id: int
    canal_id: int | None = None
    activo: bool


class HorarioAtencionRead(_OrmModel):
    dia_semana: int = Field(ge=1, le=7, description="ISO-8601: 1 = Monday, 7 = Sunday")
    hora_inicio: time
    hora_fin: time


class SedeRead(_OrmModel):
    id: int
    dependencia_id: int
    nombre: str
    direccion: str
    ciudad: str
    telefono: str | None = None
    activa: bool
    horarios: list[HorarioAtencionRead] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# People
# ---------------------------------------------------------------------------


class CiudadanoCreate(_InputModel):
    tipo_documento: str | None = Field(default=None, max_length=20)
    numero_documento: str | None = Field(default=None, max_length=30)
    nombres: str = Field(min_length=2, max_length=100)
    apellidos: str = Field(min_length=2, max_length=100)
    correo: Email | None = None
    telefono: Telefono | None = None
    autoriza_datos: bool = False

    @model_validator(mode="after")
    def documento_coherente(self) -> "CiudadanoCreate":
        if (self.tipo_documento is None) != (self.numero_documento is None):
            raise ValueError("tipo_documento and numero_documento must be provided together")
        return self


class CiudadanoRead(_OrmModel):
    id: UUID
    tipo_documento: str | None = None
    numero_documento: str | None = None
    nombres: str
    apellidos: str
    correo: Email | None = None
    telefono: Telefono | None = None
    autoriza_datos: bool


class UsuarioRead(_OrmModel):
    id: UUID
    dependencia_id: int
    correo: Email
    nombre: str
    activo: bool
    ultimo_acceso: datetime | None = None


# ---------------------------------------------------------------------------
# PQRSD case file
# ---------------------------------------------------------------------------


class PqrsdCreate(_InputModel):
    tipo_peticion_id: int = Field(gt=0)
    canal_id: int = Field(gt=0)
    dependencia_id: int = Field(gt=0)
    ciudadano_id: UUID | None = None
    asunto: str = Field(min_length=5, max_length=200)
    detalle: str = Field(min_length=20, max_length=5000)
    fecha_vencimiento: date | None = Field(
        default=None,
        description=(
            "Optional. When omitted the API computes it from the official term "
            "of the petition type, excluding weekends and the holiday catalog."
        ),
    )

    @model_validator(mode="after")
    def vencimiento_futuro(self) -> "PqrsdCreate":
        if self.fecha_vencimiento is not None and self.fecha_vencimiento < date.today():
            raise ValueError("fecha_vencimiento cannot be in the past")
        return self


class PqrsdUpdate(_InputModel):
    estado: EstadoPQRSD | None = None
    usuario_responsable_id: UUID | None = None
    respuesta: str | None = Field(default=None, min_length=20, max_length=10000)
    respondida_en: datetime | None = None

    @model_validator(mode="after")
    def respuesta_coherente(self) -> "PqrsdUpdate":
        if self.estado is EstadoPQRSD.RESPONDIDA:
            if self.respuesta is None or self.respondida_en is None:
                raise ValueError(
                    "estado 'respondida' requires both 'respuesta' and 'respondida_en'"
                )
        return self

    def transicion_valida(self, actual: EstadoPQRSD) -> bool:
        """Return True when the requested state is reachable from ``actual``."""
        if self.estado is None or self.estado is actual:
            return True
        return self.estado in SUCCESSOR_STATES[actual]


class PqrsdEventoRead(_OrmModel):
    id: int
    estado_anterior: str | None = None
    estado_nuevo: str
    usuario_id: UUID | None = None
    nota: str | None = None
    ocurrido_en: datetime


class PqrsdAnexoCreate(_InputModel):
    nombre_archivo: str = Field(min_length=1, max_length=255)
    tipo_mime: str = Field(min_length=3, max_length=100)
    tamano_bytes: int = Field(gt=0, le=10 * 1024 * 1024)
    hash_sha256: Sha256
    ruta: str = Field(min_length=1, max_length=500)


class PqrsdAnexoRead(_OrmModel):
    id: UUID
    nombre_archivo: str
    tipo_mime: str
    tamano_bytes: int
    hash_sha256: Sha256
    subido_en: datetime


class PqrsdRead(_OrmModel):
    id: UUID
    radicado: str = Field(pattern=RADICADO_PQRSD_REGEX)
    tipo_peticion_id: int
    canal_id: int
    dependencia_id: int
    ciudadano_id: UUID | None = None
    usuario_responsable_id: UUID | None = None
    asunto: str
    detalle: str
    estado: EstadoPQRSD
    fecha_radicacion: datetime
    fecha_vencimiento: date
    respondida_en: datetime | None = None
    respuesta: str | None = None
    eventos: list[PqrsdEventoRead] = Field(default_factory=list)
    anexos: list[PqrsdAnexoRead] = Field(default_factory=list)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def dias_restantes(self) -> int:
        """Business days left are approximated here; use ``festivo`` for the legal count."""
        return (self.fecha_vencimiento - date.today()).days


# ---------------------------------------------------------------------------
# Attention and satisfaction
# ---------------------------------------------------------------------------


class AtencionCreate(_InputModel):
    sede_id: int = Field(gt=0)
    canal_id: int = Field(gt=0)
    ciudadano_id: UUID | None = None
    categoria_diferencial_id: int | None = Field(default=None, gt=0)
    motivo: str = Field(min_length=5, max_length=300)


class AtencionRead(_OrmModel):
    id: UUID
    sede_id: int
    canal_id: int
    motivo: str
    iniciada_en: datetime
    finalizada_en: datetime | None = None
    duracion_segundos: int | None = None


class EncuestaCreate(_InputModel):
    atencion_id: UUID | None = None
    pqrsd_id: UUID | None = None
    puntaje: int = Field(ge=1, le=5)
    comentario: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def un_solo_origen(self) -> "EncuestaCreate":
        if (self.atencion_id is None) == (self.pqrsd_id is None):
            raise ValueError("exactly one of 'atencion_id' or 'pqrsd_id' is required")
        return self


class EncuestaRead(_OrmModel):
    id: UUID
    puntaje: int = Field(ge=1, le=5)
    comentario: str | None = None
    enviada_en: datetime


# ---------------------------------------------------------------------------
# Correspondence and operations
# ---------------------------------------------------------------------------


class CorrespondenciaCreate(_InputModel):
    radicado: str = Field(min_length=6, max_length=32, pattern=r"^[A-Z0-9-]+$")
    tipo: TipoCorrespondencia
    remitente: str | None = Field(default=None, max_length=200)
    destinatario: str | None = Field(default=None, max_length=200)
    asunto: str = Field(min_length=5, max_length=200)
    folios: int = Field(default=1, gt=0, le=999)
    planilla: str | None = Field(default=None, max_length=100)
    canal_id: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def partes_coherentes(self) -> "CorrespondenciaCreate":
        if self.tipo is TipoCorrespondencia.RECIBIDA and self.remitente is None:
            raise ValueError("'remitente' is required for received correspondence")
        if self.tipo is TipoCorrespondencia.DESPACHADA and self.destinatario is None:
            raise ValueError("'destinatario' is required for dispatched correspondence")
        return self


class CorrespondenciaRead(_OrmModel):
    id: UUID
    radicado: str
    tipo: TipoCorrespondencia
    remitente: str | None = None
    destinatario: str | None = None
    asunto: str
    folios: int
    registrada_en: datetime


class ConsultaLogCreate(_InputModel):
    pregunta_hash: bytes = Field(min_length=16, max_length=64)
    modelo: str = Field(min_length=3, max_length=100)
    latencia_ms: int = Field(gt=0, le=600_000)
    tuvo_contexto: bool
    fuentes: int = Field(default=0, ge=0, le=100)


class ConsultaLogRead(_OrmModel):
    id: int
    modelo: str
    latencia_ms: int
    tuvo_contexto: bool
    fuentes: int
    ocurrida_en: datetime


class DocumentoNormativoRead(_OrmModel):
    id: int
    nombre: str
    version: str
    vigente_desde: date
    ruta: str


class CostoTramiteRead(_OrmModel):
    concepto: str
    valor: Decimal = Field(ge=0)
    vigente_desde: date
    vigente_hasta: date | None = None


class RequisitoTramiteRead(_OrmModel):
    orden: int = Field(gt=0)
    descripcion: str
    obligatorio: bool


class ErrorDetail(BaseModel):
    """Error envelope used by the API exception handlers."""

    detail: str
    codigo: Literal[
        "validation_error",
        "not_found",
        "conflict",
        "forbidden",
        "service_unavailable",
    ] = "validation_error"
