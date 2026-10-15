/**
 * FinanUNI_Sec - Control de Formularios y Demostración de Defensas (Etapa 6)
 * CBS07 Seguridad de Software 2026-II
 */

function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

document.addEventListener('DOMContentLoaded', () => {
    // 1. Manejo del Formulario de Login
    const formLogin = document.getElementById('form-login');
    if (formLogin) {
        formLogin.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username')?.value;
            const password = document.getElementById('password')?.value;
            
            showStatusFeedback('Verificando credenciales con Argon2id...', 'info');

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nombre_acceso: username, password: password })
                });
                
                const data = await response.json();
                if (response.ok) {
                    showStatusFeedback(`[+] Inicio de sesión seguro exitoso. Bienvenido ${data.usuario.nombre_acceso} (${data.usuario.rol}). Redirigiendo...`, 'info');
                    setTimeout(() => { window.location.href = '/movimientos'; }, 800);
                } else {
                    showStatusFeedback(`[!] Rechazo de autenticación (${response.status}): ${data.error || 'Credenciales inválidas'}`, 'warning');
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
                const token = getCsrfToken();
                const response = await fetch('/api/logout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-Token': token
                    }
                });
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

            showStatusFeedback('Consultando movimientos protegidos en la base de datos...', 'info');

            try {
                const response = await fetch(`/api/movimientos?${params.toString()}`);
                const data = await response.json();
                
                if (response.ok) {
                    renderMovimientos(data.movimientos);
                    showStatusFeedback(`
                        <strong>🛡️ CONSULTA PARAMETRIZADA EXITOSA (RF05):</strong><br>
                        Se recuperaron ${data.total} movimientos dentro del alcance autorizado del usuario activo.
                    `, 'info');
                } else {
                    if (clienteId && (clienteId.includes('OR') || clienteId.includes('='))) {
                        showStatusFeedback(`
                            <strong>🛡️ MITIGACIÓN EXITOSA DE SQL INJECTION (RF05 / T03 / T04):</strong><br>
                            El servidor detectó la entrada maliciosa <code>${clienteId}</code> y la rechazó con HTTP ${response.status}:<br>
                            <em>${data.error}</em><br>
                            La base de datos y los datos de otros clientes quedaron totalmente protegidos.
                        `, 'warning');
                    } else {
                        showStatusFeedback(`[!] Error (${response.status}): ${data.error}`, 'warning');
                    }
                }
            } catch (error) {
                showStatusFeedback(`Error de conexión con el servidor: ${error.message}`, 'warning');
            }
        });

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

            showStatusFeedback(`Consultando transferencia #${transferId} con control RBAC y propiedad...`, 'info');

            try {
                const response = await fetch(`/api/transferencias/${encodeURIComponent(transferId)}`);
                const data = await response.json();

                if (response.ok) {
                    renderDetalleTransferencia(data.transferencia);
                    showStatusFeedback(`Transferencia autorizada #${data.transferencia.id} recuperada exitosamente.`, 'info');
                } else if (response.status === 404) {
                    hideDetalleCard();
                    showStatusFeedback(`
                        <strong>🛡️ MITIGACIÓN EXITOSA DE IDOR (AM02 / RF06 / T05):</strong><br>
                        El servidor respondió con <strong>HTTP 404 Recurso no encontrado</strong> uniforme.<br>
                        Se bloqueó el acceso a transferencias ajenas y se previno la enumeración de identificadores.
                    `, 'warning');
                } else {
                    hideDetalleCard();
                    showStatusFeedback(`[!] Rechazo (${response.status}): ${data.error}`, 'warning');
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
            const csrfToken = getCsrfToken();

            showStatusFeedback('Enviando solicitud con validación estricta y token CSRF...', 'info');

            try {
                const response = await fetch('/api/transferencias', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-Token': csrfToken
                    },
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
                        <em>Defensa por diseño: Ante la falta del motor nativo, la transacción no se ejecuta ni se modifican saldos.</em>
                    `, 'pending');
                } else if (response.status === 403) {
                    showStatusFeedback(`
                        <strong>🛡️ CONTROL DE AUTORIZACIÓN (RBAC / Propiedad):</strong><br>
                        ${data.error}
                    `, 'warning');
                } else if (response.status === 400) {
                    showStatusFeedback(`
                        <strong>🛡️ VALIDACIÓN DE ENTRADA Y PREVENCIÓN DE DESBORDE (RF05 / T07):</strong><br>
                        ${data.error}<br>
                        <em>El backend interceptó y rechazó el monto antes de cualquier llamada al motor C.</em>
                    `, 'warning');
                } else if (response.ok) {
                    showStatusFeedback(`Transferencia confirmada de forma atómica: ${JSON.stringify(data)}`, 'info');
                } else {
                    showStatusFeedback(`[!] Rechazo (${response.status}): ${data.error}`, 'warning');
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
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No se encontraron movimientos autorizados.</td></tr>';
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
