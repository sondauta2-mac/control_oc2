import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

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
        
        resultado = df[df['Solicitante'].str.lower() == nombre_usuario.lower()]
        resultado = resultado[resultado['Estado'].isin(['Aprobada', 'Pendiente'])]
        return resultado
    except FileNotFoundError:
        st.error("Error: No se encontró el archivo 'compras.xlsx' en la carpeta.")
        return None

# Función auxiliar para construir el reporte PDF de forma dinámica
def generar_pdf(df_datos, nombre_usuario):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, spaceAfter=15, textColor=colors.HexColor("#1E3A8A"))
    text_style = ParagraphStyle('TextStyle', parent=styles['Normal'], fontSize=11, spaceAfter=12)
    
    story.append(Paragraph("<b>Reporte de Seguimiento - Órdenes de Compra</b>", title_style))
    story.append(Paragraph(f"<b>Solicitante Consultado:</b> {nombre_usuario}", text_style))
    story.append(Spacer(1, 10))
    
    tabla_data = [["Orden", "Monto", "Estado"]]
    for _, fila in df_datos.iterrows():
        monto_str = f"${int(fila['Monto']):,}".replace(",", ".")
        tabla_data.append([str(fila['Orden']), monto_str, str(fila['Estado'])])
    
    t = Table(tabla_data, colWidths=[120, 150, 120])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F3F4F6")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D1D5DB")),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ]))
    
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# 2. Inicializar variables de estado esenciales si no existen
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
        elif message["type"] == "export_block":
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(label="📥 Descargar CSV", data=message["csv_data"], file_name=message["csv_name"], mime='text/csv', key=f"csv_{message['key']}")
            with col2:
                st.download_button(label="📊 Descargar Excel", data=message["xlsx_data"], file_name=message["xlsx_name"], mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', key=f"xlsx_{message['key']}")
            with col3:
                st.download_button(label="📄 Descargar PDF", data=message["pdf_data"], file_name=message["pdf_name"], mime='application/pdf', key=f"pdf_{message['key']}")
        else:
            st.markdown(message["content"])

# 4. COMPONENTE VISUAL: Entrada de texto libre (se ejecuta al dar ENTER)
prompt = st.text_input(
    "Escribe tu respuesta aquí y presiona ENTER:", 
    key=f"user_prompt_{st.session_state.input_key}"
)

# 5. LÓGICA DE PROCESAMIENTO (CORREGIDA): Se ejecuta tras la interacción
if prompt:
    entrada_limpia = prompt.strip().lower()
    
    # CONTROL DE ESCAPE: Si el usuario escribe "NO" o "N" -> REINICIO TOTAL
    if st.session_state.esperando_continuacion and entrada_limpia in ['no', 'n']:
        st.session_state.messages = [
            {"role": "assistant", "type": "text", "content": "¡Hola! Por favor, ingresa tu nombre completo para revisar tus órdenes de compra."}
        ]
        st.session_state.esperando_continuacion = False
        st.session_state.input_key += 1
        st.rerun()

    # CONTROL DE CONTINUACIÓN: Si escribe un nombre nuevo, apagamos la espera y procesamos
    elif prompt.strip() != "":
        if st.session_state.esperando_continuacion:
            st.session_state.esperando_continuacion = False

        st.session_state.messages.append({"role": "user", "type": "text", "content": prompt})
        datos = buscar_ordenes(prompt)
        
        if datos is not None:
            if datos.empty:
                respuesta = f"No encontré órdenes pendientes o aprobadas para el usuario **{prompt}**."
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": respuesta})
            else:
                saludo = f"Hola **{prompt}**, encontré las siguientes órdenes asociadas a tu nombre:"
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": saludo})
                
                tabla_vista = datos[['Orden', 'Monto', 'Estado']].copy()
                tabla_vista[' '] = tabla_vista['Estado'].apply(lambda x: '✅' if x == 'Aprobada' else '❓')
                tabla_vista = tabla_vista[['Orden', 'Monto', 'Estado', ' ']]
                
                # Compilar los 3 formatos binarios
                csv_bytes = tabla_vista[['Orden', 'Monto', 'Estado']].to_csv(index=False, sep=';').encode('utf-8-sig')
                
                xlsx_buffer = io.BytesIO()
                with pd.ExcelWriter(xlsx_buffer, engine='openpyxl') as writer:
                    tabla_vista[['Orden', 'Monto', 'Estado']].to_excel(writer, index=False, sheet_name='Ordenes')
                xlsx_bytes = xlsx_buffer.getvalue()
                
                pdf_bytes = generar_pdf(tabla_vista[['Orden', 'Monto', 'Estado']], prompt)
                
                nombre_base = prompt.replace(' ', '_')
                
                # Guardar tabla y bloque de botones en el historial
                st.session_state.messages.append({"role": "assistant", "type": "table", "content": tabla_vista})
                
                key_dinamica = f"block_{len(st.session_state.messages)}"
                st.session_state.messages.append({
                    "role": "assistant", 
                    "type": "export_block", 
                    "csv_data": csv_bytes, "csv_name": f"ordenes_{nombre_base}.csv",
                    "xlsx_data": xlsx_bytes, "xlsx_name": f"ordenes_{nombre_base}.xlsx",
                    "pdf_data": pdf_bytes, "pdf_name": f"ordenes_{nombre_base}.pdf",
                    "key": key_dinamica
                })
            
            # Pregunta de control final
            pregunta_siguiente = "¿Desea consultar con otro nombre? Ingrese el nombre o escriba **NO**."
            st.session_state.messages.append({"role": "assistant", "type": "text", "content": pregunta_siguiente})
            st.session_state.esperando_continuacion = True
            st.session_state.input_key += 1
            st.rerun()

# 6. Inyección de JavaScript para foco automático
components.html(
    f'''<script>
        var input = window.parent.document.querySelector('input[aria-label="Escribe tu respuesta aquí y presiona ENTER:"]');
        if (input) {{ input.focus(); }}
    </script>''', height=0, width=0
)
