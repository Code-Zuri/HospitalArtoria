from flask import Blueprint, jsonify, render_template
from database.mongodb import get_db
from services.analytics import obtener_metricas_basicas, get_dataframe
from ml.preprocessing import prepare_citas_data, prepare_consultas_data
from ml.regression import entrenar_regresion, evaluar_regresion
from ml.classification import entrenar_clasificador, evaluar_clasificador
from ml.clustering import clusterizar_pacientes
from decorators import login_required, role_required
import pandas as pd
from datetime import timedelta

reportes_bp = Blueprint('reportes', __name__)

# --- Página principal ---
@reportes_bp.route('/')
@login_required
@role_required('admin', 'medico', 'recepcionista')
def dashboard():
    return render_template('reportes.html')

# --- Endpoints de métricas y gráficas ---
@reportes_bp.route('/api/metricas')
@login_required
@role_required('admin', 'medico', 'recepcionista')
def api_metricas():
    db = get_db()
    return jsonify(obtener_metricas_basicas(db))

@reportes_bp.route('/api/consultas-por-mes')
@login_required
@role_required('admin', 'medico', 'recepcionista')
def consultas_por_mes():
    db = get_db()
    df = get_dataframe(db, 'consultas')
    if df.empty:
        return jsonify([])
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['mes'] = df['fecha'].dt.to_period('M').astype(str)
    conteo = df.groupby('mes').size().reset_index(name='cantidad')
    return jsonify(conteo.to_dict(orient='records'))

@reportes_bp.route('/api/especialidades-demanda')
@login_required
@role_required('admin', 'medico')
def especialidades_demanda():
    db = get_db()
    pipeline = [
        {'$lookup': {'from': 'medicos', 'localField': 'medico_id', 'foreignField': '_id', 'as': 'medico'}},
        {'$unwind': '$medico'},
        {'$group': {'_id': '$medico.especialidad', 'cantidad': {'$sum': 1}}}
    ]
    resultado = list(db.consultas.aggregate(pipeline))
    return jsonify(resultado)

@reportes_bp.route('/api/enfermedades-frecuentes')
@login_required
@role_required('admin', 'medico')
def enfermedades_frecuentes():
    db = get_db()
    pipeline = [
        {'$group': {'_id': '$enfermedad', 'cantidad': {'$sum': 1}}},
        {'$sort': {'cantidad': -1}},
        {'$limit': 10}
    ]
    resultado = list(db.diagnosticos.aggregate(pipeline))
    return jsonify(resultado)

@reportes_bp.route('/api/ocupacion-hospitalaria')
@login_required
@role_required('admin', 'medico', 'enfermeria')
def ocupacion_hospitalaria():
    db = get_db()
    total_camas = 50
    activas = db.hospitalizaciones.count_documents({'estado': 'Activa'})
    return jsonify({
        'total_camas': total_camas,
        'ocupadas': activas,
        'porcentaje': round((activas / total_camas) * 100, 2)
    })

# --- Endpoints de Machine Learning ---
@reportes_bp.route('/api/ml/riesgo-cancelacion')
@login_required
@role_required('admin', 'medico')
def ml_riesgo_cancelacion():
    db = get_db()
    X_train, X_test, y_train, y_test = prepare_citas_data(db)
    if X_train is None:
        return jsonify({'error': 'No hay suficientes datos para entrenar'})
    model = entrenar_clasificador(X_train, y_train)
    metrics = evaluar_clasificador(model, X_test, y_test)
    y_pred = model.predict(X_test)
    return jsonify({
        'metrics': metrics,
        'predicciones': y_pred.tolist(),
        'reales': y_test.tolist()
    })

@reportes_bp.route('/api/ml/prediccion-demanda')
@login_required
@role_required('admin', 'medico')
def ml_demanda():
    db = get_db()
    df = get_dataframe(db, 'consultas')
    if df.empty:
        return jsonify({'error': 'No hay datos'})
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['dia'] = df['fecha'].dt.dayofweek
    df['mes'] = df['fecha'].dt.month
    agrupado = df.groupby('fecha').size().reset_index(name='consultas')
    agrupado['dia_semana'] = agrupado['fecha'].dt.dayofweek
    agrupado['mes'] = agrupado['fecha'].dt.month
    X = agrupado[['dia_semana', 'mes']]
    y = agrupado['consultas']
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = entrenar_regresion(X_train, y_train, 'random_forest')
    metrics = evaluar_regresion(model, X_test, y_test)
    ultima_fecha = agrupado['fecha'].max()
    futuras = pd.date_range(start=ultima_fecha + timedelta(days=1), periods=7)
    futuras_df = pd.DataFrame({'fecha': futuras})
    futuras_df['dia_semana'] = futuras_df['fecha'].dt.dayofweek
    futuras_df['mes'] = futuras_df['fecha'].dt.month
    pred_futuras = model.predict(futuras_df[['dia_semana', 'mes']])
    return jsonify({
        'metricas': metrics,
        'predicciones_futuras': pred_futuras.tolist(),
        'fechas': futuras.strftime('%Y-%m-%d').tolist()
    })

# ------------------------------------------------------------------
# 🟢 CORREGIDO: usa prepare_consultas_data (sin $dateDiff en MongoDB)
# ------------------------------------------------------------------
@reportes_bp.route('/api/ml/prediccion-costos')
@login_required
@role_required('admin', 'medico')
def ml_costos():
    db = get_db()
    X_train, X_test, y_train, y_test = prepare_consultas_data(db)
    if X_train is None:
        return jsonify({'error': 'No hay datos suficientes para entrenar'})
    model = entrenar_regresion(X_train, y_train, 'random_forest')
    metrics = evaluar_regresion(model, X_test, y_test)
    return jsonify({
        'metricas': metrics,
        'predicciones': model.predict(X_test).tolist()
    })

@reportes_bp.route('/api/ml/clustering-pacientes')
@login_required
@role_required('admin', 'medico')
def api_clustering():
    db = get_db()
    clusters = clusterizar_pacientes(db)
    return jsonify(clusters)