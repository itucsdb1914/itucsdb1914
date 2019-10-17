from flask import Flask
from flask import render_template


app = Flask(__name__)


example_event = [
    {
        'eventName': 'Joker',
        'eventDate': '20.10.2019',
        'eventPlace': 'Cinemaximum',
        'eventPrice': '20'
    },
    {
        'eventName': 'Batman',
        'eventDate': '20.11.2029',
        'eventPlace': 'Cinepink',
        'eventPrice': '10'
    }
]




@app.route("/")
@app.route("/home")
def home_page():
    return render_template('home.html', events= example_event)


@app.route("/about")
def about_page():
    return render_template('about.html')


if __name__ == "__main__":
    app.run(debug=True)
