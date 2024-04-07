from lib.msfg_utils.msfgApp import msfg_route_app
import os
import json
from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__, template_folder="./templates",
            static_folder="./static", static_url_path='/static')
CORS(app)
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.variable_start_string = '||<-EL PSY CONGROO->||'
app.jinja_env.variable_end_string = '||<-EL PSY CONGROO->||'


msfg_route_app(app)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="IP:Port Configutation")
    parser.add_argument("--addr", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    app.run(host=args.addr, port=args.port)
