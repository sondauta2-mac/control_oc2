# -*- coding: utf-8 -*-
"""Script final de consolidación de documentación técnica SDD"""

specs_content = """# Documento de Especificación de Requerimientos (Specs - Final POC)
**Proyecto:** Sistema de Seguimiento Automatizado de Órdenes de Compra (Seguimiento OC)  
**Estado:** Prueba de Concepto (POC) Validada con Matriz Multi-Formato  
**Enfoque de Diseño:** Tradicional Basado en Reglas (Determinista)

---

## 1. Requerimientos Funcionales (RF)

### RF-01: Identificación y Entrada de Usuario
* El sistema debe solicitar el nombre completo del usuario solicitante mediante un campo de entrada de texto plano (`st.text_input`).
* **UX Fina:** El cursor de escritura debe posicionarse automáticamente (*foco de interfaz*) dentro de la casilla de texto tanto en el inicio del software como tras cada reinicio de sesión, sin requerir clics manuales del ratón.

### RF-02: Conexión y Consumo de Datos (Excel)
* El sistema debe realizar la lectura asíncrona de una planilla Excel (`compras.xlsx`) que actúa como base de datos local en fase POC.
* Las columnas requeridas para el procesamiento son estrictamente: `Solicitante`, `Orden`, `Monto`, y `Estado`.

### RF-03: Reglas de Filtrado y Negocio
Dada la identificación ingresada por el usuario, el software debe aplicar un doble filtro lógico inclusivo sobre la matriz de datos:
1. Coincidencia de Nombre: `Solicitante == Entrada_Usuario` (Insensible a mayúsculas y minúsculas; remoción obligatoria de espacios en blanco marginales via `.strip()`).
2. Estado de la Fila: El registro debe estar clasificado estrictamente en los estados `Aprobada` o `Pendiente`. Filas con estados como `Rechazada` u otros deben ser omitidas por el motor de búsqueda.

### RF-04: Presentación de Datos en Interfaz (UI)
* En caso de éxito, el sistema saludará al usuario y desplegará los registros en una **Mini Tabla Estructurada** integrada en el flujo conversacional (`st.dataframe`).
* La tabla debe desplegar el orden de columnas nativo: `Orden` | `Monto` | `Estado` | ` [Ícono]`.
* **Formateo Financiero:** La columna `Monto` debe auto-formatearse visualmente con el signo de moneda nacional (`$`) y puntos divisorios como separadores de miles (ej: `$150.000`).
* **Sello de Estado (Íconos Dinámicos):** Al final de cada fila, se inyectará una columna visual de estado:
  * Estado *Aprobada* -> Se asocia un ticket verde (`✅`).
  * Estado *Pendiente* -> Se asocia un signo de interrogación (`❓`).

### RF-05: Sistema Unificado de Exportación Multi-Formato (CSV / XLSX / PDF)

#### PARTE 1: Motores de Compilación y Transformación de Datos (Backend)
* **Aislamiento de Control de UI:** Las tres herramientas de exportación operan exclusivamente sobre la matriz limpia de negocio (`Orden`, `Monto`, `Estado`), excluyendo la columna visual de checks lógicos de la interfaz.
* **Canal 1 (CSV Regional):** Estructurado con delimitador de punto y coma (`;`) y firma de bytes `utf-8-sig` para compatibilidad nativa mediante doble clic en Excel en español (región Chile/Latam) sin romper filas por uso de comas decimales.
* **Canal 2 (Excel - .xlsx):** Compilado binariamente a través de buffers en memoria (`io.BytesIO`) utilizando el motor `openpyxl`. Mantiene los tipos de datos numéricos puros de los montos para auditorías o sumatorias financieras inmediatas.
* **Canal 3 (PDF - .pdf):** Diseñado mediante objetos de flujo de la librería `ReportLab`. Genera tablas formalizadas impresas con paletas de colores corporativos (Hex #1E3A8A) y tipografías Helvetica.

#### PARTE 2: Grid de Distribución Horizontal en la Interfaz (UI/UX)
* **Distribución en Grilla:** Los tres botones (`Descargar CSV`, `Descargar Excel`, `Descargar PDF`) se posicionan de forma adyacente horizontal compartiendo el mismo eje a través de un contenedor de tres columnas equitativas (`st.columns(3)`).
* **Posicionamiento Secuencial:** El bloque unificado de exportación se inserta estrictamente al terminar de renderizar la tabla web y de forma previa al despliegue de la pregunta de control.
* **Persistencia:** Los archivos adoptan la nomenclatura estandarizada `ordenes_[Nombre_Usuario].[extensión]`. Al gatillar el comando de reinicio por texto "NO", la grilla de descargas completa es purgada físicamente de la memoria RAM del navegador.

### RF-06: Gestión de Flujo Conversacional y Pregunta de Control
* Posterior al despliegue de datos, el sistema entra en un estado booleano de persistencia controlado por la variable `esperando_continuacion`.
* Se presentará al usuario la pregunta explícita: *¿Desea consultar con otro nombre? Ingrese el nombre o escriba NO.*

### RF-07: Reinicio Limpio de Sesión (Reset Fijo de Interfaz)
* Si el sistema se encuentra en modo `esperando_continuacion` y el usuario ingresa las cadenas de escape `['no', 'n']` y presiona ENTER, el sistema ejecutará un **reinicio forzado de ciclo**.
* **Arquitectura de Estado:** La variable de control de la UI (`input_key`) debe incrementarse en una unidad antes del llamado a re-ejecución (`st.rerun()`), mutando la clave del widget de entrada de texto. Esto rompe la persistencia en caché del navegador, destruye los elementos del chat anterior y limpia la pantalla regresando al saludo inicial.
"""

