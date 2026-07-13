# Documento de Arquitectura de Software (SDD - Architecture & Lessons)
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