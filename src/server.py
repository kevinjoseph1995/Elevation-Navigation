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

def create_geojson(coordinates):
    geojson={}
    geojson["properties"]={}
    geojson["type"]="Feature"
    geojson["geometry"]={}
    geojson["geometry"]["type"]="LineString"
    geojson["geometry"]["coordinates"]=coordinates

    return geojson

def create_data(start_location,end_location):
    # Create a string with all the geo coordinates
    (ele_latlong,shortest_latlong) =r.a_star(start_location,end_location)
    data={}
    data["elevation_route"]=create_geojson(ele_latlong)
    data["shortest_route"]=create_geojson(ele_latlong)
    if data["elevation_route"]==data["shortest_route"]:
        print("EQUAL")

    return data
    
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
    route_data=create_data((data['start_location']['lat'],data['start_location']['lng']),(data['end_location']['lat'],data['end_location']['lng']))
    return json.dumps(route_data)
