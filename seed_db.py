import argparse
import json
import os
import random
import re
import time
import unicodedata
from datetime import datetime, timedelta

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pymongo import MongoClient
from pymongo.errors import BulkWriteError, ServerSelectionTimeoutError

# ============================================================
# HOSPITAL ARTORIA - DATABASE SEEDER
# ============================================================

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "hospital_artoria")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not MONGO_URI:
    raise ValueError("❌ Falta MONGO_URI en el archivo .env")

if not GEMINI_API_KEY:
    raise ValueError("❌ Falta GEMINI_API_KEY en el archivo .env")


# ============================================================
# GEMINI SETUP
# ============================================================

client = genai.Client(api_key=GEMINI_API_KEY)

# Modelos recomendados y disponibles
MODELOS_GEMINI = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]


# ============================================================
# MONGODB
# ============================================================

print("Conectando a MongoDB...")

try:
    mongo_client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000,
    )
    mongo_client.admin.command("ping")
    db = mongo_client[DATABASE_NAME]
    print("✅ MongoDB conectado correctamente.")
except ServerSelectionTimeoutError as e:
    print("❌ No se pudo conectar a MongoDB.")
    print(e)
    raise
except Exception as e:
    print(f"❌ Error conectando a MongoDB: {e}")
    raise


# ============================================================
# CANTIDADES
# ============================================================

CANTIDADES = {
    "pacientes": 50,
    "medicos": 10,
    "citas": 100,
    "consultas": 80,
    "diagnosticos": 70,
    "tratamientos": 60,
    "hospitalizaciones": 30,
    "pagos": 90,
    "usuarios": 4,
}


# ============================================================
# UTILIDADES
# ============================================================

def limpiar_texto(texto):
    if texto is None:
        return ""
    texto = str(texto)
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto


def texto_para_email(texto):
    texto = limpiar_texto(texto).lower()
    texto = re.sub(r"[^a-z0-9]+", "", texto)
    return texto or "usuario"


def generar_email_unico(nombre, apellido, usados=None):
    if usados is None:
        usados = set()

    nombre = texto_para_email(nombre)
    apellido = texto_para_email(apellido)

    base = f"{nombre}.{apellido}"
    email = f"{base}@email.com"
    contador = 1

    while email in usados:
        email = f"{base}{contador}@email.com"
        contador += 1

    usados.add(email)
    return email


def limpiar_respuesta_json(texto):
    if not texto:
        return ""
    texto = str(texto).strip()
    if texto.startswith("```json"):
        texto = texto[7:]
    elif texto.startswith("```"):
        texto = texto[3:]
    if texto.endswith("```"):
        texto = texto[:-3]
    return texto.strip()


def asegurar_lista(datos):
    if isinstance(datos, list):
        return datos

    if isinstance(datos, dict):
        for clave in ("items", "data", "results", "records"):
            valor = datos.get(clave)
            if isinstance(valor, list):
                return valor

        for valor in datos.values():
            if isinstance(valor, list):
                return valor

    return []


def normalizar_documento(documento):
    if not isinstance(documento, dict):
        return {}
    return {k: v for k, v in documento.items() if k not in {"_id", "id"}}


# ============================================================
# GEMINI GENERATION
# ============================================================

def generar_con_gemini(prompt, cantidad, intentos=2):
    for modelo in MODELOS_GEMINI:
        for intento in range(1, intentos + 1):
            try:
                print(f"🤖 Intentando Gemini: {modelo} (intento {intento})...")

                response = client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.7,
                    ),
                )

                texto = response.text
                if not texto:
                    raise ValueError("Gemini devolvió una respuesta vacía.")

                texto = limpiar_respuesta_json(texto)
                datos = json.loads(texto)
                datos = asegurar_lista(datos)

                if not datos:
                    raise ValueError("Gemini devolvió una lista vacía.")

                datos = [
                    normalizar_documento(item)
                    for item in datos
                    if isinstance(item, dict)
                ]
                datos = [item for item in datos if item]

                if not datos:
                    raise ValueError("Gemini no devolvió documentos válidos.")

                print(f"✅ Gemini funcionó con {modelo}.")
                if len(datos) < cantidad:
                    print(
                        f"⚠️ Gemini devolvió {len(datos)} de {cantidad} registros solicitados."
                    )

                # Pausa para respetar el Rate Limit (Free Tier ~5-15 RPM)
                time.sleep(4)
                return datos

            except Exception as e:
                mensaje = str(e)
                print(f"⚠️ Error con modelo {modelo} (intento {intento}): {mensaje}")

                if "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
                    print("⏳ Rate limit alcanzado. Esperando 10 segundos antes de reintentar...")
                    time.sleep(10)
                elif "404" in mensaje or "NOT_FOUND" in mensaje:
                    break

    print("❌ Todos los modelos de Gemini fallaron.")
    print("➡️ Usando datos de respaldo.")
    return None


