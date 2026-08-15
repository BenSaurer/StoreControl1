from flask import Flask, jsonify, render_template, request
import psycopg2

app = Flask(__name__)

def obtener_conexion():
    return psycopg2.connect(
        host="localhost",
        database="storecontrol_db",
        user="postgres",
        password="admin123"
    )

@app.route("/")
def inicio():
    return render_template("index.html")

# Operación READ & CREATE: Obtener y Registrar Productos
@app.route("/api/productos", methods=["GET", "POST"])
def gestionar_productos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    # Asegurar la existencia de la tabla en PostgreSQL antes de operar
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id_producto SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                precio NUMERIC(10,2) NOT NULL CHECK (precio > 0),
                stock INT NOT NULL CHECK (stock >= 0)
            );
        """)
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        return jsonify({"error": f"Fallo al inicializar tabla: {str(e)}"}), 500
    
    if request.method == "GET":
        try:
            cursor.execute("SELECT id_producto, nombre, precio, stock FROM productos ORDER BY id_producto")
            productos = []
            for fila in cursor.fetchall():
                productos.append({
                    "id": fila[0],
                    "nombre": fila[1],
                    "precio": float(fila[2]),
                    "stock": fila[3]
                })
            return jsonify(productos), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            conexion.close()

    if request.method == "POST":
        datos = request.get_json()
        nombre = datos.get("nombre")
        precio = datos.get("precio")
        stock = datos.get("stock")
        
        try:
            cursor.execute(
                "INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s) RETURNING id_producto",
                (nombre, precio, stock)
            )
            conexion.commit()
            return jsonify({"mensaje": "Producto creado exitosamente"}), 201
        except Exception as e:
            conexion.rollback()
            return jsonify({"error": f"Fallo de integridad: {str(e)}"}), 400
        finally:
            cursor.close()
            conexion.close()

# Operación UPDATE & DELETE: Modificar y Eliminar un Producto por su ID
@app.route("/api/productos/<int:id_producto>", methods=["PUT", "DELETE"])
def alterar_producto(id_producto):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    if request.method == "PUT":
        datos = request.get_json()
        nombre = datos.get("nombre")
        precio = datos.get("precio")
        stock = datos.get("stock")
        
        try:
            cursor.execute(
                "UPDATE productos SET nombre = %s, precio = %s, stock = %s WHERE id_producto = %s",
                (nombre, precio, stock, id_producto)
            )
            conexion.commit()
            return jsonify({"mensaje": "Producto actualizado de forma correcta"}), 200
        except Exception as e:
            conexion.rollback()
            return jsonify({"error": f"Fallo de actualización: {str(e)}"}), 400
        finally:
            cursor.close()
            conexion.close()

    if request.method == "DELETE":
        try:
            cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
            conexion.commit()
            return jsonify({"mensaje": "Producto eliminado del inventario"}), 200
        except Exception as e:
            conexion.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    app.run(debug=True)