arquitectura_content = """# Documento de Arquitectura de Software (SDD - Architecture & Lessons)
**Proyecto:** Sistema de Seguimiento Automatizado de Órdenes de Compra  
**Componente:** Diseño de Infraestructura, Flujos y Registro de Aprendizaje

---

## 1. Arquitectura de Tres Capas (POC Local)
El sistema está estructurado bajo un patrón desacoplado de tres capas lógicas operando en un entorno de ejecución síncrono local:
* **CAPA 1: PRESENTACIÓN (UI/UX):** Servidor Web Streamlit (Localhost). Renderizado de Markdown, tablas estructuradas, grilla horizontal de descargas de 3 columnas e inyección de JavaScript para control de enfoque del cursor.
* **CAPA 2: LÓGICA DE NEGOCIO (BACKEND):** Motor Python 3. Gestión de Estado de Sesión Dinámico (`st.session_state`), compilación binaria de documentos en memoria (`io.BytesIO`) y algoritmos de filtrado lógico vectorial.
* **CAPA 3: ALMACENAMIENTO (DATOS):** Archivo Plano Estructurado (`compras.xlsx`). Motor de lectura e indexación en memoria mediante el motor de Pandas.

## 2. Flujo de Datos y Diagrama de Secuencia Lógica
1. **Inicialización:** El usuario accede a la URL local ➡️ Se gatilla el script JS que otorga foco al cursor ➡️ `st.session_state` monta el saludo inicial.
2. **Entrada de Datos:** El usuario digita una cadena y presiona ENTER.
3. **Evaluación de Estado:**
   * **Si `esperando_continuacion == True` e `Input == "NO"`:** El sistema altera el puntero `input_key`, borra la lista de mensajes en memoria y ejecuta `st.rerun()`. La pantalla se blanquea de forma absoluta.
   * **Si `esperando_continuacion == False`:** Se invoca la función `buscar_ordenes(Input)`.
4. **Procesamiento de Datos:** Pandas carga el archivo `compras.xlsx`, aísla la columna `Solicitante` aplicando `.str.lower()` y extrae las filas que cumplan con la doble condicional (*Nombre coincidente* + *Estado válido*).
5. **Renderizado de Salida:** Se generan las tres variantes de exportación binaria independientes. Paralelamente, se formatea la columna `Monto` y se inyecta la columna de sellos gráficos (`✅` / `❓`) al final de la fila de datos en la UI.

## 3. Registro de Aprendizaje e Iteraciones Técnicas (Historial de la POC)
Durante el desarrollo iterativo de la POC se descubrieron restricciones críticas del framework que gobernaron el diseño final:
* **Lección 1 (Comportamiento de Cajas de Texto Nativas):** Los componentes estándar de chat de Streamlit bloquean los envíos vacíos. Se migró a un componente libre `st.text_input` acoplado a un motor de ejecución por orden cronológico.
* **Lección 2 (Persistencia en Caché de Formularios):** Las estructuras tipo formulario retienen de forma muy agresiva los datos en la memoria del navegador. Para forzar un borrado de pantalla idéntico a presionar F5, se diseñó un puntero incremental dinámico (`input_key`) que destruye y recrea la caja de texto en milisegundos tras una orden de salida.
* **Lección 3 (Tiempos de Ejecución del Rerun):** Colocar validaciones lógicas antes de renderizar componentes visuales previene fallos de tipo *KeyError* y desajustes cromáticos en la interfaz de usuario.

## 4. Plan de Migración e Infraestructura para Producción (Escalabilidad)
Para transformar esta POC en una solución empresarial distribuida para toda la compañía, la arquitectura debe migrar hacia el siguiente ecosistema en la nube:
* **Ecosistema de Cómputo:** Uso de Azure App Services o AWS ECS para alojar el contenedor Docker del Chatbot Web mediante canales seguros HTTPS / TLS 1.3.
* **Seguridad y Control de Identidad (SSO):** Se eliminará el ingreso manual de nombres para evitar la suplantación de identidad. El chatbot leerá directamente los atributos `user.displayName` y `user.mail` desde el token de autenticación corporativo de **Microsoft Entra ID** (antiguo Azure AD) del usuario conectado.
* **Conector OneDrive Real:** Se sustituirá el componente local por peticiones HTTP REST dirigidas a los endpoints de Microsoft Graph API (`https://microsoft.com`). Esto permitirá leer la planilla en tiempo real mientras el equipo de operaciones la edita, sin bloquear el archivo en la nube.
* **Tolerancia a Errores de Escritura:** Se implementará la librería de comparación difusa **`thefuzz`** (basada en la distancia de Levenshtein) para mitigar omisiones de tildes o errores tipográficos (ej: buscar "Juan Pérez" con o sin tilde).
"""

with open("specs.md", "w", encoding="utf-8") as f:
    f.write(specs_content.strip())
print("📥 'specs.md' consolidado con la grilla de 3 botones.")

with open("arquitectura.md", "w", encoding="utf-8") as f:
    f.write(arquitectura_content.strip())
print("📥 'arquitectura.md' consolidado con el Registro de Aprendizaje y plan OneDrive.")
