import pandas as pd
from datetime import datetime
from bson import ObjectId

def get_dataframe(db, collection_name, filtro={}):
    cursor = db[collection_name].find(filtro)
    return pd.DataFrame(list(cursor))

def limpiar_fechas(df, columnas):
    for col in columnas:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

def obtener_metricas_basicas(db):
    total_pacientes = db.pacientes.count_documents({})
    total_medicos = db.medicos.count_documents({})
    total_citas = db.citas.count_documents({})
    total_consultas = db.consultas.count_documents({})
    total_hospitalizaciones = db.hospitalizaciones.count_documents({})
    # Ingresos: sumar montos de pagos
    pipeline = [{'$group': {'_id': None, 'total': {'$sum': '$monto'}}}]
    resultado = list(db.pagos.aggregate(pipeline))
    ingresos = resultado[0]['total'] if resultado else 0
    # Ocupación actual
    ocupadas = db.hospitalizaciones.count_documents({'estado': 'Activa'})
    total_camas = 50  # valor fijo, podría obtenerse de configuración
    ocupacion = round((ocupadas / total_camas) * 100, 2) if total_camas > 0 else 0
    return {
        'pacientes': total_pacientes,
        'medicos': total_medicos,
        'citas': total_citas,
        'consultas': total_consultas,
        'hospitalizaciones': total_hospitalizaciones,
        'ingresos': ingresos,
        'ocupacion': ocupacion,
        'camas_ocupadas': ocupadas,
        'camas_totales': total_camas
    }