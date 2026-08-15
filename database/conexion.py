import psycopg2
def obtener_conexion():
    return psycopg2.connect(host="localhost", database="storecontrol_db", user="postgres", password="admin123")
