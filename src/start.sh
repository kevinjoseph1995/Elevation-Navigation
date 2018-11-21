
source activate elenav
export FLASK_APP=server.py
export FLASK_DEBUG=1
export APP_CONFIG_FILE=settings.py
python -m flask run
