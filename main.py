from fastapi import FastAPI
import mysql.connector
import os

app = FastAPI()

def get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )

TABLAS_PERMITIDAS = ["T_MAP_TIPO_DOCUMENTO"]

@app.get("/lista")
def obtener_lista(tabla: str, campo: str, campo_dv: str, campo_lbl: str):

    try:
        # 🔒 validar tabla
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
