from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import json
import get_ts_data as tsd

app = Flask(__name__)
CORS(app) # Cross-Origin Resource Sharing policy, adds the Access-Control-Allow-Origin Header in the response

# Using this global variable allows to have the two functions with different Responses.
# get_status() calls the generate_data() function and gives status updates to the browser console.
# When done, script.js calls the get_data() function. This returns the contents that where stored
# in the data_init global variable.
data_init = tsd.ts_data

@app.route("/get-status")
def get_status():
    """
    Calls the generate_data() function of the ts_data class.
    This allows for status-updates in the browser console.
    """
    global data_init

    # Get Arguments
    min_lon = float(request.args.get("minLon"))
    min_lat = float(request.args.get("minLat"))
    max_lon = float(request.args.get("maxLon"))
    max_lat = float(request.args.get("maxLat"))
    api_key = str(request.args.get("apiKey"))

    data_init = tsd.ts_data(api_key, [min_lon, min_lat, max_lon, max_lat]) 

    response = Response(
        data_init.generate_data(), 
        mimetype="text/event-stream",
    )

    return response

@app.route("/get-data")
def get_data():
    """
    Return the data from the global variable data_init as .json
    """

    global data_init

    data = data_init.get_data()

    response = Response(
        json.dumps(data, indent=4), # Browsers may remove newlines and indents.
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=data.json"},
    )
    return response

if __name__ == "__main__":
    app.run()