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
            s.PK_PEDIDO AS numero_solicitud,
            s.FK_PERSONA_SOLICITUD AS persona_solicitud,
            s.FK_TIPO_PUBLICO AS tipo_publico,
            s.FK_EFA_PEDIDO AS ruc_efa,
            s.FK_ADMINISTRADO_PEDIDO AS ruc_administrado,
            s.TX_REGISTRO_SIGED AS registro_siged,
            s.TX_NRO_DOC AS numero_documento,
            s.FE_FEC_SOLICITUD AS fecha_solicitud,
            s.TX_AREAOD AS area_ode,
            s.TX_TEMA_PEDIDO AS tema_pedido,
            s.TX_ACCIONES AS acciones,
            s.TX_OBSERVACIONES AS observaciones,

            tg.TX_DESCRIPCION AS tema_general,
            te.TX_DESCRIPCION AS tema_especifico,
            st.TX_DESCRIPCION AS subtema,

            s.FK_SUBTEMA_SOLICITUD AS subtema_id,

            s.TX_ESTADO AS estado_pedido,
            s.TX_ESTADO AS usuario,
            s.FE_FE_REGISTRO AS fecha_registro

        FROM T_MVP_SOLICITUD_AFA s

        LEFT JOIN T_MAP_SUBTEMA st 
            ON st.PK_SUBTEMA = s.FK_SUBTEMA_SOLICITUD

        LEFT JOIN T_MAP_TEMA_ESPECIFICO te 
            ON te.PK_TEMA_ESPECIFICO = st.FK_ESPECIFICO_SUBTEMA

        LEFT JOIN T_MAP_TEMA_GENERAL tg 
            ON tg.PK_TEMA_GENERAL = te.FK_GENERAL_ESPECIFICO

        ORDER BY s.PK_PEDIDO DESC
        LIMIT 500
        """

        cursor.execute(query)
        data = cursor.fetchall()

        # 🔥 formatear fechas
        for row in data:
            if row["fecha_solicitud"]:
                row["fecha_solicitud"] = str(row["fecha_solicitud"])[:10]
            if row["fecha_registro"]:
                row["fecha_registro"] = str(row["fecha_registro"])[:10]

        cursor.close()
        conn.close()

        return data

    except Exception as e:
        return {"error": str(e)}
