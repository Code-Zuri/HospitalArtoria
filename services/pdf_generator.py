# services/pdf_generator.py
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Para entornos sin GUI
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
from flask import render_template_string

def generar_grafica_base64(fig):
    """Convierte una figura de matplotlib a base64 para incrustar en HTML."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64

def generar_informe_html(db):
    """
    Genera el contenido HTML del informe con todas las gráficas y tablas.
    Retorna el HTML como string.
    """

    # --- Obtener datos ---
    from services.analytics import obtener_metricas_basicas, get_dataframe

    metricas = obtener_metricas_basicas(db)
    pacientes = list(db.pacientes.find().limit(100))
    medicos = list(db.medicos.find().limit(50))

    # --- 1. Gráfica: Consultas por mes ---
    df_consultas = get_dataframe(db, 'consultas')
    if not df_consultas.empty:
        df_consultas['fecha'] = pd.to_datetime(df_consultas['fecha'])
        df_consultas['mes'] = df_consultas['fecha'].dt.to_period('M').astype(str)
        consultas_mes = df_consultas.groupby('mes').size().reset_index(name='cantidad')

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(consultas_mes['mes'], consultas_mes['cantidad'], color='#4BC0C0')
        ax.set_title('Consultas por mes', fontsize=14)
        ax.set_xlabel('Mes')
        ax.set_ylabel('Cantidad')
        plt.xticks(rotation=45, ha='right')
        img_consultas = generar_grafica_base64(fig)
    else:
        img_consultas = None

    # --- 2. Gráfica: Demanda por especialidad ---
    pipeline_esp = [
        {'$lookup': {'from': 'medicos', 'localField': 'medico_id', 'foreignField': '_id', 'as': 'medico'}},
        {'$unwind': '$medico'},
        {'$group': {'_id': '$medico.especialidad', 'cantidad': {'$sum': 1}}}
    ]
    esp_data = list(db.consultas.aggregate(pipeline_esp))
    if esp_data:
        fig, ax = plt.subplots(figsize=(6, 6))
        labels = [d['_id'] or 'Sin especificar' for d in esp_data]
        values = [d['cantidad'] for d in esp_data]
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.set_title('Demanda por especialidad', fontsize=14)
        img_esp = generar_grafica_base64(fig)
    else:
        img_esp = None

    # --- 3. Gráfica: Enfermedades frecuentes ---
    pipeline_enf = [
        {'$group': {'_id': '$enfermedad', 'cantidad': {'$sum': 1}}},
        {'$sort': {'cantidad': -1}},
        {'$limit': 10}
    ]
    enf_data = list(db.diagnosticos.aggregate(pipeline_enf))
    if enf_data:
        fig, ax = plt.subplots(figsize=(8, 4))
        enfermedades = [d['_id'] or 'No especificado' for d in enf_data]
        cantidades = [d['cantidad'] for d in enf_data]
        ax.barh(enfermedades, cantidades, color='#FF6384')
        ax.set_title('Enfermedades más frecuentes', fontsize=14)
        ax.set_xlabel('Frecuencia')
        img_enf = generar_grafica_base64(fig)
    else:
        img_enf = None

    # --- 4. Gráfica: Ocupación hospitalaria ---
    total_camas = 50
    ocupadas = db.hospitalizaciones.count_documents({'estado': 'Activa'})
    disponibles = total_camas - ocupadas
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie([ocupadas, disponibles], labels=['Ocupadas', 'Disponibles'],
           autopct='%1.1f%%', colors=['#FF6384', '#36A2EB'], startangle=90)
    ax.set_title('Ocupación hospitalaria', fontsize=14)
    img_ocup = generar_grafica_base64(fig)

    # --- 5. Gráfica: Citas por estado ---
    pipeline_estado = [
        {'$group': {'_id': '$estado', 'cantidad': {'$sum': 1}}}
    ]
    estado_data = list(db.citas.aggregate(pipeline_estado))
    if estado_data:
        fig, ax = plt.subplots(figsize=(6, 6))
        labels = [d['_id'] or 'Desconocido' for d in estado_data]
        values = [d['cantidad'] for d in estado_data]
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.set_title('Citas por estado', fontsize=14)
        img_estado = generar_grafica_base64(fig)
    else:
        img_estado = None

    # --- 6. Gráfica: Ingresos por mes ---
    pipeline_ing = [
        {'$match': {'estado': 'Pagado'}},
        {'$addFields': {'fecha_date': {'$toDate': '$fecha'}}},
        {'$project': {'mes': {'$dateToString': {'format': '%Y-%m', 'date': '$fecha_date'}}, 'monto': 1}},
        {'$group': {'_id': '$mes', 'total': {'$sum': '$monto'}}},
        {'$sort': {'_id': 1}}
    ]
    ing_data = list(db.pagos.aggregate(pipeline_ing))
    if ing_data:
        fig, ax = plt.subplots(figsize=(8, 4))
        meses = [d['_id'] for d in ing_data]
        totales = [d['total'] for d in ing_data]
        ax.plot(meses, totales, marker='o', linestyle='-', color='#4BC0C0')
        ax.set_title('Evolución de ingresos', fontsize=14)
        ax.set_xlabel('Mes')
        ax.set_ylabel('Ingresos ($)')
        plt.xticks(rotation=45, ha='right')
        img_ingresos = generar_grafica_base64(fig)
    else:
        img_ingresos = None

    # --- Construir HTML ---
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Informe Hospitalario</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
            h1 {{ color: #1a3e60; border-bottom: 2px solid #1a3e60; padding-bottom: 10px; }}
            h2 {{ color: #1a3e60; margin-top: 30px; }}
            .kpi-grid {{ display: flex; flex-wrap: wrap; gap: 20px; margin: 20px 0; }}
            .kpi-item {{ background: #f8f9fa; padding: 15px 25px; border-radius: 8px; border-left: 4px solid #1a3e60; }}
            .kpi-label {{ font-weight: bold; color: #6c757d; }}
            .kpi-value {{ font-size: 24px; font-weight: bold; color: #1a3e60; }}
            .chart-container {{ margin: 30px 0; text-align: center; }}
            .chart-container img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 8px; }}
            .chart-description {{ font-size: 14px; color: #555; margin-top: 10px; text-align: left; max-width: 800px; margin-left: auto; margin-right: auto; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #1a3e60; color: white; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .footer {{ margin-top: 40px; font-size: 12px; color: #999; text-align: center; border-top: 1px solid #ddd; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <h1>Informe Hospitalario</h1>
        <p><strong>Fecha de generación:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

        <h2>Resumen de Indicadores</h2>
        <div class="kpi-grid">
            <div class="kpi-item"><span class="kpi-label">🧑‍⚕️ Pacientes</span><div class="kpi-value">{metricas.get('pacientes', 0)}</div></div>
            <div class="kpi-item"><span class="kpi-label">👨‍⚕️ Médicos</span><div class="kpi-value">{metricas.get('medicos', 0)}</div></div>
            <div class="kpi-item"><span class="kpi-label">📅 Citas</span><div class="kpi-value">{metricas.get('citas', 0)}</div></div>
            <div class="kpi-item"><span class="kpi-label">🩺 Consultas</span><div class="kpi-value">{metricas.get('consultas', 0)}</div></div>
            <div class="kpi-item"><span class="kpi-label">💰 Ingresos</span><div class="kpi-value">${metricas.get('ingresos', 0):,.2f}</div></div>
            <div class="kpi-item"><span class="kpi-label">🛏️ Ocupación</span><div class="kpi-value">{metricas.get('ocupacion', 0)}%</div></div>
        </div>
        <p><strong>Interpretación:</strong> El hospital atiende a {metricas.get('pacientes', 0)} pacientes con {metricas.get('medicos', 0)} médicos. Se han registrado {metricas.get('citas', 0)} citas y {metricas.get('consultas', 0)} consultas. Los ingresos totales ascienden a ${metricas.get('ingresos', 0):,.2f} y la ocupación hospitalaria es del {metricas.get('ocupacion', 0)}%.</p>

        <h2>Análisis de Consultas</h2>
        <div class="chart-container">
            <h3>Consultas por mes</h3>
            {f'<img src="data:image/png;base64,{img_consultas}" alt="Consultas por mes">' if img_consultas else '<p>No hay datos suficientes.</p>'}
            <div class="chart-description"><strong>Descripción:</strong> Esta gráfica muestra la evolución mensual del número de consultas. Permite identificar tendencias estacionales y picos de demanda.</div>
        </div>

        <div class="chart-container">
            <h3>Demanda por especialidad</h3>
            {f'<img src="data:image/png;base64,{img_esp}" alt="Demanda por especialidad">' if img_esp else '<p>No hay datos suficientes.</p>'}
            <div class="chart-description"><strong>Descripción:</strong> Distribución porcentual de consultas según especialidad médica. Ayuda a detectar qué servicios tienen mayor demanda para planificar recursos.</div>
        </div>

        <h2>Análisis de Diagnósticos</h2>
        <div class="chart-container">
            <h3>Enfermedades más frecuentes</h3>
            {f'<img src="data:image/png;base64,{img_enf}" alt="Enfermedades más frecuentes">' if img_enf else '<p>No hay datos suficientes.</p>'}
            <div class="chart-description"><strong>Descripción:</strong> Las enfermedades más diagnosticadas. Esta información es clave para orientar campañas de prevención y optimizar inventario de medicamentos.</div>
        </div>

        <h2>Gestión Hospitalaria</h2>
        <div class="chart-container">
            <h3>Ocupación hospitalaria</h3>
            <img src="data:image/png;base64,{img_ocup}" alt="Ocupación hospitalaria">
            <div class="chart-description"><strong>Descripción:</strong> Estado actual de ocupación de camas. Un alto porcentaje (>80%) puede indicar necesidad de ampliar capacidad o gestionar altas.</div>
        </div>

        <div class="chart-container">
            <h3>Citas por estado</h3>
            {f'<img src="data:image/png;base64,{img_estado}" alt="Citas por estado">' if img_estado else '<p>No hay datos suficientes.</p>'}
            <div class="chart-description"><strong>Descripción:</strong> Distribución de citas según su estado (programadas, confirmadas, atendidas, canceladas, no asistió). Permite evaluar la eficiencia en la gestión de citas.</div>
        </div>

        <h2>Análisis Financiero</h2>
        <div class="chart-container">
            <h3>Evolución de ingresos</h3>
            {f'<img src="data:image/png;base64,{img_ingresos}" alt="Ingresos por mes">' if img_ingresos else '<p>No hay datos suficientes.</p>'}
            <div class="chart-description"><strong>Descripción:</strong> Tendencia de ingresos mensuales. Ayuda a prever flujos de caja y evaluar el impacto de campañas o cambios en tarifas.</div>
        </div>

        <h2>Listado de Pacientes (primeros 100)</h2>
        <table>
            <thead><tr><th>Nombre</th><th>Apellidos</th><th>Email</th><th>Teléfono</th><th>Tipo Sangre</th></tr></thead>
            <tbody>
    """
    for p in pacientes:
        html_content += f"""
        <tr>
            <td>{p.get('nombre', '')}</td>
            <td>{p.get('apellidos', '')}</td>
            <td>{p.get('email', '')}</td>
            <td>{p.get('telefono', '')}</td>
            <td>{p.get('tipo_sangre', '')}</td>
        </tr>
        """
    html_content += """
            </tbody>
        </table>

        <h2>Listado de Médicos</h2>
        <table>
            <thead><tr><th>Nombre</th><th>Apellidos</th><th>Especialidad</th><th>Teléfono</th><th>Email</th><th>Estado</th></tr></thead>
            <tbody>
    """
    for m in medicos:
        html_content += f"""
        <tr>
            <td>{m.get('nombre', '')}</td>
            <td>{m.get('apellidos', '')}</td>
            <td>{m.get('especialidad', '')}</td>
            <td>{m.get('telefono', '')}</td>
            <td>{m.get('email', '')}</td>
            <td>{m.get('estado', '')}</td>
        </tr>
        """
    html_content += """
            </tbody>
        </table>

        <div class="footer">
            Informe generado automáticamente por el Sistema Integral de Gestión Hospitalaria.
        </div>
    </body>
    </html>
    """
    return html_content