# ============================================================
# DATOS DE RESPALDO - PACIENTES
# ============================================================

def generar_pacientes_respaldo(cantidad=50):
    nombres = [
        "Juan", "María", "Carlos", "Ana", "Luis",
        "Laura", "Pedro", "Sofía", "Diego", "Valentina",
        "Andrés", "Camila", "Javier", "Isabella", "Miguel",
        "Lucas", "Mateo", "Emma", "Gabriel", "Daniela",
    ]

    apellidos = [
        "Pérez", "González", "Ramírez", "Martínez", "López",
        "Hernández", "García", "Flores", "Morales", "Ortiz",
        "Cruz", "Reyes", "Gómez", "Díaz", "Vázquez",
        "Jiménez", "Mendoza", "Guerrero", "Sandoval", "Romero",
    ]

    tipos_sangre = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    pacientes = []
    emails_usados = set()

    for _ in range(cantidad):
        nombre = random.choice(nombres)
        apellido1 = random.choice(apellidos)
        apellido2 = random.choice(apellidos)
        fecha_nacimiento = datetime.now() - timedelta(
            days=random.randint(365 * 18, 365 * 80)
        )

        pacientes.append({
            "nombre": nombre,
            "apellidos": f"{apellido1} {apellido2}",
            "fecha_nacimiento": fecha_nacimiento.strftime("%Y-%m-%d"),
            "genero": random.choice(["M", "F"]),
            "telefono": f"55-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            "email": generar_email_unico(nombre, apellido1, emails_usados),
            "direccion": f"Calle {random.randint(1, 100)} #{random.randint(100, 999)}",
            "tipo_sangre": random.choice(tipos_sangre),
            "alergias": (
                None
                if random.random() < 0.7
                else random.choice(["Penicilina", "Polen", "Lácteos", "Gluten"])
            ),
            "antecedentes": (
                None
                if random.random() < 0.8
                else random.choice([
                    "Hipertensión",
                    "Diabetes",
                    "Hipertensión y Diabetes",
                ])
            ),
        })

    return pacientes


# ============================================================
# DATOS DE RESPALDO - MÉDICOS
# ============================================================

def generar_medicos_respaldo(cantidad=10):
    especialidades = [
        "Cardiología", "Pediatría", "Medicina Interna", "Dermatología",
        "Neurología", "Ginecología", "Ortopedia", "Oftalmología",
    ]
    nombres = ["Carlos", "Ana", "Jorge", "Lucía", "Roberto", "Patricia", "Fernando", "Mónica"]
    apellidos = ["Ramírez", "Martínez", "López", "García", "Pérez", "Díaz", "Gómez", "Hernández"]

    medicos = []
    for i in range(cantidad):
        nombre = nombres[i % len(nombres)]
        apellido = apellidos[i % len(apellidos)]

        medicos.append({
            "nombre": nombre,
            "apellidos": f"{apellido} {random.choice(apellidos)}",
            "cedula": random.randint(10000000, 99999999),
            "especialidad": random.choice(especialidades),
            "telefono": f"55-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            "email": f"medico{i + 1}_{random.randint(100,999)}@hospital.com",
            "estado": random.choice(["Activo", "Inactivo"]),
            "horarios": {
                "lunes": "08:00-16:00",
                "martes": "08:00-16:00",
                "miércoles": "09:00-17:00",
                "jueves": "08:00-16:00",
                "viernes": "08:00-14:00",
            },
        })

    return medicos


