from collections import Counter
from flask import Flask, render_template, redirect, url_for, request
from datetime import datetime
import requests
import random

app = Flask(__name__)

def format_launches(raw_launches):
    '''
    Takes the iso time of each launch and creates a new 
    more natural date format.
    '''
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
    page = int(request.args.get('page', 1))
    per_page = 10

    response = requests.get('https://ll.thespacedevs.com/2.2.0/launch/upcoming/?limit=30')
    data = response.json()
    raw_launches = data['results'] # List of dicts representing launches

    if provider_filter:
        raw_launches = [l for l in raw_launches if l['launch_service_provider']['name'] == provider_filter]
    if location_filter:
        raw_launches = [l for l in raw_launches if l['pad']['name'] == location_filter]

    # Pagination logic
    total_launches = len(raw_launches)
    total_pages = (total_launches + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_pages = raw_launches[start:end]

    # Globe display data
    location_counter = Counter()
    map_locals = []
    for launch in raw_launches:
        pad = launch['pad']
        lat = float(pad['latitude'])
        lon = float(pad['longitude'])
        key = (lat, lon)

        count = location_counter[key]
        location_counter[key] += 1
        scatter_strength = 0.3  # Scatter duplicates slightly on globe

        lat_offset = lat + (random.uniform(-scatter_strength, scatter_strength) * count)
        lon_offset = lon + (random.uniform(-scatter_strength, scatter_strength) * count)


        map_locals.append({
            'latitude': lat_offset,
            'longitude': lon_offset,
            'provider': launch['launch_service_provider']['name'],
            'mission': launch['mission']['name'],
            'status': 'Launched' if launch['status']['name'] == 'Launch Successful' else 'Upcoming'
        })

    formatted_launches = format_launches(paginated_pages)
    return render_template(
        'launches.html',
        launches=formatted_launches,
        map_locals=map_locals,
        page=page,
        total_pages=total_pages
    )


# REMOVE BEFORE LIVE IMPLEMENTATION
if __name__ == '__main__':
    app.run(debug=True)