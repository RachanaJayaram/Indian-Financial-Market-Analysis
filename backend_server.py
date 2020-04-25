from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import Response
from nsepy import get_history

from backend_helper import extract_date, format_date
import constants

app = Flask(__name__)

@app.route('/')
@app.route('/Index')
def index_page():
    """Default page."""
    return render_template('index.html')


@app.route(constants.GRAPH1_ENDPOINT)
def graphing1():
    """Render web page for API 1"""
    return render_template('graph1.html')


@app.route(constants.GRAPH2_ENDPOINT)
def graphing2():
    """Render web page for API 2"""
    #TBD
    return


@app.route(constants.API1_ENDPOINT, methods=["GET"])
def api_1():
    """API 1

    Given a script name and a time window, fetch it’s open and close in a graph."""

    symbol = request.args.get('symbol', 0, type=str)
    start = request.args.get('start', 0, type=str)
    end = request.args.get('end', 0, type=str)

    start_date = extract_date(start)
    end_date = extract_date(end)

    nse_df = get_history(symbol=symbol, start=start_date, end=end_date)

    return_data = {}
    return_data["Symbol"] = symbol
    return_data["Dates"] = [format_date(date) for date in nse_df.index.values]
    return_data["Open"] = nse_df["Open"].tolist()
    return_data["Close"] = nse_df["Close"].tolist()
    return_data["High"] = nse_df["High"].tolist()
    return_data["Low"] = nse_df["Low"].tolist()

    print(return_data)
    return jsonify(result = {"nse_data" : return_data})


@app.route(constants.API2_ENDPOINT, methods=["GET"])
def api_2():
    """API 2

    Given a time window, fetch and display the scripts which have only grown/fallen in previous x days."""
    # TBD.
    return


if __name__ == "__main__":
    app.run(constants.URL, constants.PORT, debug=True)
