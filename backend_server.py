from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import Response
from nsepy import get_history
from bs4 import BeautifulSoup
from selenium import webdriver
import time

from backend_helper import extract_date, format_date
import constants

app = Flask(__name__)

# Web scraping for getting the symbols #
url="https://www1.nseindia.com/products/content/derivatives/equities/fo_underlying_home.htm"

#do 'whereis chromedriver' and put the right path here
driver = webdriver.Chrome("/usr/bin/chromedriver")
driver.get(url)

soup = BeautifulSoup(driver.page_source, "html.parser")
table_rows = soup.find("div",{"class":"tabular-data-historic"}).find_all('tr')
#print(table_rows)
symbols=[]

for tr in table_rows[5:-1]:
    tds = tr.find_all("td")
    symbol = str(tds[2].getText())[:-1]
    #print(symbol)
    symbols.append(symbol)

print(len(symbols)) #144 scripts


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
    return render_template('graph2.html')


@app.route(constants.API1_ENDPOINT, methods=["GET"])
def api_1():
    """API 1

    Given a script name and a time window, fetch it’s open and close in a graph."""

    symbol = request.args.get('symbol', 0, type=str)
    start = request.args.get('start', 0, type=str)
    end = request.args.get('end', 0, type=str)
    print(start)

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
    start = request.args.get('start', 0, type=str)
    end = request.args.get('end', 0, type=str)

    start_date = extract_date(start)
    end_date = extract_date(end)

    growing=[]
    falling=[]

    print("starting check")

    for symbol in symbols:
        nse_df = get_history(symbol=symbol, start=start_date, end=end_date)
        close=nse_df["Close"].tolist()
        if(symbol=="PVR"):
            print(close)
        current_falling=0
        if(len(close)>1):
            for day in range(len(close[:-1])):
                if(close[day]>close[day+1]):
                    current_falling+=1
            if(len(close)-1==current_falling):
                falling.append(symbol)
            elif(current_falling==0):
                growing.append(symbol)


    print("falling:",falling,len(falling),"growing:",growing,len(growing))
    return jsonify(result = {"falling" : falling, "growing" : growing})





if __name__ == "__main__":
    app.run(constants.URL, constants.PORT, debug=True,use_reloader=False)
