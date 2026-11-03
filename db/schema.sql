-- Relational model for the citizen-service backend.
--
-- Complements the vector store (chroma_db/): this schema holds the case file,
-- the service catalogs and the audit trail. It never stores document chunks,
-- embeddings or Chroma ids; those stay in the vector database.
--
-- Requires PostgreSQL 13+ (gen_random_uuid, identity columns) and the pg_trgm
-- contrib extension for the trigram search index. Run once:
--
--   psql "$DATABASE_URL" -f db/schema.sql
--   psql "$DATABASE_URL" -f db/seed.sql
--
-- Day of week follows ISO-8601: 1 = Monday ... 7 = Sunday.

begin;

create extension if not exists pg_trgm;

-- ---------------------------------------------------------------------------
-- Shared trigger functions
-- ---------------------------------------------------------------------------

create or replace function set_updated_at() returns trigger
language plpgsql as $$
begin
    new.updated_at := now();
    return new;
end;
$$;

create or replace function forbid_change() returns trigger
language plpgsql as $$
begin
    raise exception 'table %.% is append-only', tg_table_schema, tg_table_name;
end;
$$;

-- ---------------------------------------------------------------------------
-- Catalogs
-- ---------------------------------------------------------------------------

create table dependencia (
    id          smallint generated always as identity primary key,
    codigo      text        not null unique,
    nombre      text        not null,
    activa      boolean     not null default true,
    created_at  timestamptz not null default now(),
    updated_at  timestamptz not null default now()
);

create table canal_atencion (
    id            smallint generated always as identity primary key,
    codigo        text        not null unique,
    nombre        text        not null,
    descripcion   text,
    es_presencial boolean     not null default false
);

create table tipo_peticion (
    id                 smallint generated always as identity primary key,
    codigo             text     not null unique,
    nombre             text     not null,
    plazo_dias_habiles smallint not null check (plazo_dias_habiles between 1 and 60),
    base_legal         text     not null
);

create table festivo (
    fecha       date primary key,
    descripcion text not null
);

create table categoria_diferencial (
    id          smallint generated always as identity primary key,
    codigo      text not null unique,
    nombre      text not null,
    descripcion text
);

create table atributo_servicio (
    id          smallint generated always as identity primary key,
    codigo      text not null unique,
    nombre      text not null,
    descripcion text
);

-- Terms that must be translated to citizen language before answering.
create table glosario_termino (
    id                smallint generated always as identity primary key,
    termino_tecnico   text not null unique,
    termino_ciudadano text not null,
    ejemplo           text
);

-- ---------------------------------------------------------------------------
-- Organization and service points
-- ---------------------------------------------------------------------------

create table sede (
    id             smallint generated always as identity primary key,
    dependencia_id smallint not null references dependencia,
    nombre         text     not null,
    direccion      text     not null,
    ciudad         text     not null,
    telefono       text,
    activa         boolean  not null default true,
    created_at     timestamptz not null default now(),
    updated_at     timestamptz not null default now(),
    unique (dependencia_id, nombre)
);

create table horario_atencion (
    id          smallint generated always as identity primary key,
    sede_id     smallint not null references sede on delete cascade,
    dia_semana  smallint not null check (dia_semana between 1 and 7),
    hora_inicio time     not null,
    hora_fin    time     not null,
    check (hora_fin > hora_inicio),
    unique (sede_id, dia_semana, hora_inicio)
);

-- Contact value of a channel for a specific site (mailbox, phone, chat URL).
create table canal_sede (
    canal_id smallint not null references canal_atencion,
    sede_id  smallint not null references sede on delete cascade,
    valor    text     not null,
    primary key (canal_id, sede_id, valor)
);

-- ---------------------------------------------------------------------------
-- Service portfolio
-- ---------------------------------------------------------------------------

create table tramite (
    id             smallint generated always as identity primary key,
    codigo         text not null unique,
    nombre         text not null,
    descripcion    text,
    dependencia_id smallint not null references dependencia,
    canal_id       smallint references canal_atencion,
    activo         boolean not null default true,
    created_at     timestamptz not null default now(),
    updated_at     timestamptz not null default now()
);

