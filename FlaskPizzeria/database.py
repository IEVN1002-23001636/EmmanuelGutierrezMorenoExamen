
import mysql.connector

def conectar():

    conexion = mysql.connector.connect(
        host="localhost",
        user="emmanuel",
        password="root",
        database="pizzeria"
    )

    return conexion
