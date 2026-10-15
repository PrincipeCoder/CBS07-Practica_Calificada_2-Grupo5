"""
Módulo de acceso y conexión a base de datos SQLite (FinanUNI_Sec).
Gestiona el ciclo de vida de la conexión y la carga de la semilla acordada.
"""
import os
import sqlite3
from flask import g, current_app
from app.security.crypto import hash_password

def get_db_connection():
    """
    Obtiene la conexión a la base de datos SQLite para la petición actual en FinanUNI_Sec.
    
    Comprobamos si ya existe una conexión en el almacén de contexto 'g':
    - Si no existe, creamos una nueva conexión hacia el archivo en instance/finanuni_sec.db.
    - Activamos row_factory = sqlite3.Row para acceder a columnas por nombre.
    - Habilitamos claves foráneas con PRAGMA foreign_keys = ON para integridad referencial.
    """
    if '_database' not in g:
        db_path = current_app.config.get('DATABASE_PATH', os.path.join('instance', 'finanuni_sec.db'))
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        g._database = conn
    return g._database

def close_db_connection(exception=None):
    """
    Cierra la conexión al finalizar el ciclo de vida de la petición HTTP.
    """
    db = g.pop('_database', None)
    if db is not None:
        db.close()

def init_db(connection=None):
    """
    Crea las tablas a partir del esquema DDL definido en schema.sql.
    """
    conn = connection or get_db_connection()
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()

def load_seed_data(connection=None):
    """
    Carga los datos iniciales y reproducibles del laboratorio:
    - Usuarios: 1 Ana (cliente), 2 Bruno (cliente), 3 Auditor (auditor).
    - Cuentas: 101 (Ana, S/ 50,000.00), 102 (Bruno, S/ 30,000.00), 103 (Bruno, S/ 10,000.00).
    - Transferencias: 1051, 1052 (ajena a Ana), 1053.
    """
    conn = connection or get_db_connection()
    cursor = conn.cursor()

    # 1. Usuarios con hashes Argon2id
    pass_ana = hash_password("ana123")
    pass_bruno = hash_password("bruno123")
    pass_auditor = hash_password("auditor123")

    cursor.execute("""
        INSERT OR REPLACE INTO usuarios (id, nombre_acceso, password_hash, rol, activo)
        VALUES 
            (1, 'ana', ?, 'cliente', 1),
            (2, 'bruno', ?, 'cliente', 1),
            (3, 'auditor', ?, 'auditor', 1);
    """, (pass_ana, pass_bruno, pass_auditor))

    # 2. Cuentas bancarias con saldos iniciales en céntimos
    cursor.execute("""
        INSERT OR REPLACE INTO cuentas (id, titular_usuario_id, saldo_centimos)
        VALUES 
            (101, 1, 5000000),
            (102, 2, 3000000),
            (103, 2, 1000000);
    """)

    # 3. Transferencias históricas acordadas
    cursor.execute("""
        INSERT OR REPLACE INTO transferencias (id, cuenta_origen_id, cuenta_destino_id, monto_centimos, fecha_utc)
        VALUES 
            (1051, 101, 102, 10000, '2026-10-14 10:00:00'),
            (1052, 102, 103, 20000, '2026-10-14 11:30:00'),
            (1053, 103, 102, 5000, '2026-10-14 12:15:00');
    """)

    conn.commit()

def reset_db(connection=None):
    """
    Reinicia completamente la base de datos de Sec a la semilla acordada.
    """
    conn = connection or get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF;")
    cursor.execute("DELETE FROM transferencias;")
    cursor.execute("DELETE FROM cuentas;")
    cursor.execute("DELETE FROM sesiones;")
    cursor.execute("DELETE FROM usuarios;")
    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    init_db(conn)
    load_seed_data(conn)
