/**
 * FinanUNI_Sec - Control de Formularios y Manejo de Estados Pendientes (HTTP 501)
 * CBS07 Seguridad de Software 2026-II
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Manejo del Formulario de Login
    const formLogin = document.getElementById('form-login');
    if (formLogin) {
        formLogin.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username')?.value;
            const password = document.getElementById('password')?.value;
            
            showStatusFeedback('Enviando solicitud de inicio de sesión...', 'info');

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nombre_acceso: username, password: password })
                });
                
                const data = await response.json();
                handlePendingResponse(response.status, data, 'Inicio de sesión');
            } catch (error) {
                showStatusFeedback(`Error de conexión con el servidor: ${error.message}`, 'warning');
            }
        });
    }

    // 2. Manejo del Formulario de Filtros de Movimientos
    const formMovimientos = document.getElementById('form-movimientos');
    if (formMovimientos) {
        formMovimientos.addEventListener('submit', async (e) => {
            e.preventDefault();
            const clienteId = document.getElementById('cliente_id')?.value;
            const fechaDesde = document.getElementById('fecha_desde')?.value;
            const fechaHasta = document.getElementById('fecha_hasta')?.value;
            const montoMin = document.getElementById('monto_min_soles')?.value;
            const montoMax = document.getElementById('monto_max_soles')?.value;

            const params = new URLSearchParams();
            if (clienteId) params.append('cliente_id', clienteId);
            if (fechaDesde) params.append('fecha_desde', fechaDesde);
            if (fechaHasta) params.append('fecha_hasta', fechaHasta);
            if (montoMin) params.append('monto_min_soles', montoMin);
            if (montoMax) params.append('monto_max_soles', montoMax);

            showStatusFeedback('Consultando movimientos en la API...', 'info');

            try {
                const response = await fetch(`/api/movimientos?${params.toString()}`);
                const data = await response.json();
                handlePendingResponse(response.status, data, 'Consulta de movimientos');
            } catch (error) {
                showStatusFeedback(`Error de conexión con el servidor: ${error.message}`, 'warning');
            }
        });
    }

    // 3. Manejo del Formulario de Búsqueda de Detalle por ID
    const formDetalle = document.getElementById('form-detalle');
    if (formDetalle) {
        formDetalle.addEventListener('submit', async (e) => {
            e.preventDefault();
            const transferId = document.getElementById('transfer_id')?.value;
            if (!transferId) {
                showStatusFeedback('Por favor ingrese un ID de transferencia válido.', 'warning');
                return;
            }

            showStatusFeedback(`Consultando transferencia #${transferId} en la API...`, 'info');

            try {
                const response = await fetch(`/api/transferencias/${encodeURIComponent(transferId)}`);
                const data = await response.json();
                handlePendingResponse(response.status, data, `Detalle de transferencia #${transferId}`);
            } catch (error) {
                showStatusFeedback(`Error de conexión con el servidor: ${error.message}`, 'warning');
            }
        });
    }

    // 4. Manejo del Formulario de Nueva Transferencia
    const formTransferencia = document.getElementById('form-transferencia');
    if (formTransferencia) {
        formTransferencia.addEventListener('submit', async (e) => {
            e.preventDefault();
            const origen = document.getElementById('cuenta_origen_id')?.value;
            const destino = document.getElementById('cuenta_destino_id')?.value;
            const montoSoles = document.getElementById('monto_soles')?.value;

            showStatusFeedback('Enviando solicitud de transferencia financiera...', 'info');

            try {
                const response = await fetch('/api/transferencias', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        cuenta_origen_id: origen,
                        cuenta_destino_id: destino,
                        monto_soles: montoSoles
                    })
                });

                const data = await response.json();
                handlePendingResponse(response.status, data, 'Orden de transferencia');
            } catch (error) {
                showStatusFeedback(`Error de conexión con el servidor: ${error.message}`, 'warning');
            }
        });
    }

    // 5. Botón de Test de Salud (Health Page)
    const btnCheckHealth = document.getElementById('btn-check-health');
    if (btnCheckHealth) {
        btnCheckHealth.addEventListener('click', async () => {
            const container = document.getElementById('health-json-output');
            if (container) container.textContent = 'Consultando endpoint /api/health...';

            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                if (container) {
                    container.textContent = JSON.stringify(data, null, 2);
                }
            } catch (error) {
                if (container) {
                    container.textContent = `Error al consultar /api/health: ${error.message}`;
                }
            }
        });
    }
});

/**
 * Procesa la respuesta de un endpoint pendiente (HTTP 501)
 * y muestra la retroalimentación sin anunciar éxito ni operaciones ejecutadas.
 */
function handlePendingResponse(statusCode, data, actionLabel) {
    if (statusCode === 501) {
        const mensaje = data.mensaje || 'Funcionalidad pendiente de implementación';
        const detalle = data.detalle || 'Esta operación será implementada en las siguientes fases del proyecto.';
        
        showStatusFeedback(`
            <strong>⚠️ Respuesta del Servidor [HTTP 501 - No Implementado]</strong><br>
            <strong>Operación solicitada:</strong> ${actionLabel}<br>
            <strong>Estado:</strong> ${mensaje}<br>
            <strong>Información:</strong> ${detalle}<br>
            <em>Aviso de seguridad: Ningún dato fue modificado, no se crearon sesiones ni se alteraron saldos.</em>
        `, 'pending');
    } else {
        showStatusFeedback(`Respuesta recibida del servidor [Código ${statusCode}]: ${JSON.stringify(data)}`, 'info');
    }
}

/**
 * Despliega el contenedor de estado visual en la página.
 */
function showStatusFeedback(htmlContent, type = 'info') {
    const feedbackBox = document.getElementById('status-feedback');
    if (!feedbackBox) return;

    feedbackBox.className = 'alert';
    if (type === 'pending') {
        feedbackBox.classList.add('alert-status-pending');
    } else if (type === 'warning') {
        feedbackBox.classList.add('alert-warning');
    } else {
        feedbackBox.classList.add('alert-info');
    }

    feedbackBox.innerHTML = htmlContent;
    feedbackBox.style.display = 'block';
    feedbackBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