# ============================================================
# DATOS DE RESPALDO - CITAS
# ============================================================

def generar_citas_respaldo(cantidad, pacientes_ids, medicos_ids):
    estados = ["Programada", "Confirmada", "Atendida", "Cancelada", "No asistió"]
    motivos = [
        "Dolor de cabeza", "Revisión general", "Seguimiento",
        "Consulta de rutina", "Dolor abdominal", "Fiebre",
        "Dolor muscular", "Control médico",
    ]
    especialidades = [
        "Cardiología", "Pediatría", "Medicina Interna", "Dermatología",
        "Neurología", "Ginecología", "Ortopedia", "Oftalmología",
    ]

    citas = []
    for _ in range(cantidad):
        fecha = datetime.now() + timedelta(days=random.randint(-90, 30))
        citas.append({
            "paciente_id": random.choice(pacientes_ids),
            "medico_id": random.choice(medicos_ids),
            "fecha": fecha.isoformat(),
            "motivo": random.choice(motivos),
            "estado": random.choice(estados),
            "especialidad": random.choice(especialidades),
            "fecha_creacion": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
        })

    return citas


# ============================================================
# DATOS DE RESPALDO - CONSULTAS
# ============================================================

def generar_consultas_respaldo(cantidad, pacientes_ids, medicos_ids, citas_ids):
    motivos = ["Dolor de cabeza", "Revisión anual", "Seguimiento de tratamiento", "Consulta general", "Dolor abdominal", "Control médico"]
    sintomas = ["Dolor persistente", "Fiebre", "Náuseas", "Mareos", "Fatiga", "Dolor muscular"]
    diagnosticos = ["Hipertensión", "Infección", "Diabetes tipo 2", "Migraña", "Gastritis", "Influenza", "Dermatitis"]
    tratamientos = ["Paracetamol", "Ibuprofeno", "Reposo", "Hidratación", "Tratamiento médico"]
    especialidades = ["Medicina General", "Cardiología", "Pediatría", "Dermatología", "Neurología"]

    consultas = []
    for _ in range(cantidad):
        consultas.append({
            "paciente_id": random.choice(pacientes_ids),
            "medico_id": random.choice(medicos_ids),
            "fecha": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
            "motivo": random.choice(motivos),
            "sintomas": random.choice(sintomas),
            "observaciones": random.choice([
                "Paciente estable",
                "Paciente requiere seguimiento",
                "Sin complicaciones",
                "Se recomienda revisión",
            ]),
            "diagnostico": random.choice(diagnosticos),
            "tratamiento": random.choice(tratamientos),
            "costo": round(random.uniform(300, 5000), 2),
            "especialidad": random.choice(especialidades),
            "cita_id": (
                random.choice(citas_ids)
                if citas_ids and random.random() > 0.5
                else None
            ),
        })

    return consultas


# ============================================================
# DIAGNÓSTICOS, TRATAMIENTOS, HOSPITALIZACIONES, PAGOS
# ============================================================

def generar_diagnosticos(cantidad, pacientes_ids, medicos_ids, consultas_ids):
    enfermedades = ["Hipertensión", "Diabetes", "Infección respiratoria", "Fractura", "Dermatitis", "Migraña", "Ansiedad", "Gastritis", "Influenza", "Neumonía"]
    diagnosticos = []
    for _ in range(cantidad):
        diagnosticos.append({
            "paciente_id": random.choice(pacientes_ids),
            "medico_id": random.choice(medicos_ids),
            "enfermedad": random.choice(enfermedades),
            "codigo": f"{random.choice(['A', 'B', 'C'])}{random.randint(10, 99)}.{random.randint(0, 9)}",
            "descripcion": random.choice(["Diagnóstico general", "Diagnóstico confirmado", "Diagnóstico sujeto a seguimiento", "Diagnóstico de control"]),
            "fecha": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
            "consulta_id": (random.choice(consultas_ids) if consultas_ids and random.random() > 0.3 else None),
        })
    return diagnosticos


