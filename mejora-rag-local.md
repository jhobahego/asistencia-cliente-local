Arquitectura e Implementación de un Sistema RAG Vectorial Local con FastAPI y OllamaDiagnóstico Arquitectónico: De la Búsqueda Estática a la Recuperación Semántica VectorialLa evolución de un servicio de asistencia al cliente basado en inteligencia artificial local requiere superar las limitaciones estructurales de los esquemas de recuperación estáticos. En una arquitectura inicial donde una API REST construida con FastAPI consume un modelo de lenguaje grande (LLM) ejecutado localmente en Ollama y delega el suministro de contexto a un módulo rag.py alimentado directamente por un archivo Markdown plano de preguntas frecuentes, el sistema opera bajo un paradigma de búsqueda léxica o inyección directa de texto. Aunque este enfoque resulta funcional cuando la base de conocimiento abarca apenas una decena de fragmentos o un único documento breve, su escalabilidad colapsa rápidamente cuando el volumen documental crece hacia cientos o miles de registros.El deterioro operativo de un módulo rag.py basado en la lectura directa de archivos planos obedece a tres fenómenos técnicos interrelacionados. En primer lugar, inyectar el contenido completo de un archivo Markdown en el prompt de cada petición satura la ventana de contexto del LLM, incrementando drásticamente el tiempo de evaluación del prompt, el consumo de memoria de video (VRAM) y la degradación de atención del modelo en las secciones intermedias del texto. En segundo lugar, si el archivo rag.py intenta filtrar el documento mediante coincidencias exactas de palabras clave o expresiones regulares, el sistema pierde toda capacidad de comprensión semántica: una consulta formulada con sinónimos o giros coloquiales distintos a los redactados en el archivo Markdown no recuperará ningún fragmento útil, provocando respuestas vacías o alucinaciones. En tercer lugar, la ausencia de una capa de persistencia indexada obliga a la aplicación a procesar el archivo en memoria en cada ejecución o petición, careciendo de trazabilidad sobre qué documento o sección específica respalda cada respuesta generada.Para transformar el repositorio asistencia-cliente-local en una plataforma de grado productivo sin abandonar la premisa de privacidad y ejecución íntegramente en la máquina local, es necesario reestructurar el módulo rag.py para que actúe como un puente bidireccional entre una base de datos vectorial persistente en disco y el servidor local de Ollama. En esta arquitectura de Generación Aumentada por Recuperación (RAG), el conocimiento documental, ya provenga de archivos Markdown o documentos PDF, se divide previamente en fragmentos manejables (chunks), los cuales son transformados mediante un modelo de embeddings local en vectores numéricos de alta dimensionalidad que capturan su significado semántico.Cuando un cliente envía una pregunta al endpoint de FastAPI (por ejemplo, POST /ask o POST /v1/chat/completions), el módulo rag.py intercepta la consulta y solicita al modelo de embeddings alojado en Ollama que convierta dicha pregunta en un vector numérico. Acto seguido, la base de datos vectorial compara ese vector contra los miles de vectores almacenados en disco utilizando algoritmos de búsqueda aproximada de vecinos más cercanos, específicamente índices HNSW (Hierarchical Navigable Small World), y calcula la distancia del coseno para extraer en escasos milisegundos los $k$ fragmentos más relevantes, que habitualmente comprenden entre los 3 y 5 primeros resultados. Finalmente, rag.py ensambla un prompt estructurado que inyecta esos fragmentos verificados junto con instrucciones estrictas de anclaje (grounding), enviándolo al LLM generativo en Ollama para producir una respuesta precisa y libre de invenciones.Selección de la Base de Datos Vectorial y Estrategia de Librerías en PythonOrquestación Ligera frente a Frameworks MonolíticosUna decisión arquitectónica fundamental al modernizar rag.py consiste en determinar si se debe construir el flujo utilizando librerías específicas de bajo acoplamiento o adoptar un framework monolítico de orquestación como LangChain o LlamaIndex. Si bien bibliotecas como LlamaIndex y LangChain abstraen la extracción, indexación y conexión con el modelo en pocas líneas de código, introducir toda su jerarquía de clases en una API de FastAPI que ya cuenta con su propia lógica de negocio suele generar sobrecarga de dependencias, opacidad en el manejo de errores asíncronos y dificultades para depurar las consultas reales que se envían a Ollama.El análisis de las prácticas actuales en ingeniería de IA local demuestra que la estrategia óptima es un enfoque híbrido modular que prescinde del motor de ejecución completo de LangChain y combina, en su lugar, tres piezas especializadas e independientes. La primera pieza es el paquete autónomo langchain-text-splitters, el cual fue factorizado y separado del paquete principal de LangChain precisamente para permitir su instalación independiente (pip install langchain-text-splitters), ofreciendo los algoritmos más avanzados para fragmentar Markdown y texto plano sin arrastrar dependencias innecesarias. La segunda pieza es el SDK nativo de la base de datos vectorial (chromadb), que otorga acceso directo de bajo nivel a la gestión de colecciones, filtros de metadatos y persistencia en disco, brindando un control mucho más fino y predecible que envoltorios genéricos como langchain-chroma. Finalmente, la tercera pieza consiste en el cliente oficial de Python de Ollama (ollama) o httpx.AsyncClient, cuya integración directa permite invocar de forma nativa tanto el endpoint de embeddings por lotes (ollama.embed) como el cliente asíncrono (ollama.AsyncClient) para transmitir respuestas en tiempo real desde FastAPI sin bloquear el bucle de eventos.Evaluación y Recomendación de la Base de Datos Vectorial LocalPara cumplir con el requisito de que la base de datos vectorial resida exactamente en la misma máquina donde corre el LLM con el menor consumo de recursos posible, existen tres alternativas principales en el ecosistema de código abierto: ChromaDB, Qdrant y PostgreSQL con pgvector.Característica TécnicaChromaDB (PersistentClient)Qdrant (Local / Docker)PostgreSQL + pgvectorArquitectura de DespliegueEmbebida en proceso (Serverless local tipo SQLite) o Cliente-ServidorMotor Cliente-Servidor (requiere contenedor Docker o binario dedicado en puerto 6333)Extensión sobre servidor de base de datos relacional PostgreSQL existenteComplejidad de InstalaciónMínima (pip install chromadb, sin demonios ni Docker)Media (docker run + pip install qdrant-client)Alta (instalación de motor Postgres, compilación/activación de extensión y migraciones)Persistencia en DiscoAutomática en directorio local (ej. ./chroma_db) basada en SQLite + índices HNSWPersistente en volúmenes gestionados por el servidor QdrantPersistente en tablas transaccionales ACID de PostgreSQLIntegración Nativa con OllamaIncluye wrapper oficial OllamaEmbeddingFunction integrado en la libreríaMediante llamadas manuales a ollama.embed() e inserción de PointStructMediante generación externa de vectores e inserción SQL / ORMCaso de Uso IdealAplicaciones locales en Python/FastAPI desde prototipos hasta millones de documentos en un solo servidorMicroservicios distribuidos de alto tráfico que requieren alto rendimiento de redSistemas que ya operan PostgreSQL y buscan unificar datos relacionales y vectorialesLa evaluación comparativa conduce a recomendar de manera definitiva el uso de ChromaDB en modo PersistentClient. ChromaDB funciona como el equivalente a SQLite en el ámbito de las bases de datos vectoriales. Mientras que otras soluciones exigen levantar contenedores Docker o administrar motores de bases de datos en segundo plano que compiten por memoria RAM y CPU con Ollama, ChromaDB se ejecuta directamente dentro del proceso de Python con un simple import chromadb, guardando automáticamente todos los vectores, textos y metadatos en una carpeta local del sistema de archivos mediante chromadb.PersistentClient(path="./chroma_db"). Además, esta elección arquitectónica protege la inversión de código a futuro: si en algún momento el sistema crece hacia un entorno distribuido de múltiples servidores, ChromaDB permite cambiar del modo embebido local al modo cliente-servidor (chroma run o contenedor Docker en el puerto 8000) conservando exactamente la misma API de consulta en Python.Consideración de Segundo Orden: Bloqueos de Concurrencia en SQLiteUn matiz técnico crítico que suele pasarse por alto en implementaciones locales con FastAPI radica en la arquitectura interna de chromadb.PersistentClient. Debido a que su capa de almacenamiento local utiliza SQLite bajo el capó para gestionar los metadatos y la coordinación del índice, la ejecución de múltiples operaciones de escritura paralelas o la instanciación repetida del cliente en cada petición HTTP puede desencadenar errores de bloqueo de base de datos (Timeout/Locked errors). Asimismo, dado que FastAPI opera sobre un bucle de eventos asíncrono (event loop) de un solo hilo, cualquier llamada bloqueante mal gestionada puede congelar la totalidad de la aplicación.Para garantizar una operación robusta en producción dentro de la misma máquina, la arquitectura debe instituir una instancia única compartida (Singleton), inicializando el objeto PersistentClient y la referencia a la colección una sola vez durante el arranque de FastAPI para reutilizarlos en todas las peticiones subsecuentes. De igual modo, resulta indispensable separar los flujos de lectura y escritura, ejecutando la ingesta masiva de documentos PDF y Markdown mediante un script de sincronización dedicado o protegiendo el proceso con un semáforo asíncrono (asyncio.Semaphore) para impedir escrituras simultáneas en SQLite. Finalmente, dado que una GPU de consumo o una CPU local solo puede procesar un número limitado de flujos de inferencia simultáneos en Ollama —por ejemplo, entre 2 y 4 flujos concurrentes para modelos de 7B parámetros en una tarjeta dedicada—, la capa de FastAPI debe incorporar un asyncio.Semaphore adicional que encole ordenadamente las peticiones hacia el LLM sin desbordar la memoria de video.Modelos de Embeddings Locales en Ollama y Dinámica del Espacio VectorialUn error conceptual frecuente al construir un primer sistema RAG consiste en utilizar el mismo modelo generativo de chat (como llama3.1, mistral o llama2) para generar los vectores de búsqueda. Los modelos de chat están optimizados para predecir el siguiente token, no para comprimir el significado global de un párrafo en una representación geométrica densa; emplearlos como motor de vectorización produce representaciones deficientes y degrada severamente la precisión de búsqueda. Ollama resuelve esto sirviendo modelos de embeddings especializados a través de su misma API local en el puerto 11434, permitiendo que tanto el modelo de vectorización como el LLM de conversación coexistan en la misma infraestructura.Análisis Comparativo de Modelos para Entornos en Español y CPU/GPU LocalEl panorama de modelos de embeddings ejecutables localmente a través de Ollama ha evolucionado significativamente, desplazando las configuraciones genéricas hacia modelos con ventanas de contexto extendidas y soporte multilingüe nativo. Dado que el repositorio asistencia-cliente-local opera en español, la selección del modelo debe ponderar tanto el rendimiento en corpus multilingües como las restricciones de hardware de la máquina anfitriona.En entornos donde la ejecución se realiza exclusivamente en CPU o con recursos de memoria sumamente ajustados, nomic-embed-text (v1.5) constituye el estándar predeterminado, acumulando cerca de 90 millones de descargas en Ollama gracias a su reducida huella de 274 MB (137M de parámetros) y licencia Apache 2.0. Este modelo genera vectores de 768 dimensiones, posee una ventana nativa de 8,192 tokens y alcanza una puntuación de 62.28 en el benchmark MTEB en inglés, siendo la opción más veloz cuando el cómputo es la restricción principal. Nomic también publica la variante nomic-embed-text-v2-moe, basada en una arquitectura Mixture-of-Experts de 958 MB (475M parámetros totales y 305M activos) que incorpora soporte para cerca de 100 idiomas, aunque introduce como compensación una reducción del límite de entrada a 512 tokens.Cuando la prioridad recae en la precisión multilingüe para documentos en español y la posibilidad de realizar búsqueda híbrida, bge-m3 se posiciona como la alternativa más madura. Desarrollado por BAAI bajo licencia MIT, tiene un peso de 1.2 GB (568M de parámetros), produce vectores densos de 1,024 dimensiones y soporta una ventana de 8,192 tokens. Evaluado en más de 100 idiomas, alcanza una puntuación de 59.56 en el exigente benchmark MTEB Multilingüe de 131 tareas y destaca por ser el único modelo de código abierto capaz de generar simultáneamente representaciones densas, dispersas (léxicas estilo BM25) y multivectoriales.Por su parte, la familia qwen3-embedding (en sus variantes 0.6b, 4b y 8b) representa la generación más reciente de modelos en Ollama. La versión compacta qwen3-embedding:0.6b pesa apenas 639 MB, genera vectores de 1,024 dimensiones —reducibles hasta 32 mediante truncamiento Matryoshka (MRL)— y ofrece una extraordinaria ventana de contexto de 32,768 tokens. Con una puntuación de 64.33 en MTEB Multilingüe, supera a cualquier otro modelo inferior a 1 GB en Ollama, mientras que su versión mayor qwen3-embedding:8b (4.7 GB, 4,096 dimensiones) lidera la clasificación general con 70.58 puntos en máquinas dotadas de GPU dedicada.Modelo en OllamaComando de DescargaDimensionesContexto Máx. (Tokens)Tamaño en DiscoPrefijos Obligatorios (Documento / Consulta)nomic-embed-text (v1.5)ollama pull nomic-embed-text7688,192 (requiere num_ctx)274 MBDoc: search_document: Query: search_query: bge-m3ollama pull bge-m31,0248,1921.2 GBNinguno (texto en crudo)qwen3-embedding:0.6bollama pull qwen3-embedding:0.6b1,024 (MRL a 32)32,768639 MBDoc: NingunoQuery: Instruct: {task}\nQuery:{query}nomic-embed-text-v2-moeollama pull nomic-embed-text-v2-moe768 (MRL a 256)512958 MBDoc: search_document: Query: search_query: mxbai-embed-largeollama pull mxbai-embed-large1,024512410 MBRequiere prompt de consulta específicoembeddinggemma-2:270mollama pull embeddinggemma-2:270m768 (MRL a 128)8,192304 MBDoc: title: none | text: Query: task: search result | query: Reglas Críticas para Evitar Fallos Silenciosos en la VectorizaciónAl conectar rag.py con Ollama y ChromaDB, existen comportamientos internos que, de no gestionarse explícitamente en el código, degradan silenciosamente la calidad de las respuestas sin arrojar excepciones en consola. El primero de ellos es la incompatibilidad absoluta de espacios semánticos: los vectores generados por distintos modelos habitan espacios matemáticos independientes, por lo que calcular la similitud del coseno entre un vector de nomic-embed-text y uno de bge-m3 o qwen3-embedding carece de validez matemática, incluso si se truncan a la misma cantidad de dimensiones. Esto convierte la elección inicial del modelo en una decisión estructural, ya que cambiar de modelo de embeddings después de haber construido el índice exige borrar la colección y re-vectorizar la totalidad del corpus documental. Asimismo, como el endpoint /api/embed de Ollama devuelve vectores normalizados a longitud 1, la métrica de distancia en la base de datos vectorial debe configurarse invariablemente en similitud del coseno (cosine).Un segundo factor crítico es el truncamiento silencioso frente a la ventana de contexto y el parámetro num_ctx. Cuando un fragmento de texto supera el límite de tokens del modelo de embeddings, Ollama no devuelve un error por defecto —a menos que se pase explícitamente truncate=False—, sino que recorta silenciosamente el texto excedente, provocando la pérdida de información sin emitir advertencias en los registros del servidor. En el caso específico de nomic-embed-text v1.5, aunque el modelo soporta nativamente 8,192 tokens, la tarjeta de configuración por defecto en Ollama suele limitar el contexto activo a 2,048 tokens a menos que se amplíe mediante num_ctx en las opciones de la petición o se mantengan los fragmentos alrededor de los 512 tokens.El tercer aspecto técnico involucra la asimetría de prefijos de instrucción. Modelos como nomic-embed-text o qwen3-embedding fueron entrenados de forma asimétrica para distinguir entre un pasaje almacenado y una pregunta corta de búsqueda. Si se utiliza nomic-embed-text, cada fragmento guardado en ChromaDB debe llevar antepuesto el prefijo "search_document: " y cada pregunta del usuario debe llevar "search_query: ", pues omitir estos prefijos o mezclarlos contamina severamente la puntuación de similitud. Por el contrario, el modelo bge-m3 no requiere ningún prefijo ni durante la indexación ni durante la consulta, lo que simplifica la integración y evita errores de formateo al utilizar envoltorios automáticos como OllamaEmbeddingFunction.Finalmente, el rendimiento durante la creación de la base de datos depende de implementar la vectorización por lotes mediante ollama.embed frente al método obsoleto ollama.embeddings. El código heredado suele invocar ollama.embeddings() o el endpoint /api/embeddings dentro de un bucle, enviando un único texto por cada petición HTTP. Dado que vectorizar un documento corto toma apenas milisegundos de cómputo en GPU o CPU, iterar sobre 1,000 documentos implica asumir 1,000 veces la sobrecarga de red, apertura de conexión y serialización JSON; al utilizar ollama.embed() (endpoint /api/embed) pasando una lista de textos en el parámetro input en lotes de 32 o 128 elementos, el número de peticiones cae a 32 u 8 respectivamente, amortizando la sobrecarga hasta 128 veces.Pipeline de Ingesta y Procesamiento Documental: Archivos Markdown y PDFLa calidad de cualquier sistema RAG está gobernada por el principio de que ninguna base de datos vectorial puede compensar documentos irrelevantes o una estrategia de fragmentación deficiente. Al alimentar la base de datos con archivos Markdown (.md) y PDF (.pdf), el pipeline de ingesta debe aplicar un tratamiento diferenciado según la naturaleza estructural de cada formato.Comparativa de Formatos de Alimentación y Herramientas de ExtracciónEl formato Markdown constituye el vehículo óptimo para nutrir bases de conocimiento RAG, especialmente cuando se trata de documentación técnica o bases de preguntas frecuentes como la que ya posee el repositorio. A diferencia de los formatos binarios, un archivo .md conserva de manera explícita y ligera la jerarquía semántica del autor mediante encabezados (#, ##, ###), listas, bloques de código y reglas horizontales (---), sin introducir ruido visual. Por consiguiente, siempre que la documentación de asistencia al cliente pueda redactarse o mantenerse en Markdown, debe priorizarse este formato frente al PDF.En contraste, los archivos PDF son contenedores orientados a la maquetación visual donde el texto carece de etiquetas jerárquicas nativas, presentando saltos de línea arbitrarios o estructuras tabulares complejas. Para incorporar manuales o catálogos en PDF al sistema local en Python, la elección de la herramienta de extracción depende de la complejidad del diseño del documento. Para documentos PDF estándar compuestos principalmente por texto continuo, la librería pypdf (PdfReader), instalable vía pip install pypdf, ofrece la vía más directa y ligera al iterar sobre reader.pages e invocar page.extract_text(). Cuando se requiere mayor velocidad de análisis o mejor preservación de bloques de texto y metadatos de paginación, la integración de PyMuPDFLoader a través de langchain_community.document_loaders (respaldada por la biblioteca PyMuPDF) proporciona un motor de extracción superior. En escenarios avanzados donde los archivos PDF contienen tablas complejas, gráficos o formularios con casillas de verificación, el flujo industrial más robusto consiste en emplear analizadores documentales como Docling o LlamaParse, los cuales convierten las páginas del PDF a formato Markdown antes de pasarlas al fragmentador de texto.Estrategia de Fragmentación Semántica en Dos EtapasInsertar un documento extenso como un único registro desborda el contexto o diluye la precisión vectorial, pero cortar el texto ciegamente cada cierto número fijo de caracteres mediante CharacterTextSplitter rompe oraciones a la mitad y destruye la coherencia semántica. La arquitectura recomendada utiliza el paquete langchain-text-splitters para implementar una fragmentación jerárquica en dos etapas que preserva el significado completo de cada idea.La primera etapa, aplicada específicamente a los documentos Markdown, consiste en una división estructural por encabezados utilizando la clase MarkdownHeaderTextSplitter (o su variante avanzada ExperimentalMarkdownSyntaxTextSplitter, que también extrae bloques de código y reglas horizontales como metadatos). Al configurar los niveles de encabezado como [("#", "categoria"), ("##", "seccion"), ("###", "pregunta")], este divisor agrupa las líneas bajo su sección correspondiente e inyecta automáticamente toda la ruta de encabezados ancestros (breadcrumb) dentro del diccionario metadata de cada fragmento resultante. De este modo, un fragmento anidado profundamente conserva en sus metadatos el contexto exacto de la categoría y pregunta a la que pertenece.La segunda etapa aplica una división recursiva con solapamiento mediante RecursiveCharacterTextSplitter, tanto sobre el texto extraído de los archivos PDF como sobre las secciones de Markdown generadas en la primera etapa que superen la longitud deseada. Este algoritmo evalúa de forma recursiva una jerarquía de separadores naturales —intentando cortar primero por párrafos ("\n\n"), luego por saltos de línea ("\n"), después por oraciones (".") y finalmente por palabras (" ")— hasta que cada fragmento se ajusta al límite estipulado. Configurar un tamaño de fragmento (chunk_size) de entre 500 y 1,000 caracteres acompañado de un solapamiento (chunk_overlap) de 100 a 200 caracteres garantiza que los cortes respeten las fronteras gramaticales y que los fragmentos consecutivos compartan contexto, mejorando sustancialmente la continuidad de recuperación en documentos largos.Implementación Práctica Paso a Paso: Refactorización de asistencia-cliente-localA continuación se detalla la implementación técnica completa para transformar el repositorio asistencia-cliente-local. El diseño desacopla la aplicación en tres módulos limpios: el script de creación y actualización de la base de datos vectorial (ingest.py), el nuevo puente de recuperación semántica (rag.py) y el servidor web asíncrono (main.py).Paso 1: Preparación del Entorno, Dependencias y Modelos en OllamaEn la máquina donde se ejecuta el servicio, es necesario asegurarse de que el demonio de Ollama esté activo (ollama serve) y descargar tanto el modelo de embeddings como el modelo generativo de chat. Para un asistente en español se recomienda descargar bge-m3 por su precisión multilingüe y ausencia de requisitos de prefijos, o bien nomic-embed-text si el hardware es exclusivamente CPU con poca memoria:Bash# Descarga del modelo de embeddings multilingüe recomendado (1.2 GB)
ollama pull bge-m3

# Alternativa ultraligera para CPU (274 MB)
ollama pull nomic-embed-text

# Descarga o verificación del modelo generativo local
ollama pull llama3.1
Dentro del entorno virtual de Python del proyecto (venv), se instalan las librerías necesarias para la API, la base de datos vectorial, el procesamiento de PDFs y la fragmentación de texto:Bashpip install fastapi uvicorn chromadb ollama langchain-text-splitters pypdf pydantic httpx
La estructura del proyecto utilizará un directorio ./knowledge_base para depositar todos los archivos .md (como el archivo actual de preguntas del repositorio) y .pdf, mientras que ChromaDB creará automáticamente el directorio ./chroma_db para almacenar los índices vectoriales en disco.Paso 2: Creación y Alimentación de la Base de Datos Vectorial (ingest.py)El script ingest.py recorre la carpeta de documentos, aplica la estrategia de fragmentación en dos etapas para archivos Markdown y la extracción paginada para archivos PDF, y persiste los vectores en ChromaDB. Un detalle fundamental de esta implementación es el uso de collection.upsert() junto con identificadores deterministas basados en hashes: a diferencia de collection.add(), el método upsert actualiza los documentos existentes y agrega los nuevos sin duplicar vectores cuando el script se vuelve a ejecutar.Pythonimport hashlib
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from pypdf import PdfReader
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

# Configuración local centralizada
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "asistencia_cliente_kb"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
EMBEDDING_MODEL = "bge-m3"
DOCS_DIR = "./knowledge_base"


def generate_chunk_id(source: str, index: int, content: str) -> str:
    """Genera un ID único determinista combinando archivo, índice y hash MD5."""
    content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()[:8]
    return f"{source}_chunk_{index}_{content_hash}"


def process_markdown_file(file_path: Path) -> List[Dict[str, Any]]:
    """Lee un archivo Markdown y lo fragmenta preservando la jerarquía de encabezados."""
    with open(file_path, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    # Etapa 1: División estructural por encabezados de Markdown
    headers_to_split_on = [
        ("#", "categoria"),
        ("##", "seccion"),
        ("###", "pregunta"),
    ]
    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False,
    )
    md_header_splits = md_splitter.split_text(markdown_text)

    # Etapa 2: Sub-división recursiva con solapamiento
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    final_splits = recursive_splitter.split_documents(md_header_splits)

    processed_chunks = []
    for idx, doc in enumerate(final_splits):
        metadata = {
            "source": file_path.name,
            "file_type": "markdown",
            "categoria": doc.metadata.get("categoria", "General"),
            "seccion": doc.metadata.get("seccion", "N/A"),
            "pregunta": doc.metadata.get("pregunta", "N/A"),
        }
        processed_chunks.append({
            "id": generate_chunk_id(file_path.name, idx, doc.page_content),
            "text": doc.page_content,
            "metadata": metadata,
        })
    return processed_chunks


def process_pdf_file(file_path: Path) -> List[Dict[str, Any]]:
    """Extrae texto de archivos PDF página por página y lo divide en fragmentos con solapamiento."""
    reader = PdfReader(str(file_path))
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=180,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    processed_chunks = []
    global_idx = 0

    for page_num, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text()
        if not raw_text or not raw_text.strip():
            continue

        page_chunks = recursive_splitter.split_text(raw_text)
        for chunk_text in page_chunks:
            metadata = {
                "source": file_path.name,
                "file_type": "pdf",
                "page": page_num,
                "categoria": "Documento PDF",
            }
            processed_chunks.append({
                "id": generate_chunk_id(file_path.name, global_idx, chunk_text),
                "text": chunk_text,
                "metadata": metadata,
            })
            global_idx += 1

    return processed_chunks


def build_or_update_vector_db() -> None:
    """Inicializa ChromaDB persistente e indexa todos los documentos .md y .pdf."""
    docs_path = Path(DOCS_DIR)
    docs_path.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    ollama_ef = OllamaEmbeddingFunction(
        url=OLLAMA_EMBED_URL,
        model_name=EMBEDDING_MODEL,
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ollama_ef,
        metadata={"hnsw:space": "cosine"},
    )

    all_chunks: List[Dict[str, Any]] = []
    for file_path in docs_path.iterdir():
        if file_path.suffix.lower() == ".md":
            print(f"Procesando archivo Markdown: {file_path.name}")
            all_chunks.extend(process_markdown_file(file_path))
        elif file_path.suffix.lower() == ".pdf":
            print(f"Procesando archivo PDF: {file_path.name}")
            all_chunks.extend(process_pdf_file(file_path))

    if not all_chunks:
        print(f"No se encontraron archivos .md o .pdf en {DOCS_DIR}.")
        return

    batch_size = 64
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i : i + batch_size]
        collection.upsert(
            ids=[item["id"] for item in batch],
            documents=[item["text"] for item in batch],
            metadatas=[item["metadata"] for item in batch],
        )
        print(f"Sincronizados fragmentos {i + 1} a {min(i + batch_size, len(all_chunks))}...")

    print(f"Indexación finalizada. Total de fragmentos en ChromaDB: {collection.count()}")


