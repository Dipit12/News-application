from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import razorpay
import random

app = Flask(__name__)
app.secret_key = 'fhjvnjkf7392839'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-user-collection.db"
db = SQLAlchemy(app)

# Razorpay client initialization
razorpay_client = razorpay.Client(auth=("rzp_test_d55qWYzgFGK2jX", "mN5RHZia7hjuTstAM3xG71Lc"))

# News API key
api_key = "d877aa30b64a41c281454f873fea11b2"

# Fetch general news
url_general = (
    "https://newsapi.org/v2/top-headlines?"
    "country=us&"
    f"apiKey={api_key}"
)
response1 = requests.get(url_general)
data1 = response1.json()
news_general = {}
for i in range(len(data1["articles"])):
    title = data1["articles"][i]["title"]
    description = data1["articles"][i]["description"]
    url = data1["articles"][i]["url"]
    news_general[title] = [description, url]


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)


with app.app_context():
    db.create_all()


@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(user_name=username, password=password).first()
        if user:
            flash("Login successful!", "success")
            return redirect(url_for("dashboard_page"))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("login_page"))
    return render_template("login.html")


@app.route("/register", methods=["POST"])
def register_page():
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    username = request.form["username"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    if password != confirm_password:
        flash("Passwords do not match", "danger")
        return redirect(url_for("login_page"))

    user_exists = User.query.filter_by(user_name=username).first()
    if user_exists:
        flash("Username already taken", "danger")
        return redirect(url_for("login_page"))

    new_user = User(first_name=first_name, last_name=last_name, user_name=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    flash("Registration successful! Please log in.", "success")
    return redirect(url_for("login_page"))


@app.route("/dashboard", methods=["GET"])
def dashboard_page():
    search_query = request.args.get("q", "").strip()
    if search_query:
        url_search = f"https://newsapi.org/v2/everything?q={search_query}&from=2024-04-30&sortBy=popularity&apiKey={api_key}"
        response2 = requests.get(url_search)
        data2 = response2.json()
        news_search = {}
        for i in range(len(data2["articles"])):
            title = data2["articles"][i]["title"]
            description = data2["articles"][i]["description"]
            url = data2["articles"][i]["url"]
            news_search[title] = [description, url]
        return render_template("dashboard.html", news=news_search)
    else:
        return render_template("dashboard.html", news=news_general)


@app.route('/payment', methods=['GET'])
def payment():
    try:
        amount = 100  # 100 paise
        currency = 'INR'
        order = razorpay_client.order.create(dict(amount=amount, currency=currency))
        return render_template('add.html', order=order)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/payment-callback', methods=['POST'])
def payment_callback():
    payload = request.form.to_dict()
    try:
        razorpay_client.utility.verify_payment_signature(payload)
        payment_id = payload['razorpay_payment_id']
        razorpay_client.payment.capture(payment_id)
        return jsonify({'success': True})
    except razorpay.errors.SignatureVerificationError:
        return jsonify({'success': False}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
