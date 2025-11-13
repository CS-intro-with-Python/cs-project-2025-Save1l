from flask import Flask, render_template


app = Flask(
    __name__,
    template_folder="templates",
    static_folder="templates/source",
    static_url_path="/source",
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/pricing")
def pricing():
    return render_template("pricing.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)