def generar_tratamientos(cantidad, consultas_ids):
    medicamentos = ["Paracetamol", "Ibuprofeno", "Amoxicilina", "Loratadina", "Omeprazol", "Losartán", "Metformina"]
    tratamientos = []
    for _ in range(cantidad):
        medicamentos_seleccionados = random.sample(medicamentos, k=2)
        tratamientos.append({
            "consulta_id": random.choice(consultas_ids),
            "tratamiento": medicamentos_seleccionados[0],
            "medicamentos": medicamentos_seleccionados,
            "dosis": random.choice(["1 c/12h", "1 c/8h", "2 c/día", "1 c/día"]),
            "frecuencia": random.choice(["Diario", "Cada 12 horas", "Cada 8 horas"]),
            "duracion": random.randint(3, 30),
            "indicaciones": random.choice(["Tomar con alimentos", "Tomar después de comer", "Tomar con abundante agua", "Seguir indicaciones médicas"]),
        })
    return tratamientos


def generar_hospitalizaciones(cantidad, pacientes_ids, medicos_ids):
    motivos = ["Ingreso programado", "Urgencia médica", "Observación", "Cirugía programada", "Complicación médica"]
    diagnosticos = ["Neumonía", "Fractura", "Apendicitis", "Infección", "Diabetes descompensada", "Hipertensión"]
    hospitalizaciones = []

    for _ in range(cantidad):
        ingreso = datetime.now() - timedelta(days=random.randint(1, 90))
        alta = ingreso + timedelta(days=random.randint(1, 15)) if random.random() > 0.3 else None
        hospitalizaciones.append({
            "paciente_id": random.choice(pacientes_ids),
            "medico_id": random.choice(medicos_ids),
            "fecha_ingreso": ingreso.isoformat(),
            "fecha_alta": alta.isoformat() if alta else None,
            "habitacion": random.randint(100, 150),
            "cama": random.randint(1, 10),
            "motivo": random.choice(motivos),
            "diagnostico": random.choice(diagnosticos),
            "estado": ("Activa" if alta is None else random.choice(["Alta", "En observación"])),
            "costo_estimado": round(random.uniform(5000, 50000), 2),
        })
    return hospitalizaciones


def generar_pagos(cantidad, consultas_ids, pacientes_ids):
    pagos = []
    for _ in range(cantidad):
        pagos.append({
            "consulta_id": random.choice(consultas_ids),
            "paciente_id": random.choice(pacientes_ids),
            "monto": round(random.uniform(300, 5000), 2),
            "fecha": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
            "metodo": random.choice(["Efectivo", "Tarjeta", "Transferencia"]),
            "estado": random.choice(["Pagado", "Pendiente"]),
        })
    return pagos


def generar_usuarios():
    from werkzeug.security import generate_password_hash

    return [
        {
            "username": "admin",
            "password": generate_password_hash("admin123"),
            "nombre": "Administrador",
            "apellidos": "Sistema",
            "email": "admin@hospital.com",
            "rol": "admin",
            "foto_perfil": None,
        },
        {
            "username": "medico1",
            "password": generate_password_hash("medico123"),
            "nombre": "Carlos",
            "apellidos": "Ramírez",
            "email": "carlos@hospital.com",
            "rol": "medico",
            "foto_perfil": None,
        },
        {
            "username": "recepcion",
            "password": generate_password_hash("recep123"),
            "nombre": "Laura",
            "apellidos": "García",
            "email": "laura@hospital.com",
            "rol": "recepcionista",
            "foto_perfil": None,
        },
        {
            "username": "enfermeria",
            "password": generate_password_hash("enfer123"),
            "nombre": "Ana",
            "apellidos": "Martínez",
            "email": "ana@hospital.com",
            "rol": "enfermeria",
            "foto_perfil": None,
        },
    ]


# ============================================================
# DB OPERATIONS
# ============================================================

