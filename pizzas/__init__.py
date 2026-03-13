from flask import Blueprint

pizzas_bp = Blueprint(
    "pizzas", __name__, template_folder="templates", static_folder="static"
)

from . import routes
