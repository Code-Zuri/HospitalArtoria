import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def clusterizar_pacientes(db):
    """
    Agrupa a los pacientes en clusters según su edad y número de consultas.
    Retorna una lista de diccionarios con edad, num_consultas y cluster asignado.
    """
    pipeline = [
        {'$lookup': {'from': 'consultas', 'localField': '_id', 'foreignField': 'paciente_id', 'as': 'consultas'}},
        {'$project': {
            'edad': {'$dateDiff': {'startDate': {'$toDate': '$fecha_nacimiento'}, 'endDate': '$$NOW', 'unit': 'year'}},
            'num_consultas': {'$size': '$consultas'},
            'genero': 1
        }}
    ]
    df = pd.DataFrame(list(db.pacientes.aggregate(pipeline)))
    if df.empty:
        return []
    X = df[['edad', 'num_consultas']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=3, random_state=42)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    return df[['edad', 'num_consultas', 'cluster']].to_dict(orient='records')