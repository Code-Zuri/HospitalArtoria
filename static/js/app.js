/**
 * Hospital Artoria - Funciones JavaScript principales
 * Proporciona utilidades para CRUD, manejo de formularios, modales y actualización de UI.
 */

// ============================================================
// Configuración y estado
// ============================================================
const API_BASE = ''; // puede sobrescribirse según el módulo
let currentModule = ''; // pacientes, medicos, citas, etc.
let editingId = null;

// ============================================================
// Funciones de utilidad
// ============================================================

/**
 * Realiza una petición fetch con manejo de errores.
 */
async function apiFetch(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Error ${response.status}: ${errorText}`);
        }
        return await response.json();
    } catch (error) {
        mostrarMensaje(error.message, 'error');
        throw error;
    }
}

/**
 * Muestra mensajes al usuario (toast, alert o div).
 */
function mostrarMensaje(mensaje, tipo = 'info') {
    // Si existe un contenedor de mensajes, lo usamos; si no, alert.
    const container = document.getElementById('mensaje-container');
    if (container) {
        const div = document.createElement('div');
        div.className = `mensaje mensaje-${tipo}`;
        div.textContent = mensaje;
        container.appendChild(div);
        setTimeout(() => div.remove(), 5000);
    } else {
        alert(mensaje);
    }
}

/**
 * Obtiene el valor de un campo de formulario por su nombre.
 */
function getFormValue(formId, fieldName) {
    const form = document.getElementById(formId);
    if (!form) return null;
    const input = form.querySelector(`[name="${fieldName}"]`);
    return input ? input.value : null;
}

/**
 * Convierte un formulario en un objeto de datos.
 */
function formToObject(formId) {
    const form = document.getElementById(formId);
    if (!form) return {};
    const data = new FormData(form);
    const obj = {};
    for (let [key, value] of data.entries()) {
        obj[key] = value;
    }
    return obj;
}

/**
 * Llena un formulario con datos para edición.
 */
function fillForm(formId, data) {
    const form = document.getElementById(formId);
    if (!form) return;
    for (const key in data) {
        const input = form.querySelector(`[name="${key}"]`);
        if (input) {
            input.value = data[key] || '';
        }
    }
}

/**
 * Limpia un formulario.
 */
function resetForm(formId) {
    const form = document.getElementById(formId);
    if (form) form.reset();
    editingId = null;
}

/**
 * Abre un modal (simple, sin librerías externas).
 */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        modal.classList.add('modal-active');
    }
}

/**
 * Cierra un modal.
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('modal-active');
    }
    resetForm(modalId + '-form');
}

// ============================================================
// Funciones CRUD genéricas
// ============================================================

/**
 * Lista los registros de un módulo en el contenedor especificado.
 * @param {string} module - nombre del módulo (pacientes, medicos, etc.)
 * @param {string} containerId - id del elemento donde se mostrará la lista
 * @param {Function} renderRow - función que recibe un item y devuelve HTML de fila
 */
async function listarRegistros(module, containerId, renderRow) {
    const container = document.getElementById(containerId);
    if (!container) return;
    try {
        const data = await apiFetch(`/${module}/api`);
        if (data.length === 0) {
            container.innerHTML = '<p>No hay registros.</p>';
            return;
        }
        // Crear tabla
        let html = `<table class="tabla-datos">
            <thead>
                <tr>
                    ${Object.keys(data[0]).filter(k => k !== '_id').map(k => `<th>${k.replace(/_/g, ' ')}</th>`).join('')}
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>`;
        data.forEach(item => {
            html += `<tr>`;
            // Mostrar todas las columnas excepto _id
            for (const key in item) {
                if (key === '_id') continue;
                html += `<td>${item[key] || ''}</td>`;
            }
            html += `<td>
                <button onclick="editarRegistro('${module}', '${item._id}')">Editar</button>
                <button onclick="eliminarRegistro('${module}', '${item._id}')">Eliminar</button>
            </td>`;
            html += `</tr>`;
        });
        html += `</tbody></table>`;
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = `<p>Error al cargar datos: ${error.message}</p>`;
    }
}

/**
 * Crea un nuevo registro.
 */
async function crearRegistro(module, formId, modalId, callback) {
    const data = formToObject(formId);
    if (!data || Object.keys(data).length === 0) {
        mostrarMensaje('No hay datos en el formulario', 'error');
        return;
    }
    try {
        await apiFetch(`/${module}/api`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
        mostrarMensaje('Registro creado exitosamente', 'success');
        closeModal(modalId);
        resetForm(formId);
        if (callback) callback();
        else location.reload(); // recarga simple
    } catch (error) {
        // ya manejado en apiFetch
    }
}

/**
 * Edita un registro (carga datos en el formulario y abre modal).
 */
async function editarRegistro(module, id) {
    try {
        const data = await apiFetch(`/${module}/api/${id}`);
        const formId = `${module}-form`;
        const modalId = `${module}-modal`;
        editingId = id;
        fillForm(formId, data);
        openModal(modalId);
        // Cambiar título del modal
        const modalTitle = document.querySelector(`#${modalId} .modal-title`);
        if (modalTitle) modalTitle.textContent = 'Editar registro';
    } catch (error) {
        mostrarMensaje('Error al cargar datos para edición', 'error');
    }
}

