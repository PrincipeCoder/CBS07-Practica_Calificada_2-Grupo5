/**
 * FinanUNI_Vuln - Control de Formularios y Demostración de Vulnerabilidades (Etapa 5)
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
            
            showStatusFeedback('Verificando credenciales...', 'info');

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nombre_acceso: username, password: password })
                });
                
                const data = await response.json();
                if (response.ok) {
                    showStatusFeedback(`[+] Inicio de sesión exitoso. Bienvenido ${data.usuario.nombre_acceso} (${data.usuario.rol}). Redirigiendo...`, 'info');
                    setTimeout(() => { window.location.href = '/movimientos'; }, 800);
                } else {
                    showStatusFeedback(`[!] Error (${response.status}): ${data.error || 'Credenciales inválidas'}`, 'warning');
                }
            } catch (error) {
                showStatusFeedback(`Error de conexión con el servidor: ${error.message}`, 'warning');
            }
        });
    }

    // Botón de Logout en Navbar
    const btnLogoutNav = document.getElementById('btn-logout-nav');
    if (btnLogoutNav) {
        btnLogoutNav.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/logout', { method: 'POST' });
                if (response.ok) {
                    window.location.href = '/login';
                }
            } catch (err) {
                console.error("Error al cerrar sesión:", err);
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

            showStatusFeedback('Consultando movimientos en la base de datos...', 'info');

            try {
                const response = await fetch(`/api/movimientos?${params.toString()}`);
                const data = await response.json();
                
                if (response.ok) {
                    renderMovimientos(data.movimientos);
                    if (clienteId && (clienteId.includes('OR') || clienteId.includes('='))) {
                        showStatusFeedback(`
                            <strong>⚠️ DEMOSTRACIÓN EXITOSA DE SQL INJECTION (AM01 / CWE-89):</strong><br>
                            El filtro malicioso <code>${clienteId}</code> alteró la consulta concatenada.<br>
                            Se han recuperado <strong>${data.total}</strong> movimientos de la base de datos,
                            exponiendo transferencias de clientes ajenos.
                        `, 'warning');
                    } else {
                        showStatusFeedback(`Consulta exitosa: se encontraron ${data.total} movimientos.`, 'info');
                    }
                } else {
                    showStatusFeedback(`[!] Error (${response.status}): ${data.error}`, 'warning');
                }
            } catch (error) {
                showStatusFeedback(`Error de conexión con el servidor: ${error.message}`, 'warning');
            }
        });

        // Cargar automáticamente si el usuario ya está autenticado
        if (document.getElementById('tabla-movimientos-body')) {
            formMovimientos.dispatchEvent(new Event('submit'));
        }
    }

    // 3. Manejo de Búsqueda de Detalle de Transferencia por ID
    const formDetalle = document.getElementById('form-detalle');
    if (formDetalle) {
        formDetalle.addEventListener('submit', async (e) => {
            e.preventDefault();
            const transferId = document.getElementById('transfer_id')?.value;
            if (!transferId) {
                showStatusFeedback('Ingrese un identificador de transferencia.', 'warning');
                return;
            }

            showStatusFeedback(`Consultando transferencia #${transferId}...`, 'info');

            try {
                const response = await fetch(`/api/transferencias/${encodeURIComponent(transferId)}`);
                const data = await response.json();

                if (response.ok) {
                    renderDetalleTransferencia(data.transferencia);
                    const t = data.transferencia;
                    // Detectar si se está evidenciando IDOR (1052 es de Bruno y Ana es cliente 1)
                    if (t.id === 1052 && t.titular_origen_id !== 1 && t.titular_destino_id !== 1) {
                        showStatusFeedback(`
                            <strong>⚠️ DEMOSTRACIÓN EXITOSA DE IDOR (AM02 / CWE-639):</strong><br>
                            El endpoint omitió verificar si el usuario es titular o participante.<br>
                            Se ha consultado la transferencia #${t.id} perteneciente a <strong>${t.titular_origen}</strong>
                            sin contar con autorización sobre el recurso.
                        `, 'warning');
                    } else {
                        showStatusFeedback(`Ficha de transferencia #${t.id} recuperada exitosamente.`, 'info');
                    }
                } else {
                    hideDetalleCard();
                    showStatusFeedback(`[!] Respuesta (${response.status}): ${data.error || 'Transferencia no encontrada'}`, 'warning');
                }
            } catch (error) {
                showStatusFeedback(`Error de conexión con el servidor: ${error.message}`, 'warning');
            }
        });
    }

    // 4. Manejo de Nueva Transferencia
    const formTransferencia = document.getElementById('form-transferencia');
    if (formTransferencia) {
        formTransferencia.addEventListener('submit', async (e) => {
            e.preventDefault();
            const origen = document.getElementById('cuenta_origen_id')?.value;
            const destino = document.getElementById('cuenta_destino_id')?.value;
            const montoSoles = document.getElementById('monto_soles')?.value;

            showStatusFeedback('Enviando solicitud de transferencia...', 'info');

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
                if (response.status === 501) {
                    showStatusFeedback(`
                        <strong>ℹ️ Dependencia pendiente del motor C (Código HTTP 501):</strong><br>
                        ${data.error || 'El motor numérico conversor_c aún no ha sido provisto por el Integrante 2.'}<br>
                        <em>No se alteraron saldos ni se completó la operación en ausencia del motor.</em>
                    `, 'pending');
                } else if (response.ok) {
                    showStatusFeedback(`Transferencia confirmada: ${JSON.stringify(data)}`, 'info');
                } else {
                    showStatusFeedback(`[!] Error (${response.status}): ${data.error}`, 'warning');
                }
            } catch (error) {
                showStatusFeedback(`Error de conexión: ${error.message}`, 'warning');
            }
        });
    }
});

function renderMovimientos(movimientos) {
    const tbody = document.getElementById('tabla-movimientos-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (!movimientos || movimientos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No se encontraron movimientos registrados.</td></tr>';
        return;
    }

    movimientos.forEach(m => {
        const tr = document.createElement('tr');
        const soles = (m.monto_centimos / 100).toFixed(2);
        tr.innerHTML = `
            <td><strong>#${m.id}</strong></td>
            <td>Cuenta ${m.cuenta_origen_id} (${m.titular_origen})</td>
            <td>Cuenta ${m.cuenta_destino_id} (${m.titular_destino})</td>
            <td><strong>S/ ${soles}</strong></td>
            <td><small>${m.fecha_utc}</small></td>
            <td>
                <button class="btn btn-secondary" style="padding: 3px 8px; font-size: 0.78rem;" onclick="verDetalleDirecto(${m.id})">
                    Ver Ficha
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function verDetalleDirecto(id) {
    window.location.href = `/transferencias/detalle?id=${id}`;
}

function renderDetalleTransferencia(t) {
    const card = document.getElementById('ficha-detalle-transferencia');
    if (!card) return;
    card.style.display = 'block';

    document.getElementById('det-id').textContent = `#${t.id}`;
    document.getElementById('det-origen').textContent = `Cuenta ${t.cuenta_origen_id} (${t.titular_origen})`;
    document.getElementById('det-destino').textContent = `Cuenta ${t.cuenta_destino_id} (${t.titular_destino})`;
    document.getElementById('det-monto-soles').textContent = `S/ ${(t.monto_centimos / 100).toFixed(2)}`;
    document.getElementById('det-monto-centimos').textContent = `${t.monto_centimos} céntimos`;
    document.getElementById('det-fecha').textContent = t.fecha_utc;
}

function hideDetalleCard() {
    const card = document.getElementById('ficha-detalle-transferencia');
    if (card) card.style.display = 'none';
}

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
