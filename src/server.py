from flask import Flask, request, session, g, redirect, \
    url_for, abort, render_template, flash,jsonify
import requests
from router import Router
import json

app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('APP_CONFIG_FILE', silent=True)

MAPBOX_ACCESS_KEY = app.config['MAPBOX_ACCESS_KEY']
# Mapbox driving direction API call
ROUTE_URL = "https://api.mapbox.com/directions/v5/mapbox/driving/{0}.json?access_token={1}&overview=full&geometries=geojson"


def create_route_url(start_location,end_location):
    # Create a string with all the geo coordinates
    r=Router()
    lat_longs =r.get_shortest_path(start_location,end_location)
    # Create a url with the geo coordinates and access token
    url = ROUTE_URL.format(lat_longs, MAPBOX_ACCESS_KEY)
    return url

def get_route_data(route_url):   
    # Perform a GET request to the route API
    result = requests.get(route_url)
    # Convert the return value to JSON
    data = result.json()
    
    # Create a geo json object from the routing data        
    geometry = data["routes"][0]["geometry"]
    route_data={"geometry":geometry,"properties":{},"type":"Feature"}   

    return route_data



@app.route('/mapbox_gl')
def mapbox_gl():    
    """ get your data here and return it as json """    

    return render_template(
        'mapbox_gl.html', 
        ACCESS_KEY=MAPBOX_ACCESS_KEY
        
    )


@app.route('/route',methods=['POST'])
def get_route():    
    data=request.get_json(force=True)      
    route_url=create_route_url((data['start_location']['lat'],data['start_location']['lng']),(data['end_location']['lat'],data['end_location']['lng']))
    route_data=get_route_data(route_url) 
    return json.dumps(route_data)
