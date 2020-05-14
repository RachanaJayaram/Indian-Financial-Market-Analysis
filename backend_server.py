from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import Response
from nsepy import get_history
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import redis
import json
from datetime import date
import datetime

from backend_helper import extract_date, format_date
import constants

app = Flask(__name__)

# Web scraping for getting the symbols #
#url="https://www1.nseindia.com/products/content/derivatives/equities/fo_underlying_home.htm"

#do 'whereis chromedriver' and put the right path here
#"C:/bin/chromedriver"
#driver = webdriver.Chrome("C:/bin/chromedriver")
#driver.get(url)

#soup = BeautifulSoup(driver.page_source, "html.parser")
#table_rows = soup.find("div",{"class":"tabular-data-historic"}).find_all('tr')
#print(table_rows)

f = open("symbols.txt", "r")
symbols_string = f.read()

symbols=symbols_string.split(",")


# for tr in table_rows[5:-1]:
#     tds = tr.find_all("td")
#     symbol = str(tds[2].getText())[:-1]
#     #print(symbol)
#     symbols.append(symbol)

print("Number of symbols: ",len(symbols)) #144 scripts


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

    r = redis.Redis(host = 'localhost', port = 6379, db = 0, charset = "utf-8", decode_responses = True)

    # CACHE 1

    #Start date and End date are concatenated to form the hash
    key_date = str(start_date) + str(end_date)
    print(key_date)
    # Checking if hash  exists in cache
    get_cachedvalue = r.hgetall(key_date)

    if(get_cachedvalue):
    	print("Cache 1 hit")
    	falling = get_cachedvalue["falling"].split(";")
    	growing = get_cachedvalue["growing"].split(";")
    	print("falling: ", falling, len(falling), "growing: ", growing, len(growing))
    	return jsonify(result = {"falling" : falling, "growing" : growing})

    # CACHE 2

    # Day 0
    firstDate = date(1970,1,1)

    # find score of start_date
    min_score = (start_date - firstDate).days
    print("Minimum Score: ", min_score)

    # find score of end_date
    max_score = (end_date - firstDate).days
    print("Maximum Score: ", max_score)

    # get the records from cache 2
    get_cachedvalue2 = r.zrangebyscore("Cache2", min_score, max_score)

    # check if the end date of records in less than end_date
    eligible_records = []
    if(get_cachedvalue2):
    	for i in range(len(get_cachedvalue2)):
    		members = json.loads(get_cachedvalue2[i])
    		member_end = members["end"]
    		member_range = members["range"]
    		member_end = extract_date(member_end)
    		end_diff = (end_date - member_end).days
    		if(end_diff < 0):
    			continue
    		else:
    			eligible_records.append(members)
    		# choosing the record with maximum range
    		if(eligible_records):
    			best_record = (sorted(eligible_records, key = lambda i: i["range"], reverse = True))[0]
    			print("Chosen Record: ", best_record)

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

    # adding to cache1
    growing1 = growing
    falling1 = falling
    falling_string = ";".join(falling1)
    growing_string = ";".join(growing1)
    to_add = {"falling" : falling_string, "growing" : growing_string}
    r.hmset(key_date, to_add)

    # adding to cache2
    cache2_record = dict()
    cache2_record["start"] = str(start_date)
    cache2_record["end"] = str(end_date)
    cache2_record["range"] = (end_date - start_date).days
    cache2_record["growing"] = growing_string
    cache2_record["falling"] = falling_string

    record = json.dumps(cache2_record)

    r.zadd("Cache2", {record : min_score})

    # returning the output
    print("falling:",falling,len(falling),"growing:",growing,len(growing))
    return jsonify(result = {"falling" : falling, "growing" : growing})
    

if __name__ == "__main__":
    app.run(constants.URL, constants.PORT, debug=True,use_reloader=False)
