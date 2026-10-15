-- FinanUNI_Sec - Esquema Relacional de Base de Datos SQLite
-- Especificación de entidades acordadas en Etapa 2

-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_acceso TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK(rol IN ('cliente', 'auditor')),
    activo INTEGER NOT NULL DEFAULT 1
);

-- Tabla de Cuentas Bancarias
CREATE TABLE IF NOT EXISTS cuentas (
    id INTEGER PRIMARY KEY,
    titular_usuario_id INTEGER NOT NULL,
    saldo_centimos INTEGER NOT NULL CHECK(saldo_centimos >= 0 AND saldo_centimos <= 2147483647),
    FOREIGN KEY (titular_usuario_id) REFERENCES usuarios(id)
);

-- Tabla de Transferencias Históricas y Nuevas
CREATE TABLE IF NOT EXISTS transferencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cuenta_origen_id INTEGER NOT NULL,
    cuenta_destino_id INTEGER NOT NULL,
    monto_centimos INTEGER NOT NULL CHECK(monto_centimos > 0),
    fecha_utc TEXT NOT NULL,
    FOREIGN KEY (cuenta_origen_id) REFERENCES cuentas(id),
    FOREIGN KEY (cuenta_destino_id) REFERENCES cuentas(id)
);

-- Tabla de Sesiones Servidoras Opacas
CREATE TABLE IF NOT EXISTS sesiones (
    id TEXT PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    expiracion TEXT NOT NULL,
    estado TEXT NOT NULL CHECK(estado IN ('activa', 'revocada', 'expirada')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla de Eventos de Auditoría
CREATE TABLE IF NOT EXISTS eventos_auditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correlacion_id TEXT NOT NULL,
    fecha_utc TEXT NOT NULL,
    actor TEXT NOT NULL,
    accion TEXT NOT NULL,
    recurso TEXT NOT NULL,
    resultado TEXT NOT NULL,
    motivo TEXT
);
