from flask import Flask, request, session, g, redirect, \
    url_for, abort, render_template, flash,jsonify

app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('APP_CONFIG_FILE', silent=True)

MAPBOX_ACCESS_KEY = app.config['MAPBOX_ACCESS_KEY']

@app.route('/mapbox_gl')
def mapbox_gl():
    return render_template(
        'mapbox_gl.html', 
        ACCESS_KEY=MAPBOX_ACCESS_KEY
    )

@app.route('/data',methods = ['POST'])
def get_LatLong():

    """ get your data here and return it as json """
    print(request.get_json(force=True))
    return render_template(
        'mapbox_gl.html', 
        ACCESS_KEY=MAPBOX_ACCESS_KEY
    )