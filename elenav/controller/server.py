from flask import Flask, request, session, g, redirect, \
    url_for, abort, render_template, flash,jsonify
import requests
import json
import elenav.controller.algorithms as algorithms
import os
import elenav.model

app = Flask(__name__, static_url_path = '', static_folder = "../view/static", template_folder = "../view/templates")
app.config.from_object(__name__)

app.config.from_envvar('APP_CONFIG_FILE', silent=True)

MAPBOX_ACCESS_KEY = 'pk.eyJ1Ijoia2V2aW5qb3NlcGgxOTk1IiwiYSI6ImNqbzUxc2kwaDAybm4zanRjdm9mbndqZW8ifQ.wdJv5gB84BWVy1dAoNN6ew'
# Mapbox driving direction API call
ROUTE_URL = "https://api.mapbox.com/directions/v5/mapbox/driving/{0}.json?access_token={1}&overview=full&geometries=geojson"



def create_geojson(coordinates):
    geojson = {}
    geojson["properties"] = {}
    geojson["type"] = "Feature"
    geojson["geometry"] = {}
    geojson["geometry"]["type"] = "LineString"
    geojson["geometry"]["coordinates"] = coordinates

    return geojson

def create_data(start_location,end_location):
    # Create a string with all the geo coordinates
    M = elenav.model.graph_model.Model()
    G = M.get_graph(start_location,end_location)    
    shortestDist = algorithms.get_shortest_path(G, start_location, end_location)
    ele_latlong,ascent,descent = algorithms.a_star(G, start_location, end_location, shortestDist)    
    
    data={"elevation_route" : create_geojson(ele_latlong)}  
    data["ascent"] = ascent
    data["descent"] = descent
    return data
    
@app.route('/mapbox_gl_new')
def mapbox_gl_new():    
    """ get your data here and return it as json """    

    return render_template(
        'mapbox_gl_new.html', 
        ACCESS_KEY=MAPBOX_ACCESS_KEY
    )


@app.route('/route',methods=['POST'])
def get_route():    
    data = request.get_json(force=True)
    route_data = create_data((data['start_location']['lat'],data['start_location']['lng']),\
                             (data['end_location']['lat'],data['end_location']['lng']))
    return json.dumps(route_data)
