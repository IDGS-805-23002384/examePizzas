from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField, SelectMultipleField, widgets
from wtforms.validators import DataRequired


class PizzaForm(FlaskForm):
    nombre = StringField(
        "Nombre", validators=[DataRequired(message="Ingresa el nombre")]
    )
    direccion = StringField(
        "Dirección", validators=[DataRequired(message="Ingresa la dirección")]
    )
    telefono = StringField(
        "Teléfono", validators=[DataRequired(message="Ingresa un número de teléfono")]
    )
    cantidad = IntegerField(
        "Cantidad", validators=[DataRequired(message="Ingresa la cantidad de pizzas")]
    )
    tamano = RadioField(
        "Tamaño",
        choices=[("chica", "Chica"), ("mediana", "Mediana"), ("grande", "Grande")],
        validators=[DataRequired(message="Selecciona el tamaño")],
    )
    ingredientes = SelectMultipleField(
        "Ingredientes",
        choices=[("jamon", "Jamón"), ("piña", "Piña"), ("champinones", "Champiñones")],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
    )
