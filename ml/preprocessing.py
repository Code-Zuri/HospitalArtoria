import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

def prepare_citas_data(db):
    """
    Prepara datos para clasificación de riesgo de cancelación.
    Todo el procesamiento de fechas se hace en Python para evitar errores de MongoDB.
    """
    pipeline = [
        {'$lookup': {'from': 'pacientes', 'localField': 'paciente_id', 'foreignField': '_id', 'as': 'paciente'}},
        {'$unwind': '$paciente'},
        {'$project': {
            'fecha_nacimiento': '$paciente.fecha_nacimiento',
            'fecha_cita': '$fecha',  # traemos la fecha de la cita como string
            'especialidad': 1,
            'estado': 1
        }}
    ]
    cursor = db.citas.aggregate(pipeline)
    df = pd.DataFrame(list(cursor))
    if df.empty:
        return None, None, None, None
    
    # Convertir fechas a datetime
    df['fecha_nacimiento'] = pd.to_datetime(df['fecha_nacimiento'], errors='coerce')
    df['fecha_cita'] = pd.to_datetime(df['fecha_cita'], errors='coerce')
    
    # Calcular edad en años
    ahora = pd.Timestamp.now()
    df['edad'] = (ahora - df['fecha_nacimiento']).dt.days // 365
    df['edad'] = df['edad'].fillna(0).astype(int)
    
    # Extraer día de la semana (0=lunes, 6=domingo) y hora
    df['dia_semana'] = df['fecha_cita'].dt.dayofweek  # 0-6
    df['hora'] = df['fecha_cita'].dt.hour
    
    # Codificar especialidad
    le = LabelEncoder()
    df['especialidad_enc'] = le.fit_transform(df['especialidad'].astype(str))
    
    # Target: 1 si cancelada, 0 si no
    df['target'] = df['estado'].apply(lambda x: 1 if x == 'Cancelada' else 0)
    
    # Seleccionar características
    X = df[['edad', 'dia_semana', 'hora', 'especialidad_enc']]
    y = df['target']
    X = X.fillna(0)
    return train_test_split(X, y, test_size=0.2, random_state=42)

def prepare_consultas_data(db):
    """
    Prepara datos para regresión de costos.
    Todo el procesamiento de fechas en Python.
    """
    pipeline = [
        {'$lookup': {'from': 'pacientes', 'localField': 'paciente_id', 'foreignField': '_id', 'as': 'paciente'}},
        {'$unwind': '$paciente'},
        {'$lookup': {'from': 'medicos', 'localField': 'medico_id', 'foreignField': '_id', 'as': 'medico'}},
        {'$unwind': '$medico'},
        {'$project': {
            'fecha_nacimiento': '$paciente.fecha_nacimiento',
            'especialidad': '$medico.especialidad',
            'costo': 1
        }}
    ]
    df = pd.DataFrame(list(db.consultas.aggregate(pipeline)))
    if df.empty:
        return None, None, None, None
    
    # Convertir fecha de nacimiento a datetime
    df['fecha_nacimiento'] = pd.to_datetime(df['fecha_nacimiento'], errors='coerce')
    ahora = pd.Timestamp.now()
    df['edad'] = (ahora - df['fecha_nacimiento']).dt.days // 365
    df['edad'] = df['edad'].fillna(0).astype(int)
    
    le = LabelEncoder()
    df['especialidad_enc'] = le.fit_transform(df['especialidad'].astype(str))
    X = df[['edad', 'especialidad_enc']]
    y = df['costo']
    X = X.fillna(0)
    return train_test_split(X, y, test_size=0.2, random_state=42)