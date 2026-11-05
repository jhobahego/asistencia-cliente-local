-- Catalog seed data taken verbatim from the manuals in knowledge_base/.
-- Idempotent: re-running it does not duplicate or overwrite edited rows.
--
--   psql "$DATABASE_URL" -f db/seed.sql

begin;

set client_encoding = 'UTF8';

-- Source: Protocolos de Servicio al Ciudadano v9, "Canales de Servicio".
insert into canal_atencion (codigo, nombre, descripcion, es_presencial) values
    ('escrito', 'Escrito', 'Correo físico o postal, correo electrónico institucional y formulario electrónico.', false),
    ('presencial', 'Presencial', 'Contacto personalizado en las instalaciones de la entidad.', true),
    ('telefonico', 'Telefónico', 'Contacto verbal por los medios telefónicos dispuestos para tal fin.', false),
    ('virtual', 'Virtual', 'Chat institucional y demás canales virtuales habilitados.', false)
on conflict (codigo) do nothing;

-- Source: Manual de Atención al Ciudadano 2023, "Términos para resolver las
-- peticiones" (Resolución 369 de 2019).
insert into tipo_peticion (codigo, nombre, plazo_dias_habiles, base_legal) values
    ('informacion_copias', 'Información y copias o fotocopias de documentos', 10, 'Resolución 369 de 2019'),
    ('consulta_materias', 'Consulta en relación con materias a cargo de la entidad', 30, 'Resolución 369 de 2019'),
    ('documentos_otras_entidades', 'Petición de documentos provenientes de otras entidades', 10, 'Resolución 369 de 2019'),
    ('acceso_consulta_documental', 'Acceso a consulta documental', 10, 'Resolución 369 de 2019'),
    ('asesoria_tecnica_capacitacion', 'Asesoría técnica y capacitación', 30, 'Resolución 369 de 2019'),
    ('quejas_denuncias', 'Quejas y denuncias', 15, 'Resolución 369 de 2019'),
    ('reclamos_sugerencias', 'Reclamos y sugerencias', 15, 'Resolución 369 de 2019')
on conflict (codigo) do nothing;

-- Source: Protocolos de Servicio al Ciudadano v9, "Atributos del buen servicio".
insert into atributo_servicio (codigo, nombre, descripcion) values
    ('respetuoso', 'Respetuoso', 'Reconoce y valora a las personas sin desconocer sus diferencias.'),
    ('amable', 'Amable', 'Trato cortés, pero también sincero.'),
    ('confiable', 'Confiable', 'Actúa conforme a lo previsto en las normas.'),
    ('empatico', 'Empático', 'Percibe lo que siente la persona y se pone en su lugar.'),
    ('incluyente', 'Incluyente', 'Servicio de calidad para todas las personas sin discriminación.'),
    ('oportuno', 'Oportuno', 'Se brinda en el momento adecuado, cumpliendo los términos acordados.'),
    ('efectivo', 'Efectivo', 'Resuelve lo solicitado.')
on conflict (codigo) do nothing;

-- Source: Manual de Atención al Ciudadano 2023 section 7 and Manual de
-- Servicio al Ciudadano 2024 section 5.6 (differential approach).
insert into categoria_diferencial (codigo, nombre, descripcion) values
    ('visual', 'Discapacidad visual', 'Personas ciegas o con baja visión.'),
    ('auditiva', 'Discapacidad auditiva', 'Personas sordas o hipoacúsicas.'),
    ('sordoceguera', 'Sordoceguera', 'Discapacidad visual y auditiva simultánea.'),
    ('fisica_motora', 'Discapacidad física o motora', 'Limitación para la movilidad.'),
    ('cognitiva', 'Discapacidad cognitiva', 'Dificultad en los procesos de comprensión.'),
    ('mental', 'Discapacidad mental', 'Condición de salud mental que requiere apoyo.'),
    ('talla_baja', 'Persona de talla baja', 'Ajustes de accesibilidad física.'),
    ('adulto_mayor', 'Adulto mayor', 'Atención preferencial.'),
    ('mujer_gestante', 'Mujer gestante', 'Atención preferencial.'),
    ('ninez_adolescencia', 'Niñez y adolescencia', 'Atención con enfoque de derechos.'),
    ('victimas_conflicto', 'Víctimas del conflicto armado', 'Atención con enfoque diferencial.'),
    ('lgbti', 'Sectores LGBTI', 'Atención libre de discriminación.'),
    ('etnicos', 'Grupos étnicos y culturales', 'Atención con enfoque intercultural.')
on conflict (codigo) do nothing;

-- Source: Guía de Lenguaje Ciudadano, section 2.2.1 ("Escriba de manera simple").
insert into glosario_termino (termino_tecnico, termino_ciudadano, ejemplo) values
    ('adolecer', 'carecer', 'Carece del requisito, no adolece del requisito.'),
    ('clarificar', 'aclarar', 'Vamos a aclarar su caso.'),
    ('coadyuvar', 'contribuir', 'Su respuesta contribuye al trámite.'),
    ('complejidad', 'dificultad', 'La dificultad del caso.'),
    ('denominación', 'nombre', 'El nombre del trámite.'),
    ('efectuar', 'hacer', 'El pago se hace en el banco.'),
    ('ejecutar', 'hacer', 'El trámite se hace en línea.'),
    ('inclusive', 'incluso', 'Incluso sin cita puede acercarse.'),
    ('intencionalidad', 'intención', 'La intención de la solicitud.'),
    ('rol', 'papel', 'El papel de cada dependencia.')
on conflict (termino_tecnico) do nothing;

-- Holidays are not seeded: the legal calendar changes every year. Load the
-- official Colombian calendar into festivo before relying on business-day math.

commit;
