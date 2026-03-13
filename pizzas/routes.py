from flask import render_template, request, redirect, url_for, flash, session
from . import pizzas_bp
from .forms import PizzaForm
from models import db, Clientes, Pedidos, Pizzas, DetallePedido
from datetime import datetime

PRECIOS = {"chica": 40, "mediana": 80, "grande": 120}
PRECIO_INGREDIENTE = 10


@pizzas_bp.route("/registrar", methods=["GET", "POST"])
def registrar():
    form = PizzaForm()

    if "pedido_temp" not in session:
        session["pedido_temp"] = {"cliente": {}, "pizzas": []}

    if request.method == "POST":
        if form.validate_on_submit():
            session["pedido_temp"]["cliente"] = {
                "nombre": form.nombre.data,
                "direccion": form.direccion.data,
                "telefono": form.telefono.data,
            }

            if not form.ingredientes.data:
                flash(
                    "Debes seleccionar al menos un ingrediente para la pizza", "warning"
                )
                return render_template(
                    "pizzas/registrar.html",
                    form=form,
                    pedido=session.get("pedido_temp", {"cliente": {}, "pizzas": []}),
                )

            cantidad = form.cantidad.data
            tamano = form.tamano.data
            ingredientes = form.ingredientes.data

            precio_por_pizza = PRECIOS[tamano] + (
                len(ingredientes) * PRECIO_INGREDIENTE
            )
            subtotal = precio_por_pizza * cantidad

            pizza_temp = {
                "id": len(session["pedido_temp"]["pizzas"]),
                "cantidad": cantidad,
                "tamaño": tamano,
                "ingredientes": list(ingredientes),
                "precio_unitario": precio_por_pizza,
                "subtotal": subtotal,
            }

            session["pedido_temp"]["pizzas"].append(pizza_temp)
            session.modified = True

            flash(f"Pizza agregada al pedido. Subtotal: ${subtotal}", "success")
            return redirect(url_for("pizzas.registrar"))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    campo_nombre = {
                        "nombre": "Nombre",
                        "direccion": "Dirección",
                        "telefono": "Teléfono",
                        "cantidad": "Cantidad",
                        "tamano": "Tamaño",
                        "ingredientes": "Ingredientes",
                    }.get(field, field)

                    flash(f"{campo_nombre}: {error}", "error")

            return render_template(
                "pizzas/registrar.html",
                form=form,
                pedido=session.get("pedido_temp", {"cliente": {}, "pizzas": []}),
            )

    return render_template(
        "pizzas/registrar.html",
        form=form,
        pedido=session.get("pedido_temp", {"cliente": {}, "pizzas": []}),
    )


@pizzas_bp.route("/quitar/<int:pizza_id>")
def quitar_pizza(pizza_id):
    if "pedido_temp" in session:
        pizzas = session["pedido_temp"]["pizzas"]
        session["pedido_temp"]["pizzas"] = [p for p in pizzas if p["id"] != pizza_id]
        session.modified = True
        flash("Pizza eliminada del pedido", "info")
    return redirect(url_for("pizzas.registrar"))


@pizzas_bp.route("/terminar", methods=["POST"])
def terminar():
    if "pedido_temp" not in session or not session["pedido_temp"]["pizzas"]:
        flash("No hay pizzas en el pedido", "error")
        return redirect(url_for("pizzas.registrar"))

    pedido_temp = session["pedido_temp"]

    if not pedido_temp["cliente"].get("nombre"):
        flash("Ingresa los datos del cliente", "error")
        return redirect(url_for("pizzas.registrar"))

    if not pedido_temp["cliente"].get("direccion"):
        flash("Ingresa la dirección del cliente", "error")
        return redirect(url_for("pizzas.registrar"))

    if not pedido_temp["cliente"].get("telefono"):
        flash("Ingresa el teléfono del cliente", "error")
        return redirect(url_for("pizzas.registrar"))

    total_pedido = sum(pizza["subtotal"] for pizza in pedido_temp["pizzas"])

    try:
        cliente_data = pedido_temp["cliente"]

        cliente = Clientes.query.filter_by(
            nombre=cliente_data["nombre"], telefono=cliente_data["telefono"]
        ).first()

        if not cliente:
            cliente = Clientes(
                nombre=cliente_data["nombre"],
                direccion=cliente_data["direccion"],
                telefono=cliente_data["telefono"],
            )
            db.session.add(cliente)
            db.session.flush()

        pedido = Pedidos(
            id_cliente=cliente.id_cliente,
            fecha=datetime.now().date(),
            total=total_pedido,
        )
        db.session.add(pedido)
        db.session.flush()

        for pizza_temp in pedido_temp["pizzas"]:
            ingredientes_str = ", ".join(pizza_temp["ingredientes"])

            pizza = Pizzas.query.filter_by(
                tamano=pizza_temp["tamaño"], ingredientes=ingredientes_str
            ).first()

            if not pizza:
                pizza = Pizzas(
                    tamano=pizza_temp["tamaño"],
                    ingredientes=ingredientes_str,
                    precio=pizza_temp["precio_unitario"],
                )
                db.session.add(pizza)
                db.session.flush()

            detalle = DetallePedido(
                id_pedido=pedido.id_pedido,
                id_pizza=pizza.id_pizza,
                cantidad=pizza_temp["cantidad"],
                subtotal=pizza_temp["subtotal"],
            )
            db.session.add(detalle)

        db.session.commit()

        session.pop("pedido_temp", None)

        flash(f"¡Pedido completado! Total a pagar: ${total_pedido}", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al guardar el pedido: {str(e)}", "error")

    return redirect(url_for("pizzas.registrar"))


@pizzas_bp.route("/ventas", methods=["GET", "POST"])
def ventas():
    ventas = []
    total_general = 0
    tipo_consulta = None
    valor_consulta = None

    if request.method == "POST":
        tipo_consulta = request.form.get("tipo_consulta")
        valor_consulta = request.form.get("valor_consulta")

        if tipo_consulta and valor_consulta:
            if tipo_consulta == "dia":
                dias = {
                    "lunes": 0,
                    "martes": 1,
                    "miercoles": 2,
                    "miércoles": 2,
                    "jueves": 3,
                    "viernes": 4,
                    "sabado": 5,
                    "sábado": 5,
                    "domingo": 6,
                }
                dia_num = dias.get(valor_consulta.lower().strip())

                if dia_num is not None:
                    todos_pedidos = Pedidos.query.all()
                    ventas = [v for v in todos_pedidos if v.fecha.weekday() == dia_num]

            elif tipo_consulta == "mes":
                meses = {
                    "enero": 1,
                    "febrero": 2,
                    "marzo": 3,
                    "abril": 4,
                    "mayo": 5,
                    "junio": 6,
                    "julio": 7,
                    "agosto": 8,
                    "septiembre": 9,
                    "octubre": 10,
                    "noviembre": 11,
                    "diciembre": 12,
                }
                mes_num = meses.get(valor_consulta.lower().strip())

                if mes_num is not None:
                    todos_pedidos = Pedidos.query.all()
                    ventas = [v for v in todos_pedidos if v.fecha.month == mes_num]

            total_general = sum(float(v.total) for v in ventas)

    return render_template(
        "pizzas/ventas.html",
        ventas=ventas,
        total_general=total_general,
        tipo_consulta=tipo_consulta,
        valor_consulta=valor_consulta,
    )


@pizzas_bp.route("/detalle/<int:pedido_id>")
def detalle_pedido(pedido_id):
    pedido = Pedidos.query.get_or_404(pedido_id)
    return render_template("pizzas/detalle_pedido.html", pedido=pedido)
