from flask import Flask, render_template, redirect, url_for
from datetime import datetime
import requests

app = Flask(__name__)

def format_launches(raw_launches):
    for launch in raw_launches:
        iso = launch['window_start']
        dt = datetime.fromisoformat(iso.replace('Z', '+00:00'))
        launch['format_datetime'] = dt.strftime('%B %d, %Y at %I:%M %p UTC')
    return raw_launches

@app.route('/')
def homepage():
    return redirect(url_for('launches'))

@app.route('/launches')
def launches():
    response = requests.get('https://ll.thespacedevs.com/2.2.0/launch/upcoming/?limit=10')
    data = response.json()
    raw_launches = data['results'] # List of dicts representing launches
    formatted_launches = format_launches(raw_launches)

    return render_template('launches.html', launches=formatted_launches)


if __name__ == '__main__':
    app.run(debug=True)