import pandas as pd
import os
import random

# 1. Listas base para generar combinaciones aleatorias realistas
nombres_pool = [
    "Juan Perez", "Maria Gomez", "Carlos Soto", "Ana Silva", "Luis Munoz",
    "Jose Contreras", "Rosa Diaz", "Jorge Morales", "Francisca Reyes", "Manuel Gutierrez",
    "Camila Henriquez", "Diego Sepulveda", "Felipe Poblete", "Valentina Vergara", "Sebastian Aravena"
]

estados_pool = ["Aprobada", "Pendiente", "Rechazada"]

# 2. Bucle automático para construir las 50 filas únicas
nuevas_ordenes = []
for i in range(50):
    solicitante = random.choice(nombres_pool)
    orden = f"OC-{3000 + i}"  # Genera folios desde OC-3000 hasta OC-3049
    monto = random.randint(15, 250) * 1000  # Genera montos múltiplos de mil (ej: 45.000, 120.000)
    estado = random.choice(estados_pool)
    
    nuevas_ordenes.append({
        "Solicitante": solicitante,
        "Orden": orden,
        "Monto": monto,
        "Estado": estado
    })

# Nombre del archivo Excel de la base de datos
archivo_excel = "compras.xlsx"

# 3. Lógica de acople con datos existentes
if os.path.exists(archivo_excel):
    print(f"📂 Encontré el archivo '{archivo_excel}'. Inyectando los 50 nuevos registros...")
    df_existente = pd.read_excel(archivo_excel)
    df_nuevos_datos = pd.DataFrame(nuevas_ordenes)
    df_final = pd.concat([df_existente, df_nuevos_datos], ignore_index=True)
else:
    print(f"✨ El archivo '{archivo_excel}' no existía. Generando base de datos con 50 registros...")
    df_final = pd.DataFrame(nuevas_ordenes)

# 4. Escritura final en la planilla Excel local
df_final.to_excel(archivo_excel, index=False)

print(f"✅ ¡Éxito! Se han inyectado {len(nuevas_ordenes)} filas aleatorias en '{archivo_excel}'.")
print(f"📊 Total de registros listos para la simulación: {len(df_final)}")
