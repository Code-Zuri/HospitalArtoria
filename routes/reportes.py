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
from odf import text, teletype, table as odf_table
from odf.opendocument import OpenDocumentText
from io import BytesIO
from flask import send_file

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

# ============================================================
# Nuevos endpoints para gráficas adicionales
# ============================================================

@reportes_bp.route('/api/citas-por-estado')
@login_required
@role_required('admin', 'medico', 'recepcionista')
def citas_por_estado():
    """Retorna el conteo de citas agrupadas por estado."""
    db = get_db()
    pipeline = [
        {'$group': {'_id': '$estado', 'cantidad': {'$sum': 1}}}
    ]
    resultado = list(db.citas.aggregate(pipeline))
    return jsonify(resultado)

@reportes_bp.route('/api/ingresos-por-mes')
@login_required
@role_required('admin', 'medico')
def ingresos_por_mes():
    """Retorna los ingresos totales agrupados por mes."""
    db = get_db()
    pipeline = [
        {'$match': {'estado': 'Pagado'}},
        # Convertir 'fecha' de string a Date
        {'$addFields': {
            'fecha_date': {'$toDate': '$fecha'}
        }},
        {'$project': {
            'mes': {'$dateToString': {'format': '%Y-%m', 'date': '$fecha_date'}},
            'monto': 1
        }},
        {'$group': {'_id': '$mes', 'total': {'$sum': '$monto'}}},
        {'$sort': {'_id': 1}}
    ]
    resultado = list(db.pagos.aggregate(pipeline))
    data = [{'mes': r['_id'], 'total': r['total']} for r in resultado]
    return jsonify(data)



@reportes_bp.route('/api/informe')
@login_required
@role_required('admin', 'medico', 'recepcionista')
def descargar_informe():
    """Genera un informe en formato ODF (.odt) con KPIs, pacientes y médicos."""
    db = get_db()

    # --- 1. Obtener datos ---
    metricas = obtener_metricas_basicas(db)
    pacientes = list(db.pacientes.find().limit(100))
    medicos = list(db.medicos.find().limit(50))

    # --- 2. Crear documento ODT ---
    doc = OpenDocumentText()

    # Título principal (outlinelevel=1)
    h1 = text.H(outlinelevel=1, text="Informe Hospitalario - " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"))
    doc.text.addElement(h1)

    # --- Resumen de KPIs (subtítulo nivel 2) ---
    h2 = text.H(outlinelevel=2, text="Resumen de Indicadores")
    doc.text.addElement(h2)

    for key, value in metricas.items():
        if key in ['pacientes', 'medicos', 'citas', 'consultas', 'camas_ocupadas', 'camas_totales']:
            doc.text.addElement(text.P(text=f"{key.capitalize()}: {value}"))
    doc.text.addElement(text.P(text=f"Ingresos totales: ${metricas.get('ingresos', 0):,.2f}"))
    doc.text.addElement(text.P(text=f"Ocupación: {metricas.get('ocupacion', 0)}%"))

    # --- Tabla de Pacientes (subtítulo nivel 2) ---
    h_pac = text.H(outlinelevel=2, text="Listado de Pacientes (primeros 100)")
    doc.text.addElement(h_pac)

    tabla_pacientes = odf_table.Table(name="Pacientes")
    encabezados = ["Nombre", "Apellidos", "Email", "Teléfono", "Tipo Sangre"]
    fila_enc = odf_table.TableRow()
    for enc in encabezados:
        celda = odf_table.TableCell()
        celda.addElement(text.P(text=enc))
        fila_enc.addElement(celda)
    tabla_pacientes.addElement(fila_enc)

    for p in pacientes:
        fila = odf_table.TableRow()
        for campo in ['nombre', 'apellidos', 'email', 'telefono', 'tipo_sangre']:
            celda = odf_table.TableCell()
            valor = p.get(campo, '')
            if valor is None:
                valor = ''
            celda.addElement(text.P(text=str(valor)))
            fila.addElement(celda)
        tabla_pacientes.addElement(fila)
    doc.text.addElement(tabla_pacientes)

    # --- Tabla de Médicos (subtítulo nivel 2) ---
    h_med = text.H(outlinelevel=2, text="Listado de Médicos")
    doc.text.addElement(h_med)

    tabla_medicos = odf_table.Table(name="Médicos")
    encabezados_med = ["Nombre", "Apellidos", "Especialidad", "Teléfono", "Email", "Estado"]
    fila_enc_med = odf_table.TableRow()
    for enc in encabezados_med:
        celda = odf_table.TableCell()
        celda.addElement(text.P(text=enc))
        fila_enc_med.addElement(celda)
    tabla_medicos.addElement(fila_enc_med)

    for m in medicos:
        fila = odf_table.TableRow()
        for campo in ['nombre', 'apellidos', 'especialidad', 'telefono', 'email', 'estado']:
            celda = odf_table.TableCell()
            valor = m.get(campo, '')
            if valor is None:
                valor = ''
            celda.addElement(text.P(text=str(valor)))
            fila.addElement(celda)
        tabla_medicos.addElement(fila)
    doc.text.addElement(tabla_medicos)

    # --- Guardar en memoria y enviar ---
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Informe_Hospital_{pd.Timestamp.now().strftime('%Y%m%d')}.odt",
        mimetype='application/vnd.oasis.opendocument.text'
    )

# ============================================================
# NUEVOS ENDPOINTS PARA GRÁFICAS DE ML Y ANÁLISIS
# ============================================================

