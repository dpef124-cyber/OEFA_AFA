from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import os

app = FastAPI()

# 🔥 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        ssl_disabled=False  # 👈 importante para Aiven / SSL
    )

TABLAS_PERMITIDAS = [
    "T_MAP_TIPO_DOCUMENTO",
    "T_MAP_REGION",
    "T_MAP_SEXO",
    "T_MAP_TEMA_GENERAL",
    "T_MAP_SUB_SECTOR",
    "T_MAP_TIPO_PUBLICO",
    "T_MAP_AREA"
]

# =========================================
# 🔹 ENDPOINT 1 (YA TENÍAS)
# =========================================
@app.get("/lista")
def obtener_lista(tabla: str, campo: str, campo_dv: str, campo_lbl: str):

    try:
        if tabla not in TABLAS_PERMITIDAS:
            return {"error": "Tabla no permitida"}

        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        query = f"""
            SELECT DISTINCT
                {campo} AS value,
                {campo_dv} AS dataValue,
                {campo_lbl} AS text
            FROM {tabla}
            WHERE {campo_lbl} IS NOT NULL
            LIMIT 100
        """

        print("QUERY:", query)

        cursor.execute(query)
        data = cursor.fetchall()

        print("RESULT:", data)

        cursor.close()
        conn.close()

        return data

    except Exception as e:
        return {"error": str(e)}


# =========================================
# 🔹 ENDPOINT 2 (NUEVO)
# =========================================
@app.get("/solicitudes")
def obtener_solicitudes():

    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                PK_PEDIDO AS numero_solicitud,
                FK_PERSONA_SOLICITUD AS persona_solicitud,
                FK_TIPO_PUBLICO AS tipo_publico,
                FK_EFA_PEDIDO AS ruc_efa,
                FK_ADMINISTRADO_PEDIDO AS ruc_administrado,
                TX_REGISTRO_SIGED AS registro_siged,
                TX_NRO_DOC AS numero_documento,
                FE_FEC_SOLICITUD AS fecha_solicitud,
                TX_AREAOD AS area_ode,
                TX_TEMA_PEDIDO AS tema_pedido,
                TX_ACCIONES AS acciones,
                TX_OBSERVACIONES AS observaciones,
                FK_SUBTEMA_SOLICITUD AS subtema,
                TX_ESTADO AS estado_pedido,
                TX_ESTADO AS usuario,
                FE_FE_REGISTRO AS fecha_registro
            FROM T_MVP_SOLICITUD_AFA
            ORDER BY PK_PEDIDO DESC
            LIMIT 500
        """

        print("QUERY SOLICITUDES:", query)

        cursor.execute(query)
        data = cursor.fetchall()

        # 🔥 Formateo de fechas (igual que GAS)
        for row in data:
            if row["fecha_solicitud"]:
                row["fecha_solicitud"] = str(row["fecha_solicitud"])[:10]
            if row["fecha_registro"]:
                row["fecha_registro"] = str(row["fecha_registro"])[:10]

        cursor.close()
        conn.close()

        print("RESULT SOLICITUDES:", len(data))

        return data

    except Exception as e:
        return {"error": str(e)}
