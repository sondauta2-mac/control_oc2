# -*- coding: utf-8 -*-
"""Script de actualización final para consolidar la lógica de encadenamiento en specs.md"""

specs_content = """# Documento de Especificación de Requerimientos (Specs - Final POC)
**Proyecto:** Sistema de Seguimiento Automatizado de Órdenes de Compra (Seguimiento OC)  
**Estado:** Prueba de Concepto (POC) Validada con Matriz Multi-Formato y Consultas Encadenadas  
**Enfoque de Diseño:** Tradicional Basado en Reglas (Determinista)

---

## 1. Requerimientos Funcionales (RF)

### RF-01: Identificación y Entrada de Usuario
* El sistema debe solicitar el nombre completo del usuario solicitante mediante un campo de entrada de texto plano (`st.text_input`).
* **UX Fina:** El cursor de escritura debe posicionarse automáticamente (*foco de interfaz*) dentro de la casilla de texto tanto en el inicio del software como tras cada reinicio de sesión o nueva consulta, sin requerir clics manuales del ratón.

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

### RF-06: Gestión de Flujo Conversacional y Consultas Encadenadas
* Posterior al despliegue de datos, el sistema entra en un estado booleano de persistencia controlado por la variable `esperando_continuacion`.
* Se presentará al usuario la pregunta explícita: *¿Desea consultar con otro nombre? Ingrese el nombre o escriba NO.*
* **Lógica de Encadenamiento Continuo:** Si el sistema está en modo `esperando_continuacion == True` y el usuario ingresa un **nuevo nombre** en lugar de una señal de escape, el software debe apagar de forma automática la bandera de espera, procesar el nuevo nombre de manera descendente en el chat y acumular la nueva tabla con su respectiva grilla de tres botones en el historial, garantizando la fluidez de la sesión.

### RF-07: Reinicio Limpio de Sesión (Reset Fijo de Interfaz)
* Si el sistema se encuentra en modo `esperando_continuacion` y el usuario ingresa las cadenas de escape `['no', 'n']` y presiona ENTER, el sistema ejecutará un **reinicio forzado de ciclo**.
* **Arquitectura de Estado:** La variable de control de la UI (`input_key`) debe incrementarse en una unidad antes del llamado a re-ejecución (`st.rerun()`), mutando la clave del widget de entrada de texto. Esto rompe la persistencia en caché del navegador, destruye los elementos del chat anterior y limpia la pantalla regresando al saludo inicial.
"""

with open("specs.md", "w", encoding="utf-8") as f:
    f.write(specs_content.strip())
print("📥 'specs.md' actualizado con éxito con la regla final de consultas encadenadas.")