@reportes_bp.route('/api/ml/distribucion-edad')
@login_required
@role_required('admin', 'medico')
def distribucion_edad():
    """Retorna datos para histograma de edades de pacientes."""
    db = get_db()
    pipeline = [
        {'$project': {
            'edad': {'$dateDiff': {'startDate': {'$toDate': '$fecha_nacimiento'}, 'endDate': '$$NOW', 'unit': 'year'}}
        }}
    ]
    df = pd.DataFrame(list(db.pacientes.aggregate(pipeline)))
    if df.empty:
        return jsonify([])
    # Crear bins de edad (0-10, 10-20, ..., 80-90, 90+)
    bins = list(range(0, 101, 10))
    labels = [f'{bins[i]}-{bins[i+1]}' for i in range(len(bins)-1)]
    df['grupo_edad'] = pd.cut(df['edad'], bins=bins, labels=labels, right=False)
    conteo = df['grupo_edad'].value_counts().sort_index().reset_index()
    conteo.columns = ['grupo', 'cantidad']
    return jsonify(conteo.to_dict(orient='records'))

@reportes_bp.route('/api/ml/costo-vs-edad')
@login_required
@role_required('admin', 'medico')
def costo_vs_edad():
    """Retorna datos para scatter plot de costo vs edad."""
    db = get_db()
    pipeline = [
        {'$lookup': {'from': 'pacientes', 'localField': 'paciente_id', 'foreignField': '_id', 'as': 'paciente'}},
        {'$unwind': '$paciente'},
        {'$project': {
            'edad': {'$dateDiff': {'startDate': {'$toDate': '$paciente.fecha_nacimiento'}, 'endDate': '$$NOW', 'unit': 'year'}},
            'costo': 1
        }}
    ]
    df = pd.DataFrame(list(db.consultas.aggregate(pipeline)))
    if df.empty:
        return jsonify([])
    # Limpiar valores nulos y outliers
    df = df.dropna(subset=['edad', 'costo'])
    df = df[(df['edad'] >= 0) & (df['edad'] <= 120) & (df['costo'] > 0) & (df['costo'] < 100000)]
    # Calcular regresión lineal simple (para la línea de tendencia)
    from sklearn.linear_model import LinearRegression
    X = df[['edad']].values
    y = df['costo'].values
    model = LinearRegression().fit(X, y)
    x_min, x_max = df['edad'].min(), df['edad'].max()
    x_line = np.linspace(x_min, x_max, 50).reshape(-1, 1)
    y_line = model.predict(x_line)
    return jsonify({
        'puntos': df[['edad', 'costo']].to_dict(orient='records'),
        'linea': {'x': x_line.flatten().tolist(), 'y': y_line.tolist()}
    })

@reportes_bp.route('/api/ml/ingresos-vs-ocupacion')
@login_required
@role_required('admin', 'medico')
def ingresos_vs_ocupacion():
    """Retorna datos para gráfica de ingresos vs ocupación (eje dual)."""
    db = get_db()
    # Ingresos por mes
    pipeline_ing = [
        {'$match': {'estado': 'Pagado'}},
        {'$addFields': {'fecha_date': {'$toDate': '$fecha'}}},
        {'$project': {'mes': {'$dateToString': {'format': '%Y-%m', 'date': '$fecha_date'}}, 'monto': 1}},
        {'$group': {'_id': '$mes', 'total': {'$sum': '$monto'}}},
        {'$sort': {'_id': 1}}
    ]
    ingresos = list(db.pagos.aggregate(pipeline_ing))
    # Ocupación por mes (promedio de camas ocupadas)
    # Para simplificar, usamos el total de hospitalizaciones activas por mes
    pipeline_ocup = [
        {'$addFields': {'fecha_ingreso_date': {'$toDate': '$fecha_ingreso'}}},
        {'$project': {'mes': {'$dateToString': {'format': '%Y-%m', 'date': '$fecha_ingreso_date'}}, 'estado': 1}},
        {'$group': {'_id': {'mes': '$mes', 'estado': '$estado'}, 'count': {'$sum': 1}}},
        {'$sort': {'_id.mes': 1}}
    ]
    ocup_data = list(db.hospitalizaciones.aggregate(pipeline_ocup))
    # Procesar para obtener ocupación promedio por mes (simplificado)
    ocup_por_mes = {}
    total_camas = 50
    for item in ocup_data:
        mes = item['_id']['mes']
        estado = item['_id']['estado']
        count = item['count']
        if mes not in ocup_por_mes:
            ocup_por_mes[mes] = {'activas': 0, 'totales': 0}
        if estado == 'Activa':
            ocup_por_mes[mes]['activas'] += count
        ocup_por_mes[mes]['totales'] += count
    # Crear lista de meses y ocupación porcentual
    meses_ocup = []
    ocupacion_porcentaje = []
    for mes, datos in sorted(ocup_por_mes.items()):
        meses_ocup.append(mes)
        porcentaje = (datos['activas'] / total_camas) * 100 if total_camas > 0 else 0
        ocupacion_porcentaje.append(porcentaje)
    # Unir con ingresos (solo meses comunes)
    meses_ing = [i['_id'] for i in ingresos]
    ingresos_val = [i['total'] for i in ingresos]
    # Intersectar meses
    meses_comunes = sorted(set(meses_ing) & set(meses_ocup))
    ingresos_filtrados = [ingresos_val[meses_ing.index(m)] for m in meses_comunes]
    ocupacion_filtrada = [ocupacion_porcentaje[meses_ocup.index(m)] for m in meses_comunes]
    return jsonify({
        'meses': meses_comunes,
        'ingresos': ingresos_filtrados,
        'ocupacion': ocupacion_filtrada
    })