def insertar_documentos(coleccion, documentos, nombre):
    if not documentos:
        print(f"⚠️ No hay {nombre} para insertar.")
        return []

    try:
        resultado = coleccion.insert_many(documentos, ordered=False)
        ids = resultado.inserted_ids
        print(f"✅ Insertados {len(ids)} {nombre}.")
        return ids
    except BulkWriteError as e:
        detalles = e.details or {}
        insertados = detalles.get("nInserted", 0)
        errores = detalles.get("writeErrors", [])
        print(f"⚠️ Se insertaron {insertados} {nombre}, pero {len(errores)} documentos fueron rechazados.")
        return [doc["_id"] for doc in documentos if "_id" in doc]


def upsert_por_campo(coleccion, documentos, campo, nombre):
    ids = []
    for documento in documentos:
        valor = documento.get(campo)
        if not valor:
            continue

        try:
            resultado = coleccion.update_one(
                {campo: valor},
                {"$set": documento},
                upsert=True,
            )
            if resultado.upserted_id:
                ids.append(resultado.upserted_id)
            else:
                existente = coleccion.find_one({campo: valor}, {"_id": 1})
                if existente:
                    ids.append(existente["_id"])
        except Exception as e:
            print(f"⚠️ Error procesando {nombre} {campo}={valor}: {e}")

    print(f"✅ Procesados {len(ids)} {nombre} mediante upsert.")
    return ids


def corregir_emails_pacientes(pacientes):
    usados = set()
    corregidos = []
    for paciente in pacientes:
        nombre = paciente.get("nombre", "Paciente")
        apellidos = paciente.get("apellidos", "Hospital")
        email = paciente.get("email")

        if not email or email in usados:
            apellido = str(apellidos).split()[0] if apellidos else "hospital"
            email = generar_email_unico(nombre, apellido, usados)
        else:
            usados.add(email)

        paciente["email"] = email
        corregidos.append(paciente)
    return corregidos


def corregir_emails_medicos(medicos):
    usados = set()
    corregidos = []
    for i, medico in enumerate(medicos):
        nombre = medico.get("nombre", f"medico{i + 1}")
        apellidos = medico.get("apellidos", "Hospital")
        email = medico.get("email")

        if not email or email in usados:
            apellido = str(apellidos).split()[0] if apellidos else f"medico{i + 1}"
            email = generar_email_unico(nombre, apellido, usados)
        else:
            usados.add(email)

        medico["email"] = email
        corregidos.append(medico)
    return corregidos


# ============================================================
# PROMPTS
# ============================================================

def generar_pacientes_prompt(cantidad):
    return f"""
Genera exactamente {min(cantidad, 20)} pacientes ficticios para Hospital Artoria en formato JSON.
Formato de salida esperado:
[
  {{
    "nombre": "Juan",
    "apellidos": "Pérez García",
    "fecha_nacimiento": "1990-05-15",
    "genero": "M",
    "telefono": "55-1234-5678",
    "email": "juan.perez@email.com",
    "direccion": "Calle 10 #123",
    "tipo_sangre": "O+",
    "alergias": null,
    "antecedentes": null
  }}
]
"""


def generar_medicos_prompt(cantidad):
    return f"""
Genera exactamente {min(cantidad, 10)} médicos ficticios para Hospital Artoria en formato JSON.
Especialidades válidas: Cardiología, Pediatría, Medicina Interna, Dermatología, Neurología, Ginecología, Ortopedia, Oftalmología.
Formato de salida esperado:
[
  {{
    "nombre": "Carlos",
    "apellidos": "Ramírez López",
    "cedula": 12345678,
    "especialidad": "Cardiología",
    "telefono": "55-1234-5678",
    "email": "carlos.ramirez@email.com",
    "estado": "Activo",
    "horarios": {{
      "lunes": "08:00-16:00",
      "martes": "08:00-16:00"
    }}
  }}
]
"""


def generar_citas_prompt(cantidad):
    return f"""
Genera exactamente {min(cantidad, 20)} citas médicas en formato JSON.
Estados válidos: Programada, Confirmada, Atendida, Cancelada, No asistió.
Formato de salida esperado:
[
  {{
    "paciente_id": null,
    "medico_id": null,
    "fecha": "2026-08-15T10:00:00",
    "motivo": "Revisión general",
    "estado": "Programada",
    "especialidad": "Medicina Interna",
    "fecha_creacion": "2026-08-01T10:00:00"
  }}
]
"""


