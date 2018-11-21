from flask import Flask, request, session, g, redirect, \
    url_for, abort, render_template, flash,jsonify
import requests
from router import Router
import json

app = Flask(__name__, static_url_path='', static_folder="static")
app.config.from_object(__name__)

app.config.from_envvar('APP_CONFIG_FILE', silent=True)

MAPBOX_ACCESS_KEY = app.config['MAPBOX_ACCESS_KEY']
# Mapbox driving direction API call
ROUTE_URL = "https://api.mapbox.com/directions/v5/mapbox/driving/{0}.json?access_token={1}&overview=full&geometries=geojson"

r=Router()
def create_route_geojson(start_location,end_location):
    # Create a string with all the geo coordinates
    lat_longs =r.get_shortest_path(start_location,end_location)
    geojson={}
    geojson["properties"]={}
    geojson["type"]="Feature"
    geojson["geometry"]={}
    geojson["geometry"]["type"]="LineString"
    geojson["geometry"]["coordinates"]=lat_longs
    
    return geojson
    
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
    route_data=create_route_geojson((data['start_location']['lat'],data['start_location']['lng']),(data['end_location']['lat'],data['end_location']['lng']))
    return json.dumps(route_data)
