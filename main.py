from flask import Flask, render_template, request
import requests

app = Flask(__name__)
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

# Search news will be fetched dynamically based on the user's search query

@app.route("/")
def home_page():
    return "Hello, world"


@app.route("/login")
def login_page():
    pass


@app.route("/register")
def register_page():
    pass


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


if __name__ == "__main__":
    app.run(debug=True)