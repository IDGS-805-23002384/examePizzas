from flask import Flask, render_template, redirect, url_for
from config import DevelopmentConfig
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from models import db
from pizzas import pizzas_bp

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config["SECRET_KEY"] = "clave-secreta"

db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

app.register_blueprint(pizzas_bp)


@app.route("/")
def index():
    return redirect(url_for("pizzas.registrar"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
