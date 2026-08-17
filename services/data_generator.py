import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('es_MX')

def generate_pacientes(db, n=60):
    for _ in range(n):
        data = {
            'nombre': fake.first_name(),
            'apellidos': fake.last_name(),
            'fecha_nacimiento': fake.date_of_birth(minimum_age=0, maximum_age=90).isoformat(),
            'genero': random.choice(['M', 'F']),
            'telefono': fake.phone_number(),
            'email': fake.email(),
            'direccion': fake.address(),
            'tipo_sangre': random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
            'alergias': random.choice([None, fake.word(), fake.sentence()]),
            'antecedentes': random.choice([None, fake.text()])
        }
        db.pacientes.insert_one(data)

def generate_medicos(db, n=12):
    especialidades = ['Cardiología', 'Pediatría', 'Medicina Interna', 'Dermatología', 'Neurología', 'Ginecología', 'Ortopedia', 'Oftalmología']
    for _ in range(n):
        data = {
            'nombre': fake.first_name(),
            'apellidos': fake.last_name(),
            'cedula': fake.random_number(digits=8),
            'especialidad': random.choice(especialidades),
            'telefono': fake.phone_number(),
            'email': fake.email(),
            'estado': random.choice(['Activo', 'Inactivo']),
            'horarios': random.choice([{'lunes': '9-14', 'miercoles': '9-14'}, {'martes': '10-15', 'jueves': '10-15'}])
        }
        db.medicos.insert_one(data)

def generate_citas(db, n=200):
    pacientes = list(db.pacientes.find())
    medicos = list(db.medicos.find())
    estados = ['Programada', 'Confirmada', 'Atendida', 'Cancelada', 'No asistió']
    for _ in range(n):
        p = random.choice(pacientes)
        m = random.choice(medicos)
        fecha = fake.date_time_between(start_date='-90d', end_date='+30d')
        data = {
            'paciente_id': p['_id'],
            'medico_id': m['_id'],
            'fecha': fecha.isoformat(),
            'motivo': fake.sentence(),
            'estado': random.choice(estados),
            'especialidad': m.get('especialidad', 'General'),
            'fecha_creacion': datetime.now().isoformat()
        }
        db.citas.insert_one(data)

def generate_consultas(db, n=150):
    pacientes = list(db.pacientes.find())
    medicos = list(db.medicos.find())
    for _ in range(n):
        p = random.choice(pacientes)
        m = random.choice(medicos)
        fecha = fake.date_time_between(start_date='-90d', end_date='now')
        data = {
            'paciente_id': p['_id'],
            'medico_id': m['_id'],
            'fecha': fecha.isoformat(),
            'motivo': fake.sentence(),
            'sintomas': fake.text(),
            'observaciones': fake.text(),
            'diagnostico': fake.word(),
            'tratamiento': fake.sentence(),
            'costo': round(random.uniform(300, 5000), 2),
            'especialidad': m.get('especialidad', 'General')
        }
        db.consultas.insert_one(data)

def generate_diagnosticos(db, n=120):
    pacientes = list(db.pacientes.find())
    medicos = list(db.medicos.find())
    enfermedades = ['Hipertensión', 'Diabetes', 'Infección respiratoria', 'Fractura', 'Dermatitis', 'Migraña', 'Ansiedad', 'Gastritis']
    for _ in range(n):
        p = random.choice(pacientes)
        m = random.choice(medicos)
        fecha = fake.date_time_between(start_date='-90d', end_date='now')
        data = {
            'paciente_id': p['_id'],
            'medico_id': m['_id'],
            'enfermedad': random.choice(enfermedades),
            'codigo': fake.bothify(text='??-####'),
            'descripcion': fake.sentence(),
            'fecha': fecha.isoformat()
        }
        db.diagnosticos.insert_one(data)

def generate_tratamientos(db, n=100):
    consultas = list(db.consultas.find())
    medicamentos = ['Paracetamol', 'Ibuprofeno', 'Amoxicilina', 'Loratadina', 'Omeprazol', 'Losartán', 'Metformina']
    for _ in range(n):
        c = random.choice(consultas)
        data = {
            'consulta_id': c['_id'],
            'tratamiento': fake.sentence(),
            'medicamentos': [random.choice(medicamentos) for _ in range(random.randint(1, 3))],
            'dosis': random.choice(['1 c/12h', '1 c/8h', '2 c/día']),
            'frecuencia': random.choice(['Diario', 'Cada 12 horas']),
            'duracion': random.randint(3, 30),
            'indicaciones': fake.text()
        }
        db.tratamientos.insert_one(data)

def generate_hospitalizaciones(db, n=40):
    pacientes = list(db.pacientes.find())
    medicos = list(db.medicos.find())
    estados = ['Activa', 'Alta', 'En observación']
    for _ in range(n):
        p = random.choice(pacientes)
        m = random.choice(medicos)
        ingreso = fake.date_time_between(start_date='-90d', end_date='now')
        alta = ingreso + timedelta(days=random.randint(1, 15)) if random.random() > 0.3 else None
        data = {
            'paciente_id': p['_id'],
            'medico_id': m['_id'],
            'fecha_ingreso': ingreso.isoformat(),
            'fecha_alta': alta.isoformat() if alta else None,
            'habitacion': random.randint(100, 150),
            'cama': random.randint(1, 10),
            'motivo': fake.sentence(),
            'diagnostico': fake.word(),
            'estado': random.choice(estados),
            'costo_estimado': round(random.uniform(5000, 50000), 2)
        }
        db.hospitalizaciones.insert_one(data)

def generate_pagos(db, n=150):
    consultas = list(db.consultas.find())
    for _ in range(n):
        c = random.choice(consultas)
        data = {
            'consulta_id': c['_id'],
            'paciente_id': c['paciente_id'],
            'monto': c.get('costo', random.uniform(300, 5000)),
            'fecha': fake.date_time_between(start_date='-90d', end_date='now').isoformat(),
            'metodo': random.choice(['Efectivo', 'Tarjeta', 'Transferencia']),
            'estado': random.choice(['Pagado', 'Pendiente'])
        }
        db.pagos.insert_one(data)

def generate_all_data(db):
    print("Generando pacientes...")
    generate_pacientes(db, 60)
    print("Generando médicos...")
    generate_medicos(db, 12)
    print("Generando citas...")
    generate_citas(db, 200)
    print("Generando consultas...")
    generate_consultas(db, 150)
    print("Generando diagnósticos...")
    generate_diagnosticos(db, 120)
    print("Generando tratamientos...")
    generate_tratamientos(db, 100)
    print("Generando hospitalizaciones...")
    generate_hospitalizaciones(db, 40)
    print("Generando pagos...")
    generate_pagos(db, 150)
    print("Datos de prueba generados exitosamente.")