if __name__ == "__main__":
    build_or_update_vector_db()
Paso 3: Refactorización del Módulo Puente (rag.py)El nuevo archivo rag.py reemplaza la lectura estática del archivo Markdown por la clase LocalVectorRAG, que conecta chromadb.PersistentClient con ollama.AsyncClient. Para evitar que el asistente se distraiga con fragmentos irrelevantes cuando el usuario realiza preguntas fuera de dominio, el método de recuperación aplica un umbral de similitud (max_distance) sobre la distancia del coseno calculada por ChromaDB:$$\text{Distancia}_{\text{coseno}} = 1 - \text{Similitud}_{\text{coseno}} = 1 - \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$$En esta escala, $0.0$ representa vectores idénticos y los valores cercanos o superiores a $1.0$ indican ausencia de relación semántica. Descartar cualquier fragmento cuya distancia supere el umbral configurado (por ejemplo, $0.65$) e instruir explícitamente al LLM para que se limite al contexto recuperado reduce drásticamente las alucinaciones.Pythonfrom typing import List, Dict, Any, Optional, AsyncGenerator
import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from ollama import AsyncClient

from ingest import CHROMA_DB_PATH, COLLECTION_NAME, OLLAMA_EMBED_URL, EMBEDDING_MODEL


class LocalVectorRAG:
    """
    Puente entre ChromaDB local y el servidor LLM en Ollama.
    Diseñado para instanciarse una sola vez en el estado de FastAPI.
    """

    def __init__(
        self,
        llm_model: str = "llama3.1",
        ollama_host: str = "http://localhost:11434",
        top_k: int = 4,
        max_distance: float = 0.65,
    ):
        self.llm_model = llm_model
        self.top_k = top_k
        self.max_distance = max_distance

        self.ollama_async_client = AsyncClient(host=ollama_host)
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.embedding_fn = OllamaEmbeddingFunction(
            url=OLLAMA_EMBED_URL,
            model_name=EMBEDDING_MODEL,
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def retrieve_context(
        self,
        query: str,
        categoria_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Ejecuta la búsqueda vectorial y filtra resultados según el umbral de distancia."""
        where_clause = {"categoria": categoria_filter} if categoria_filter else None

        results = self.collection.query(
            query_texts=[query],
            n_results=self.top_k,
            where=where_clause,
            include=["documents", "metadatas", "distances"],
        )

        valid_chunks: List[Dict[str, Any]] = []
        if not results["documents"] or not results["documents"][0]:
            return valid_chunks

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0]

        for doc, meta, dist in zip(docs, metas, distances):
            if dist <= self.max_distance:
                valid_chunks.append({
                    "content": doc,
                    "metadata": meta,
                    "distance": round(dist, 4),
                })

        return valid_chunks

    def build_messages(self, user_query: str, retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Construye los mensajes del sistema e inyecta los fragmentos recuperados."""
        if not retrieved_chunks:
            context_block = "NO SE ENCONTRÓ INFORMACIÓN RELEVANTE EN LA BASE DE CONOCIMIENTO."
        else:
            formatted_parts = []
            for idx, item in enumerate(retrieved_chunks, start=1):
                meta = item["metadata"]
                source_info = f"Fuente: {meta.get('source', 'Desconocida')}"
                if meta.get("file_type") == "pdf":
                    source_info += f" (Página {meta.get('page', '?')})"
                elif meta.get("seccion") and meta.get("seccion") != "N/A":
                    source_info += f" | Sección: {meta.get('seccion')}"

                formatted_parts.append(f"[Fragmento {idx} - {source_info}]\n{item['content']}")
            context_block = "\n\n---\n\n".join(formatted_parts)

        system_prompt = (
            "Eres un asistente de atención al cliente experto, preciso y cortés. "
            "Responde a la consulta del usuario basándote ÚNICAMENTE en los fragmentos de contexto "
            "proporcionados a continuación. Si la respuesta no se encuentra en el contexto, "
            "indica amablemente que no dispones de esa información en la documentación oficial "
            "y evita inventar datos o suposiciones.\n\n"
            f"CONTEXTO OFICIAL RECUPERADO:\n{context_block}"
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ]

    async def ask(self, query: str, categoria: Optional[str] = None) -> Dict[str, Any]:
        """Recupera contexto de ChromaDB y genera la respuesta completa con Ollama."""
        chunks = self.retrieve_context(query, categoria_filter=categoria)
        messages = self.build_messages(query, chunks)

        response = await self.ollama_async_client.chat(
            model=self.llm_model,
            messages=messages,
            stream=False,
        )

        return {
            "answer": response["message"]["content"],
            "sources": chunks,
        }

    async def ask_stream(self, query: str, categoria: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Recupera contexto y transmite la respuesta generada token por token."""
        chunks = self.retrieve_context(query, categoria_filter=categoria)
        messages = self.build_messages(query, chunks)

        stream = await self.ollama_async_client.chat(
            model=self.llm_model,
            messages=messages,
            stream=True,
        )

        async for part in stream:
            token = part["message"]["content"]
            if token:
                yield token

Paso 4: Integración Asíncrona y Streaming en FastAPI (main.py)El módulo main.py expone la funcionalidad de LocalVectorRAG a través de endpoints validados con esquemas Pydantic. La arquitectura implementa el gestor de contexto lifespan para compartir la instancia del cliente vectorial y del cliente asíncrono de Ollama en el estado de la aplicación (app.state), utiliza un asyncio.Semaphore para evitar saturar la GPU o CPU local ante peticiones concurrentes y ofrece tanto un endpoint de respuesta completa con trazabilidad de fuentes como un endpoint con StreamingResponse para visualización inmediata de tokens.Pythonimport asyncio
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from rag import LocalVectorRAG
from ingest import build_or_update_vector_db


# Limita el número de inferencias simultáneas hacia Ollama según el hardware local
LLM_CONCURRENCY_LIMIT = 3
inference_semaphore = asyncio.Semaphore(LLM_CONCURRENCY_LIMIT)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa la conexión con ChromaDB y Ollama al levantar FastAPI."""
    app.state.rag = LocalVectorRAG(
        llm_model="llama3.1",
        ollama_host="http://localhost:11434",
        top_k=4,
        max_distance=0.65,
    )
    yield


app = FastAPI(
    title="API de Asistencia al Cliente Local con RAG Vectorial",
    version="2.0.0",
    lifespan=lifespan,
)


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Pregunta del cliente")
    categoria: Optional[str] = Field(None, description="Filtro opcional de categoría en metadatos")


class SourceMetadata(BaseModel):
    content: str
    metadata: Dict[str, Any]
    distance: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceMetadata]


@app.post("/api/v1/ask", response_model=QueryResponse)
async def ask_question(payload: QueryRequest, request: Request):
    """Devuelve la respuesta generada junto con los fragmentos documentales que la respaldan."""
    rag_engine: LocalVectorRAG = request.app.state.rag
    try:
        async with inference_semaphore:
            result = await rag_engine.ask(
                query=payload.question,
                categoria=payload.categoria,
            )
            return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error en el motor RAG local: {str(exc)}")


@app.post("/api/v1/ask/stream")
async def ask_question_stream(payload: QueryRequest, request: Request):
    """Transmite la respuesta token por token en tiempo real."""
    rag_engine: LocalVectorRAG = request.app.state.rag

    async def token_generator():
        async with inference_semaphore:
            async for token in rag_engine.ask_stream(
                query=payload.question,
                categoria=payload.categoria,
            ):
                yield token

    return StreamingResponse(token_generator(), media_type="text/plain; charset=utf-8")


@app.post("/api/v1/sync-kb")
async def sync_knowledge_base():
    """Ejecuta la re-indexación de archivos PDF y Markdown en un hilo separado."""
    try:
        await asyncio.to_thread(build_or_update_vector_db)
        return {"status": "ok", "message": "Base de datos vectorial actualizada correctamente."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Fallo al indexar documentos: {str(exc)}")

Conclusiones y Recomendaciones de Operación en ProducciónLa transición desde un archivo rag.py basado en la lectura directa de un documento Markdown hacia una arquitectura respaldada por ChromaDB (PersistentClient), Ollama y langchain-text-splitters transforma radicalmente las capacidades del repositorio asistencia-cliente-local. Al consolidar tanto la base de datos vectorial como los motores de embeddings y generación dentro de la misma máquina física, el sistema preserva intacta la soberanía y privacidad de los datos sin incurrir en costos recurrentes por token de APIs comerciales ni depender de conectividad externa.Para asegurar el éxito sostenido del despliegue en producción, conviene estandarizar la gestión documental manteniendo las preguntas frecuentes y guías operativas en archivos Markdown estructurados con encabezados #, ## y ###, mientras se reserva el formato PDF para manuales extensos o documentos oficiales de solo lectura. El uso de MarkdownHeaderTextSplitter convierte automáticamente esa estructura de encabezados en metadatos navegables, permitiendo filtrar respuestas por departamento o categoría mediante la cláusula where de ChromaDB antes siquiera de ejecutar la comparación vectorial.En cuanto a la alineación entre el hardware local y los modelos de vectorización, los servidores que cuenten con GPU dedicada o memoria unificada holgada obtendrán el mayor beneficio al operar bge-m3 o qwen3-embedding:0.6b debido a su dominio del español y su amplia ventana de contexto de entre 8,192 y 32,768 tokens. En máquinas restringidas exclusivamente a una CPU modesta, nomic-embed-text v1.5 proporciona la menor latencia con apenas 274 MB en disco, requiriendo únicamente cuidar el uso de los prefijos search_document: y search_query: y configurar num_ctx si se procesan fragmentos largos.Finalmente, la inclusión de los fragmentos recuperados y sus distancias matemáticas dentro de la respuesta JSON del endpoint /api/v1/ask dota al sistema de observabilidad inmediata para auditar en qué documento y página se fundamenta cada respuesta del asistente. Monitorear las puntuaciones de distancia reales durante las primeras semanas de uso permitirá calibrar con exactitud el parámetro max_distance entre 0.55 y 0.75, estableciendo al mismo tiempo las bases para evolucionar en el futuro hacia esquemas de búsqueda híbrida que combinen la coincidencia léxica exacta (vectores dispersos estilo BM25 de bge-m3) con la recuperación semántica densa.