/**
 * Actualiza un registro existente.
 */
async function actualizarRegistro(module, formId, modalId, callback) {
    if (!editingId) {
        mostrarMensaje('No hay registro seleccionado para editar', 'error');
        return;
    }
    const data = formToObject(formId);
    try {
        await apiFetch(`/${module}/api/${editingId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
        mostrarMensaje('Registro actualizado', 'success');
        closeModal(modalId);
        resetForm(formId);
        editingId = null;
        if (callback) callback();
        else location.reload();
    } catch (error) {
        // ya manejado
    }
}

/**
 * Elimina un registro con confirmación.
 */
async function eliminarRegistro(module, id) {
    if (!confirm('¿Estás seguro de eliminar este registro?')) return;
    try {
        await apiFetch(`/${module}/api/${id}`, {
            method: 'DELETE'
        });
        mostrarMensaje('Registro eliminado', 'success');
        location.reload();
    } catch (error) {
        // ya manejado
    }
}

/**
 * Inicializa los eventos de un módulo:
 * - Botón para abrir modal de creación.
 * - Formulario con submit para crear/actualizar.
 */
function initModule(module, containerId, renderRow) {
    currentModule = module;
    const formId = `${module}-form`;
    const modalId = `${module}-modal`;
    const btnNuevo = document.getElementById(`btn-nuevo-${module}`);
    const btnGuardar = document.getElementById(`btn-guardar-${module}`);

    // Cargar lista inicial
    listarRegistros(module, containerId, renderRow);

    // Botón "Nuevo"
    if (btnNuevo) {
        btnNuevo.addEventListener('click', function() {
            resetForm(formId);
            editingId = null;
            const modalTitle = document.querySelector(`#${modalId} .modal-title`);
            if (modalTitle) modalTitle.textContent = 'Nuevo registro';
            openModal(modalId);
        });
    }

    // Botón guardar (crear o actualizar)
    if (btnGuardar) {
        btnGuardar.addEventListener('click', function() {
            if (editingId) {
                actualizarRegistro(module, formId, modalId, () => {
                    listarRegistros(module, containerId, renderRow);
                });
            } else {
                crearRegistro(module, formId, modalId, () => {
                    listarRegistros(module, containerId, renderRow);
                });
            }
        });
    }

    // Cerrar modal con botón de cierre o fondo
    const modal = document.getElementById(modalId);
    if (modal) {
        const closeBtn = modal.querySelector('.modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => closeModal(modalId));
        }
        modal.addEventListener('click', function(e) {
            if (e.target === this) closeModal(modalId);
        });
    }
}

// ============================================================
// Inicialización después de que el DOM esté listo
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    // Detectar módulo por la URL o por el contenido de la página
    const path = window.location.pathname;
    let module = '';
    if (path.includes('/pacientes')) module = 'pacientes';
    else if (path.includes('/medicos')) module = 'medicos';
    else if (path.includes('/citas')) module = 'citas';
    else if (path.includes('/consultas')) module = 'consultas';
    else if (path.includes('/diagnosticos')) module = 'diagnosticos';
    else if (path.includes('/tratamientos')) module = 'tratamientos';
    else if (path.includes('/hospitalizaciones')) module = 'hospitalizaciones';
    else if (path.includes('/reportes')) module = 'reportes';
    else if (path.includes('/machine-learning')) module = 'ml';

    // Si es un módulo con listado, inicializar
    if (module && !['reportes', 'ml'].includes(module)) {
        const containerId = `${module}-list`;
        // Verificar que el contenedor existe en la página
        if (document.getElementById(containerId)) {
            initModule(module, containerId, null);
        }
    }
});

// ============================================================
// Funciones para gráficos y ML (se pueden usar en reportes)
// ============================================================
function crearGrafico(ctx, tipo, datos, opciones = {}) {
    return new Chart(ctx, {
        type: tipo,
        data: datos,
        options: opciones
    });
}

/**
 * Función para cargar indicadores en el dashboard (se usa en reportes.html)
 */
function cargarIndicadores(url, containerId) {
    fetch(url)
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById(containerId);
            if (!container) return;
            let html = '';
            for (const key in data) {
                html += `<div class="kpi-item"><span class="kpi-label">${key}</span><span class="kpi-value">${data[key]}</span></div>`;
            }
            container.innerHTML = html;
        })
        .catch(err => console.error('Error cargando indicadores:', err));
}