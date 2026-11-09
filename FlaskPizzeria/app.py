
from flask import Flask, request
from flask_cors import CORS
from database import conectar

app = Flask(__name__)
CORS(app)


@app.route('/')
def inicio():
    return 'API de Pizzeria funcionando'


@app.route('/api/prueba-db')
def prueba_db():

    conexion = conectar()

    if conexion.is_connected():
        conexion.close()
        return {'mensaje': 'Conexion a MySQL correcta'}

    return {'mensaje': 'Error de conexion'}


# GUARDAR PEDIDO
@app.route('/api/pedidos', methods=['POST'])
def guardar_pedido():

    datos = request.json

    conexion = conectar()
    cursor = conexion.cursor()

    try:
        sql_cliente = """
        INSERT INTO clientes (nombre, direccion, telefono)
        VALUES (%s, %s, %s)
        """

        valores_cliente = (
            datos['nombre'],
            datos['direccion'],
            datos['telefono']
        )

        cursor.execute(sql_cliente, valores_cliente)

        id_cliente = cursor.lastrowid

        sql_pedido = """
        INSERT INTO pedidos (id_cliente, fecha, total)
        VALUES (%s, %s, %s)
        """

        valores_pedido = (
            id_cliente,
            datos['fecha'],
            datos['total']
        )

        cursor.execute(sql_pedido, valores_pedido)

        id_pedido = cursor.lastrowid

        for pizza in datos['pizzas']:

            sql_detalle = """
            INSERT INTO detalle_pedido
            (id_pedido, tamano, ingredientes, cantidad, subtotal)
            VALUES (%s, %s, %s, %s, %s)
            """

            valores_detalle = (
                id_pedido,
                pizza['tamano'],
                pizza['ingredientes'],
                pizza['cantidad'],
                pizza['subtotal']
            )

            cursor.execute(sql_detalle, valores_detalle)

        conexion.commit()

        return {
            'mensaje': 'Pedido guardado correctamente',
            'id_pedido': id_pedido
        }

    except Exception as error:
        conexion.rollback()
        return {'error': str(error)}, 500

    finally:
        cursor.close()
        conexion.close()


# VENTAS POR DIA DE LA SEMANA
@app.route('/api/ventas/dia')
def ventas_dia():

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            DAYOFWEEK(fecha) AS dia,
            COUNT(*) AS cantidad_ventas,
            SUM(total) AS total_ventas
        FROM pedidos
        GROUP BY DAYOFWEEK(fecha)
        ORDER BY dia
    """)

    resultado = cursor.fetchall()

    cursor.close()
    conexion.close()

    return resultado


# VENTAS POR MES
@app.route('/api/ventas/mes')
def ventas_mes():

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            MONTH(fecha) AS mes,
            COUNT(*) AS cantidad_ventas,
            SUM(total) AS total_ventas
        FROM pedidos
        GROUP BY MONTH(fecha)
        ORDER BY mes
    """)

    resultado = cursor.fetchall()

    cursor.close()
    conexion.close()

    return resultado


# DETALLE DE UNA VENTA
@app.route('/api/pedidos/<int:id_pedido>')
def detalle_pedido(id_pedido):

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            pedidos.id_pedido,
            clientes.nombre,
            clientes.direccion,
            clientes.telefono,
            pedidos.fecha,
            pedidos.total,
            detalle_pedido.tamano,
            detalle_pedido.ingredientes,
            detalle_pedido.cantidad,
            detalle_pedido.subtotal
        FROM pedidos
        INNER JOIN clientes
            ON pedidos.id_cliente = clientes.id_cliente
        INNER JOIN detalle_pedido
            ON pedidos.id_pedido = detalle_pedido.id_pedido
        WHERE pedidos.id_pedido = %s
    """, (id_pedido,))

    resultado = cursor.fetchall()

    cursor.close()
    conexion.close()

    return resultado


if __name__ == '__main__':
    app.run(debug=True)