def generar_consultas_prompt(cantidad):
    return f"""
Genera exactamente {min(cantidad, 20)} consultas médicas en formato JSON.
Formato de salida esperado:
[
  {{
    "paciente_id": null,
    "medico_id": null,
    "fecha": "2026-08-01T10:00:00",
    "motivo": "Consulta general",
    "sintomas": "Fiebre y tos",
    "observaciones": "Paciente estable",
    "diagnostico": "Influenza",
    "tratamiento": "Reposo",
    "costo": 800.50,
    "especialidad": "Medicina General",
    "cita_id": null
  }}
]
"""


# ============================================================
# SEED PRINCIPAL
# ============================================================

def seed_database(limpiar=False):
    print()
    print("=" * 60)
    print("🏥 HOSPITAL ARTORIA")
    print("🌱 DATABASE SEEDING")
    print("=" * 60)
    print()

    if limpiar:
        print("🧹 Eliminando datos existentes...")
        for coleccion in db.list_collection_names():
            db[coleccion].delete_many({})
        print("✅ Datos eliminados.\n")

    # 1. PACIENTES
    print("👤 Generando pacientes con Gemini...")
    pacientes_data = generar_con_gemini(
        generar_pacientes_prompt(CANTIDADES["pacientes"]),
        CANTIDADES["pacientes"],
    )

    if pacientes_data:
        pacientes_data = corregir_emails_pacientes(pacientes_data)
        faltantes = CANTIDADES["pacientes"] - len(pacientes_data)
        if faltantes > 0:
            print(f"➡️ Completando {faltantes} pacientes con respaldo...")
            pacientes_data.extend(generar_pacientes_respaldo(faltantes))
        pacientes_ids = upsert_por_campo(db.pacientes, pacientes_data, "email", "pacientes")
    else:
        print("➡️ Usando datos de respaldo para pacientes...")
        pacientes_ids = upsert_por_campo(
            db.pacientes,
            generar_pacientes_respaldo(CANTIDADES["pacientes"]),
            "email",
            "pacientes de respaldo",
        )

    # 2. MÉDICOS
    print("\n👨‍⚕️ Generando médicos con Gemini...")
    medicos_data = generar_con_gemini(
        generar_medicos_prompt(CANTIDADES["medicos"]),
        CANTIDADES["medicos"],
    )

    if medicos_data:
        medicos_data = corregir_emails_medicos(medicos_data)
        faltantes = CANTIDADES["medicos"] - len(medicos_data)
        if faltantes > 0:
            medicos_data.extend(generar_medicos_respaldo(faltantes))
        medicos_ids = upsert_por_campo(db.medicos, medicos_data, "email", "médicos")
    else:
        print("➡️ Usando datos de respaldo para médicos...")
        medicos_ids = upsert_por_campo(
            db.medicos,
            generar_medicos_respaldo(CANTIDADES["medicos"]),
            "email",
            "médicos de respaldo",
        )

    # 3. CITAS
    citas_ids = []
    if pacientes_ids and medicos_ids:
        print("\n📅 Generando citas...")
        citas_data = generar_con_gemini(
            generar_citas_prompt(CANTIDADES["citas"]),
            CANTIDADES["citas"],
        )

        if citas_data:
            for cita in citas_data:
                cita["paciente_id"] = random.choice(pacientes_ids)
                cita["medico_id"] = random.choice(medicos_ids)

            faltantes = CANTIDADES["citas"] - len(citas_data)
            if faltantes > 0:
                citas_data.extend(
                    generar_citas_respaldo(faltantes, pacientes_ids, medicos_ids)
                )
            citas_ids = insertar_documentos(db.citas, citas_data, "citas")
        else:
            print("➡️ Usando datos de respaldo para citas...")
            citas_ids = insertar_documentos(
                db.citas,
                generar_citas_respaldo(CANTIDADES["citas"], pacientes_ids, medicos_ids),
                "citas de respaldo",
            )

    # 4. CONSULTAS
    consultas_ids = []
    if pacientes_ids and medicos_ids:
        print("\n🩺 Generando consultas...")
        consultas_data = generar_con_gemini(
            generar_consultas_prompt(CANTIDADES["consultas"]),
            CANTIDADES["consultas"],
        )

        if consultas_data:
            for consulta in consultas_data:
                consulta["paciente_id"] = random.choice(pacientes_ids)
                consulta["medico_id"] = random.choice(medicos_ids)
                consulta["cita_id"] = (
                    random.choice(citas_ids)
                    if citas_ids and random.random() > 0.5
                    else None
                )

            faltantes = CANTIDADES["consultas"] - len(consultas_data)
            if faltantes > 0:
                consultas_data.extend(
                    generar_consultas_respaldo(
                        faltantes, pacientes_ids, medicos_ids, citas_ids
                    )
                )
            consultas_ids = insertar_documentos(db.consultas, consultas_data, "consultas")
        else:
            print("➡️ Usando datos de respaldo para consultas...")
            consultas_ids = insertar_documentos(
                db.consultas,
                generar_consultas_respaldo(
                    CANTIDADES["consultas"], pacientes_ids, medicos_ids, citas_ids
                ),
                "consultas de respaldo",
            )

    # 5. DIAGNÓSTICOS, TRATAMIENTOS, HOSPITALIZACIONES, PAGOS
    if pacientes_ids and medicos_ids:
        print("\n🔬 Generando diagnósticos...")
        diagnosticos = generar_diagnosticos(
            CANTIDADES["diagnosticos"], pacientes_ids, medicos_ids, consultas_ids
        )
        insertar_documentos(db.diagnosticos, diagnosticos, "diagnósticos")

    if consultas_ids:
        print("\n💊 Generando tratamientos...")
        tratamientos = generar_tratamientos(CANTIDADES["tratamientos"], consultas_ids)
        insertar_documentos(db.tratamientos, tratamientos, "tratamientos")

    if pacientes_ids and medicos_ids:
        print("\n🏥 Generando hospitalizaciones...")
        hospitalizaciones = generar_hospitalizaciones(
            CANTIDADES["hospitalizaciones"], pacientes_ids, medicos_ids
        )
        insertar_documentos(db.hospitalizaciones, hospitalizaciones, "hospitalizaciones")

    if consultas_ids and pacientes_ids:
        print("\n💰 Generando pagos...")
        pagos = generar_pagos(CANTIDADES["pagos"], consultas_ids, pacientes_ids)
        insertar_documentos(db.pagos, pagos, "pagos")

    # 6. USUARIOS
    print("\n👥 Generando usuarios...")
    usuarios = generar_usuarios()
    upsert_por_campo(db.usuarios, usuarios, "username", "usuarios")

    # RESUMEN
    print("\n" + "=" * 60)
    print("✅ SEEDING COMPLETADO EXITOSAMENTE")
    print("=" * 60 + "\n")
    print(f"📊 Base de datos: {DATABASE_NAME}\n")

    colecciones = [
        "pacientes", "medicos", "citas", "consultas",
        "diagnosticos", "tratamientos", "hospitalizaciones",
        "pagos", "usuarios",
    ]

    for coleccion in colecciones:
        total = db[coleccion].count_documents({})
        print(f"   {coleccion:<22} {total}")

    print("\n🔐 Usuarios disponibles:")
    print("   admin       / admin123")
    print("   medico1     / medico123")
    print("   recepcion   / recep123")
    print("   enfermeria  / enfer123")
    print("\n💡 Para limpiar y volver a crear todo:")
    print("   python seed_db.py --clean\n")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Seed de Hospital Artoria con Gemini y datos de respaldo."
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Elimina todos los datos de las colecciones antes de sembrar.",
    )
    args = parser.parse_args()

    try:
        seed_database(limpiar=args.clean)
    except KeyboardInterrupt:
        print("\n⚠️ Seeding cancelado por el usuario.")
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ ERROR DURANTE EL SEEDING")
        print("=" * 60)
        print(e)
        raise