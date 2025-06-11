from flask import Flask, render_template, redirect, url_for, request
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
    provider_filter = request.args.get('provider')
    location_filter = request.args.get('location')

    response = requests.get('https://ll.thespacedevs.com/2.2.0/launch/upcoming/?limit=10')
    data = response.json()
    raw_launches = data['results'] # List of dicts representing launches

    if provider_filter:
        raw_launches = [l for l in raw_launches if l['launch_service_provider']['name'] == provider_filter]
    if location_filter:
        raw_launches = [l for l in raw_launches if l['pad']['name'] == location_filter]
    
    formatted_launches = format_launches(raw_launches)
    return render_template('launches.html', launches=formatted_launches)


# REMOVE BEFORE LIVE IMPLEMENTATION
if __name__ == '__main__':
    app.run(debug=True)