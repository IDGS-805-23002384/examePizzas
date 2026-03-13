from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Clientes(db.Model):
    __tablename__ = "clientes"
    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    
    pedidos = db.relationship("Pedidos", back_populates="cliente")


class Pizzas(db.Model):
    __tablename__ = "pizzas"
    id_pizza = db.Column(db.Integer, primary_key=True)
    tamano = db.Column(db.String(20), nullable=False)
    ingredientes = db.Column(db.String(200), nullable=False)
    precio = db.Column(db.Numeric(8, 2), nullable=False)
    
    detalles = db.relationship("DetallePedido", back_populates="pizza")


class Pedidos(db.Model):
    __tablename__ = "pedidos"
    id_pedido = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("clientes.id_cliente"), nullable=False)
    fecha = db.Column(db.Date, default=datetime.datetime.now)
    total = db.Column(db.Numeric(10, 2), nullable=False)

    cliente = db.relationship("Clientes", back_populates="pedidos")
    detalles = db.relationship("DetallePedido", back_populates="pedido")


class DetallePedido(db.Model):
    __tablename__ = "detalle_pedido"
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedidos.id_pedido"), nullable=False)
    id_pizza = db.Column(db.Integer, db.ForeignKey("pizzas.id_pizza"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    pedido = db.relationship("Pedidos", back_populates="detalles")
    pizza = db.relationship("Pizzas", back_populates="detalles")