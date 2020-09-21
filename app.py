import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_meals")
def get_meals():
    meals = list(mongo.db.Meals.find())
    return render_template("meals.html", meals=meals)


@app.route("/")
@app.route("/browse_all")
def browse_all():
    meals = list(mongo.db.Meals.find())
    return render_template("browseall.html", meals=meals)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registration successful!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
              existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username")))
                return redirect(url_for(
                    "profile", username=session["user"]))
            else:
                # Invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return render_template("profile.html", username=username)


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_meal", methods=["GET", "POST"])
def add_meal():
    if request.method == "POST":
        meal = {
            "meal_name": request.form.get("meal_name"),
            "meal_time": request.form.get("meal_time"),
            "meal_method": request.form.getlist("meal_method"),
            "meal_ingredients": request.form.getlist("meal_ingredients"),
            "dairy_free": request.form.get("dairy_free"),
            "nut_free": request.form.get("nut_free"),
            "gluten_free": request.form.get("gluten_free"),
            "egg_free": request.form.get("egg_free"),
            "vegan": request.form.get("vegan"),
            "vegetarian": request.form.get("vegetarian"),
            "meal_img": request.form.get("meal_img"),
            "created_by": session["user"]

        }
        mongo.db.Meals.insert_one(meal)
        flash("Meal Successfully Added")
        return redirect(url_for("get_meals"))

    return render_template("add_meal.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
