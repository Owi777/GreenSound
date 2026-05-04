from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

app.secret_key = "greensound_secret_key"
ADMIN_PASSWORD = "admin123"


def get_product_data():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products ORDER BY id DESC LIMIT 1")
    product = cursor.fetchone()

    cursor.execute("SELECT * FROM product_images WHERE product_id = ?", (product["id"],))
    images = cursor.fetchall()

    cursor.execute("SELECT * FROM product_features WHERE product_id = ?", (product["id"],))
    features = cursor.fetchall()

    conn.close()
    return product, images, features


def get_about_info():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM about_info LIMIT 1")
    about = cursor.fetchone()

    conn.close()
    return about


@app.route("/")
def home():
    product, images, features = get_product_data()
    return render_template("index.html", product=product, images=images, features=features)


@app.route("/product")
def product():
    product, images, features = get_product_data()
    return render_template("product.html", product=product, images=images, features=features)


@app.route("/about")
def about():
    about = get_about_info()
    return render_template("about.html", about=about)


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/submit_contact", methods=["POST"])
def submit_contact():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO contact_messages (name, email, message) VALUES (?, ?, ?)",
        (name, email, message)
    )

    conn.commit()
    conn.close()

    return redirect("/contact")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")

        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect("/admin/messages")
        else:
            return render_template("admin_login.html", error="Nepareiza parole")

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect("/admin/login")


@app.route("/admin/messages")
def admin_messages():
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM contact_messages")
    messages = cursor.fetchall()

    conn.close()

    return render_template("admin_messages.html", messages=messages)


@app.route("/delete_message/<int:id>")
def delete_message(id):
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM contact_messages WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect("/admin/messages")


if __name__ == "__main__":
    app.run(debug=True)