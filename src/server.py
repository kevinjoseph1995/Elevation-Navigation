from flask import Flask, request, session, g, redirect, \
    url_for, abort, render_template, flash,jsonify
import requests
from router import Router


app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('APP_CONFIG_FILE', silent=True)

MAPBOX_ACCESS_KEY = app.config['MAPBOX_ACCESS_KEY']
# Mapbox driving direction API call
ROUTE_URL = "https://api.mapbox.com/directions/v5/mapbox/driving/{0}.json?access_token={1}&overview=full&geometries=geojson"

def create_route_url():
    # Create a string with all the geo coordinates
    r=Router()
    
    lat_longs =r.get_shortest_path((42.377041, -72.519681),(42.350070, -72.528798))
    # Create a url with the geo coordinates and access token
    url = ROUTE_URL.format(lat_longs, MAPBOX_ACCESS_KEY)
    return url

def get_route_data():
    # Get the route url
    route_url = create_route_url()
    # Perform a GET request to the route API
    result = requests.get(route_url)
    # Convert the return value to JSON
    data = result.json()
    
    # Create a geo json object from the routing data
    geometry = data["routes"][0]["geometry"]
    route_data={"geometry":geometry,"properties":{},"type":"Feature"}
    print(route_data)

    return route_data

@app.route('/mapbox_gl')
def mapbox_gl():
    route_data = get_route_data()

    return render_template('mapbox_gl.html', 
        ACCESS_KEY=MAPBOX_ACCESS_KEY,
        route_data = route_data
    )

@app.route('/data',methods = ['POST'])
def get_LatLong():

    """ get your data here and return it as json """
    print(request.get_json(force=True))
    return render_template(
        'mapbox_gl.html', 
        ACCESS_KEY=MAPBOX_ACCESS_KEY
    )


