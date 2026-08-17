from flask import current_app, g
from pymongo import MongoClient
import os
import time

def get_db():
    if 'db' not in g:
        # Configurar timeouts más largos para evitar NetworkTimeout
        client = MongoClient(
            os.getenv('MONGO_URI'),
            serverSelectionTimeoutMS=30000,   # 30 segundos
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            retryWrites=True,
            w='majority'
        )
        # Verificar conexión antes de devolver
        try:
            client.admin.command('ping')
            print("✅ Conexión a MongoDB Atlas exitosa.")
        except Exception as e:
            print(f"❌ Error al conectar a MongoDB: {e}")
            raise
        g.db = client[os.getenv('DATABASE_NAME')]
    return g.db

def init_db(app):
    with app.app_context():
        db = get_db()
        print("Creando índices en MongoDB...")
        try:
            # Índices para pacientes
            db.pacientes.create_index('email', unique=True)
            db.pacientes.create_index([('apellidos', 1), ('nombre', 1)])
            
            # Índices para médicos
            db.medicos.create_index('cedula', unique=True)
            db.medicos.create_index('especialidad')
            
            # Índices para citas
            db.citas.create_index([('paciente_id', 1), ('fecha', -1)])
            db.citas.create_index([('medico_id', 1), ('fecha', -1)])
            db.citas.create_index('fecha')
            db.citas.create_index('estado')
            
            # Índices para consultas
            db.consultas.create_index([('paciente_id', 1), ('fecha', -1)])
            db.consultas.create_index([('medico_id', 1), ('fecha', -1)])
            db.consultas.create_index('fecha')
            
            # Índices para diagnósticos
            db.diagnosticos.create_index('enfermedad')
            db.diagnosticos.create_index('fecha')
            
            # Índices para hospitalizaciones
            db.hospitalizaciones.create_index([('paciente_id', 1), ('fecha_ingreso', -1)])
            db.hospitalizaciones.create_index('estado')
            db.hospitalizaciones.create_index('fecha_ingreso')
            
            # Índices para pagos
            db.pagos.create_index('fecha')
            db.pagos.create_index('estado')
            
            # Índice para usuarios
            db.usuarios.create_index('username', unique=True)
            db.usuarios.create_index('email', unique=True)
            
            print("✅ Índices creados exitosamente.")
        except Exception as e:
            print(f"⚠️ Error al crear algunos índices: {e}")
            # No detenemos la ejecución, los índices pueden crearse después manualmente
        
    return db