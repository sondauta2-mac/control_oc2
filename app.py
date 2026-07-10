import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. Configuración de la página y título
st.set_page_config(page_title="Seguimiento OC", page_icon="🛍️")
st.title("🤖 Seguimiento OC")
st.write("Consulta el estado de tus solicitudes de compra de forma inmediata.")

# Función para leer y filtrar el archivo Excel local
def buscar_ordenes(nombre_usuario):
    try:
        df = pd.read_excel('compras.xlsx')
        df['Solicitante'] = df['Solicitante'].astype(str).str.strip()
        df['Estado'] = df['Estado'].astype(str).str.strip()
        
        # Filtra por nombre (ignora mayúsculas/minúsculas)
        resultado = df[df['Solicitante'].str.lower() == nombre_usuario.lower()]
        # Filtra solo los estados requeridos (Aprobada o Pendiente)
        resultado = resultado[resultado['Estado'].isin(['Aprobada', 'Pendiente'])]
        return resultado
    except FileNotFoundError:
        st.error("Error: No se encontró el archivo 'compras.xlsx' en la carpeta.")
        return None

# 2. Inicializar variables de estado esenciales en la sesión si no existen
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "type": "text", "content": "¡Hola! Por favor, ingresa tu nombre completo para revisar tus órdenes de compra."}
    ]
if "esperando_continuacion" not in st.session_state:
    st.session_state.esperando_continuacion = False
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# 3. MUESTRA VISUAL: Dibujar el historial acumulado en la pantalla de forma ordenada
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "table":
            st.dataframe(message["content"], use_container_width=True, hide_index=True)
        elif message["type"] == "download_btn":
            st.download_button(
                label="📥 Descargar estas órdenes en CSV",
                data=message["content"],
                file_name=message["file_name"],
                mime='text/csv',
                key=message["key"]
            )
        else:
            st.markdown(message["content"])

# 4. COMPONENTE VISUAL: Entrada de texto libre (se ejecuta al dar ENTER)
prompt = st.text_input(
    "Escribe tu respuesta aquí y presiona ENTER:", 
    key=f"user_prompt_{st.session_state.input_key}"
)

# 5. LÓGICA DE PROCESAMIENTO: Se ejecuta estrictamente después de que la interfaz existe
if prompt:
    entrada_limpia = prompt.strip().lower()
    
    # CASO A: Si el bot esperaba confirmación y el usuario escribe "NO" o "N" -> REINICIO TOTAL
    if st.session_state.esperando_continuacion and entrada_limpia in ['no', 'n']:
        st.session_state.messages = [
            {"role": "assistant", "type": "text", "content": "¡Hola! Por favor, ingresa tu nombre completo para revisar tus órdenes de compra."}
        ]
        st.session_state.esperando_continuacion = False
        st.session_state.input_key += 1
        st.rerun()

    # CASO B: Procesar la búsqueda del nombre en el Excel (solo si no es un comando de salida)
    elif not st.session_state.esperando_continuacion and prompt.strip() != "":
        # Guardamos lo que escribió el usuario en el historial
        st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
        
        datos = buscar_ordenes(prompt)
        
        if datos is not None:
            if datos.empty:
                respuesta = f"No encontré órdenes pendientes o aprobadas para el usuario **{prompt}**."
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": respuesta})
            else:
                saludo = f"Hola **{prompt}**, encontré las siguientes órdenes asociadas a tu nombre:"
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": saludo})
                
                # Construcción de la tabla estructurada
                tabla_vista = datos[['Orden', 'Monto', 'Estado']].copy()
                tabla_vista[' '] = tabla_vista['Estado'].apply(lambda x: '✅' if x == 'Aprobada' else '❓')
                tabla_vista = tabla_vista[['Orden', 'Monto', 'Estado', ' ']]
                
                # CSV de descarga optimizado para Excel en español (punto y coma + utf-8-sig)
                csv_datos = tabla_vista[['Orden', 'Monto', 'Estado']].to_csv(index=False, sep=';').encode('utf-8-sig')
                nombre_archivo_csv = f"ordenes_{prompt.replace(' ', '_')}.csv"
                
                # Formatear el dinero para la vista de la página web
                tabla_vista['Monto'] = tabla_vista['Monto'].apply(lambda x: f"${int(x):,}".replace(",", "."))
                
                # Guardar la tabla en el historial
                st.session_state.messages.append({"role": "assistant", "type": "table", "content": tabla_vista})
                
                # Guardar el botón de descarga en el historial
                key_dinamica = f"btn_{len(st.session_state.messages)}"
                st.session_state.messages.append({
                    "role": "assistant", 
                    "type": "download_btn", 
                    "content": csv_datos, 
                    "file_name": nombre_archivo_csv,
                    "key": key_dinamica
                })
            
            # Pregunta de control final
            pregunta_siguiente = "¿Desea consultar con otro nombre? Ingrese el nombre o escriba **NO**."
            st.session_state.messages.append({"role": "assistant", "type": "text", "content": pregunta_siguiente})
            st.session_state.esperando_continuacion = True
            st.session_state.input_key += 1
            st.rerun()

# 6. Inyección de JavaScript para forzar el foco automático del cursor en la caja de texto
components.html(
    f"""
    <script>
        var input = window.parent.document.querySelector('input[aria-label="Escribe tu respuesta aquí y presiona ENTER:"]');
        if (input) {{
            input.focus();
        }}
    </script>
    """,
    height=0,
    width=0,
)
