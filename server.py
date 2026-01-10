from flask import Flask, render_template, request
from logger import setup_logger

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="templates/source",
    static_url_path="/source",
)

setup_logger(app)

app.config['SQLALCHEMY_ECHO'] = True


@app.before_request
def log_request_info():
    app.logger.info(
        'Request: %s %s from %s',
        request.method,
        request.path,
        request.remote_addr
    )

@app.route("/")
def index():
    return render_template("index.html", active_page=None)


@app.route("/home")
def home():
    return render_template("home.html", active_page="home")


@app.route("/pricing")
def pricing():
    return render_template("pricing.html", active_page="pricing")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)