create table requisito_tramite (
    id          smallint generated always as identity primary key,
    tramite_id  smallint not null references tramite on delete cascade,
    orden       smallint not null check (orden > 0),
    descripcion text     not null,
    obligatorio boolean  not null default true,
    unique (tramite_id, orden)
);

create table costo_tramite (
    id            smallint generated always as identity primary key,
    tramite_id    smallint not null references tramite on delete cascade,
    concepto      text     not null,
    valor         numeric(12, 2) not null check (valor >= 0),
    vigente_desde date     not null,
    vigente_hasta date,
    check (vigente_hasta is null or vigente_hasta >= vigente_desde)
);

-- ---------------------------------------------------------------------------
-- People and access control
-- ---------------------------------------------------------------------------

create table ciudadano (
    id               uuid primary key default gen_random_uuid(),
    tipo_documento   text,
    numero_documento text,
    nombres          text not null,
    apellidos        text not null,
    correo           text,
    telefono         text,
    autoriza_datos   boolean not null default false,
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now(),
    check ((tipo_documento is null) = (numero_documento is null)),
    check (correo is null or correo ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
    check (telefono is null or telefono ~ '^[0-9+() -]{7,20}$')
);

-- Document is optional, so uniqueness applies only when it is present.
create unique index ciudadano_documento_uq
    on ciudadano (tipo_documento, numero_documento)
    where numero_documento is not null;

create table usuario (
    id             uuid primary key default gen_random_uuid(),
    dependencia_id smallint not null references dependencia,
    correo         text     not null unique,
    nombre         text     not null,
    hash_password  text     not null,
    activo         boolean  not null default true,
    ultimo_acceso  timestamptz,
    created_at     timestamptz not null default now(),
    updated_at     timestamptz not null default now(),
    check (correo ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$')
);

create table rol (
    id          smallint generated always as identity primary key,
    codigo      text not null unique,
    nombre      text not null,
    descripcion text
);

create table usuario_rol (
    usuario_id uuid     not null references usuario on delete cascade,
    rol_id     smallint not null references rol on delete cascade,
    primary key (usuario_id, rol_id)
);

create table sesion (
    id          uuid primary key default gen_random_uuid(),
    usuario_id  uuid not null references usuario on delete cascade,
    emitida_en  timestamptz not null default now(),
    expira_en   timestamptz not null,
    revocada_en timestamptz,
    ip          inet,
    user_agent  text,
    check (expira_en > emitida_en)
);

create index sesion_usuario_idx on sesion (usuario_id, expira_en desc);

-- ---------------------------------------------------------------------------
-- Case file: PQRSD
-- ---------------------------------------------------------------------------

-- One row per year; the radicado is a correlative that must never repeat,
-- be amended or be struck through.
create table secuencia_radicado (
    vigencia smallint primary key,
    ultimo   bigint not null default 0 check (ultimo >= 0)
);

create or replace function next_radicado(p_vigencia smallint) returns text
language plpgsql as $$
declare
    v_next bigint;
begin
    insert into secuencia_radicado (vigencia, ultimo)
    values (p_vigencia, 1)
    on conflict (vigencia)
        do update set ultimo = secuencia_radicado.ultimo + 1
    returning ultimo into v_next;

    return 'PQRSD-' || p_vigencia::text || '-' || lpad(v_next::text, 6, '0');
end;
$$;

create table pqrsd (
    id                     uuid primary key default gen_random_uuid(),
    radicado               text not null unique
                              default next_radicado(extract(year from now())::smallint),
    tipo_peticion_id       smallint not null references tipo_peticion,
    canal_id               smallint not null references canal_atencion,
    dependencia_id         smallint not null references dependencia,
    ciudadano_id           uuid references ciudadano,
    usuario_responsable_id uuid references usuario,
    asunto                 text not null check (char_length(asunto) between 5 and 200),
    detalle                text not null check (char_length(detalle) >= 20),
    estado                 text not null default 'recibida'
                              check (estado in ('recibida', 'en_tramite', 'respondida', 'vencida', 'cerrada', 'archivada')),
    fecha_radicacion       timestamptz not null default now(),
    fecha_vencimiento      date not null,
    respondida_en          timestamptz,
    respuesta              text,
    created_at             timestamptz not null default now(),
    updated_at             timestamptz not null default now(),
    check (respondida_en is null or respondida_en >= fecha_radicacion),
    check (estado <> 'respondida' or (respondida_en is not null and respuesta is not null)),
    check (radicado ~ '^PQRSD-[0-9]{4}-[0-9]{6}$')
);

create index pqrsd_vencimiento_idx on pqrsd (estado, fecha_vencimiento)
    where estado in ('recibida', 'en_tramite');
create index pqrsd_dependencia_idx on pqrsd (dependencia_id, estado);
create index pqrsd_ciudadano_idx on pqrsd (ciudadano_id) where ciudadano_id is not null;
create index pqrsd_asunto_trgm_idx on pqrsd using gin (asunto gin_trgm_ops);

create or replace function pqrsd_radicado_immutable() returns trigger
language plpgsql as $$
begin
    if new.radicado is distinct from old.radicado then
        raise exception 'radicado % cannot be modified', old.radicado;
    end if;
    return new;
end;
$$;

create table pqrsd_evento (
    id              bigint generated always as identity primary key,
    pqrsd_id        uuid not null references pqrsd on delete cascade,
    estado_anterior text,
    estado_nuevo    text not null,
    usuario_id      uuid references usuario,
    nota            text,
    ocurrido_en     timestamptz not null default now(),
    check (estado_anterior is null or estado_anterior <> estado_nuevo)
);

create index pqrsd_evento_pqrsd_idx on pqrsd_evento (pqrsd_id, ocurrido_en);

create table pqrsd_anexo (
    id            uuid primary key default gen_random_uuid(),
    pqrsd_id      uuid not null references pqrsd on delete cascade,
    nombre_archivo text not null,
    tipo_mime     text not null,
    tamano_bytes  bigint not null check (tamano_bytes > 0 and tamano_bytes <= 10485760),
    hash_sha256   text not null check (hash_sha256 ~ '^[a-f0-9]{64}$'),
    ruta          text not null,
    subido_por    uuid references usuario,
    subido_en     timestamptz not null default now(),
    unique (pqrsd_id, hash_sha256)
);

-- ---------------------------------------------------------------------------
-- Attention sessions and satisfaction
-- ---------------------------------------------------------------------------

create table atencion (
    id                        uuid primary key default gen_random_uuid(),
    sede_id                   smallint not null references sede,
    canal_id                  smallint not null references canal_atencion,
    ciudadano_id              uuid references ciudadano,
    categoria_diferencial_id  smallint references categoria_diferencial,
    atendida_por              uuid references usuario,
    motivo                    text not null check (char_length(motivo) between 5 and 300),
    iniciada_en               timestamptz not null default now(),
    finalizada_en             timestamptz,
    duracion_segundos         integer generated always as
                                  (extract(epoch from (finalizada_en - iniciada_en))::integer) stored,
    check (finalizada_en is null or finalizada_en >= iniciada_en)
);

create index atencion_sede_idx on atencion (sede_id, iniciada_en desc);

create table encuesta_satisfaccion (
    id          uuid primary key default gen_random_uuid(),
    atencion_id uuid references atencion on delete cascade,
    pqrsd_id    uuid references pqrsd on delete cascade,
    puntaje     smallint not null check (puntaje between 1 and 5),
    comentario  text check (char_length(comentario) <= 1000),
    enviada_en  timestamptz not null default now(),
    check (num_nonnulls(atencion_id, pqrsd_id) = 1)
);

-- ---------------------------------------------------------------------------
-- Postal and email correspondence
-- ---------------------------------------------------------------------------

create table correspondencia (
    id              uuid primary key default gen_random_uuid(),
    radicado        text not null unique check (radicado ~ '^[A-Z0-9-]{6,32}$'),
    tipo            text not null check (tipo in ('recibida', 'despachada')),
    remitente       text,
    destinatario    text,
    asunto          text not null,
    folios          smallint not null default 1 check (folios > 0),
    planilla        text,
    canal_id        smallint references canal_atencion,
    registrada_en   timestamptz not null default now(),
    registrada_por  uuid references usuario,
    check (tipo <> 'recibida' or remitente is not null),
    check (tipo <> 'despachada' or destinatario is not null)
);

create index correspondencia_tipo_idx on correspondencia (tipo, registrada_en desc);

-- ---------------------------------------------------------------------------
-- Operations: normative versions, query metrics, audit trail
-- ---------------------------------------------------------------------------

create table documento_normativo (
    id           smallint generated always as identity primary key,
    nombre       text not null,
    version      text not null,
    vigente_desde date not null,
    hash_sha256  text not null check (hash_sha256 ~ '^[a-f0-9]{64}$'),
    ruta         text not null,
    unique (nombre, version)
);

-- Latency metrics for the local model. The question itself is never stored:
-- only its hash, so the table stays free of personal data.
create table consulta_log (
    id             bigint generated always as identity primary key,
    pregunta_hash  bytea not null,
    modelo         text not null,
    latencia_ms    integer not null check (latencia_ms > 0),
    tuvo_contexto  boolean not null,
    fuentes        smallint not null default 0 check (fuentes >= 0),
    ocurrida_en    timestamptz not null default now()
);

create index consulta_log_fecha_idx on consulta_log (ocurrida_en desc);

create table auditoria (
    id          bigint generated always as identity primary key,
    tabla       text not null,
    operacion   text not null check (operacion in ('insert', 'update', 'delete')),
    registro_id text not null,
    usuario_id  uuid references usuario,
    datos       jsonb,
    ocurrida_en timestamptz not null default now()
);

create index auditoria_tabla_idx on auditoria (tabla, ocurrida_en desc);

create or replace function audit_change() returns trigger
language plpgsql as $$
begin
    insert into auditoria (tabla, operacion, registro_id, usuario_id, datos)
    values (
        tg_table_name,
        lower(tg_op),
        coalesce(new.id, old.id)::text,
        nullif(current_setting('app.usuario_id', true), '')::uuid,
        case when tg_op = 'DELETE' then to_jsonb(old) else to_jsonb(new) end
    );
    return coalesce(new, old);
end;
$$;

-- ---------------------------------------------------------------------------
-- Triggers
-- ---------------------------------------------------------------------------

create trigger dependencia_set_updated_at before update on dependencia
    for each row execute function set_updated_at();
create trigger sede_set_updated_at before update on sede
    for each row execute function set_updated_at();
create trigger tramite_set_updated_at before update on tramite
    for each row execute function set_updated_at();
create trigger ciudadano_set_updated_at before update on ciudadano
    for each row execute function set_updated_at();
create trigger usuario_set_updated_at before update on usuario
    for each row execute function set_updated_at();
create trigger pqrsd_set_updated_at before update on pqrsd
    for each row execute function set_updated_at();

create trigger pqrsd_radicado_immutable before update on pqrsd
    for each row execute function pqrsd_radicado_immutable();

create trigger pqrsd_evento_append_only before update or delete on pqrsd_evento
    for each row execute function forbid_change();

create trigger pqrsd_audit after insert or update or delete on pqrsd
    for each row execute function audit_change();

-- ---------------------------------------------------------------------------
-- Reporting views
-- ---------------------------------------------------------------------------

create view v_pqrsd_vencidas as
select p.radicado,
       p.estado,
       tp.nombre  as tipo_peticion,
       d.nombre   as dependencia,
       p.fecha_radicacion,
       p.fecha_vencimiento,
       (current_date - p.fecha_vencimiento) as dias_vencida
from pqrsd p
join tipo_peticion tp on tp.id = p.tipo_peticion_id
join dependencia d on d.id = p.dependencia_id
where p.estado in ('recibida', 'en_tramite')
  and p.fecha_vencimiento < current_date;

-- ---------------------------------------------------------------------------
-- Row level security (enable once the API sets app.dependencia_id per request)
-- ---------------------------------------------------------------------------
--
--   alter table pqrsd enable row level security;
--   create policy pqrsd_dependencia_isolation on pqrsd
--       using (dependencia_id = current_setting('app.dependencia_id')::smallint);
--
-- The table owner bypasses row level security unless FORCE ROW LEVEL SECURITY
-- is set, so the API must connect with a dedicated, non-owner role.

commit;
