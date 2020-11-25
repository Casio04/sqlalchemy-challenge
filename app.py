# Dependencies
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, and_, or_, distinct, desc
from datetime import datetime, timedelta
from flask import Flask, jsonify, request

# Reflect base and create session to query
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})
Base = automap_base()
Base.prepare(engine, reflect=True)
session = Session(engine)

# Define classes names
Measurement = Base.classes.measurement
Station = Base.classes.station

#  Initiate Flask
app = Flask(__name__)

# Create first route including only the links to the other routes
@app.route("/")
def home():
    max_date = session.query(func.max(Measurement.date)).scalar()
    min_date = session.query(func.min(Measurement.date)).scalar()
    return(f"""<section style="font-family:Arial">
    <h1 style="color:darkblue">Hello. This is the API index.</h1>
    <p> The minimum date available is: <b>{min_date}</b>. <br>
    The maximum date available is: <b>{max_date}</b>
    <h3 style="color:darkblue">Here are the routes available: </h3>
    <ol>
        <li><a target="_blank" href="/api/v1.0/precipitation">/api/v1.0/precipitation </a> - Daily precipitation data from the last 12 months available</li>
        <li><a target="_blank" href="/api/v1.0/stations">/api/v1.0/stations</a> - The list of available stations as of today</li>
        <li><a target="_blank" href="/api/v1.0/tobs">/api/v1.0/tobs</a> - Daily temperatures observed data from the last 12 months available</li>
        <li><a target="_blank" href="/api/v1.0/start/end">/api/v1.0/start/end</a> - Returns the maximum, minimum and average temperature for a range of time.</li>
    </ol>
    </section>""")

@app.route("/api/v1.0/precipitation")
def prec():
    # Filtering the data from the last available year in the database
    prec_data = session.query(Measurement).filter(Measurement.date >= "2016-08-23").group_by(Measurement.date).all()
    prec_dict = {}
    # Looping through every date available and turning that into a JSON
    for x in prec_data:
        prec_dict[f"{x.date}"] = x.prcp
    return  jsonify(prec_dict)

@app.route("/api/v1.0/stations")
def stns ():
    # Get all the different stations 
    stations = session.query(Station).all()
    station_list = []

    # Add the stations to a JSON
    for x in stations:
        station_list.append(x.station)
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Query all the temperatures observed for the last year available
    active_station = session.query(Measurement.station, func.count(Measurement.station).label("tobs")).group_by(Measurement.station).order_by(desc("tobs")).first()[0]
    temp_obs = session.query(Measurement).filter(and_(Measurement.station == active_station, Measurement.date >= "2016-08-23")).all()
    temp_list = {}

    #  Insert Date and Temperature Observed as a JSON
    for temp in temp_obs:
        temp_list[temp.date] = temp.tobs
    return jsonify(temp_list)

#  Creating two routes to query for the same filter
@app.route("/api/v1.0/<start>", endpoint="onearg")
@app.route("/api/v1.0/<start>/<end>", endpoint="twoargs")
def start_date(start, end):
    # I get the minimum and maximum dates so it can show later a message for the user if he picks an out of scope date.
    max_date = session.query(func.max(Measurement.date)).scalar()
    min_date = session.query(func.min(Measurement.date)).scalar()

    # If the endpoint uses only start date, then the end date is set to 2099 so it can filter the next 80 years from now
    if request.endpoint=="onearg":
        end = "2099-12-31"

    #  Then we query for both start and end date and store the values 
    minimum = session.query(func.min(Measurement.tobs).filter(and_(Measurement.date >= start, Measurement.date <= end))).all()[0][0]
    maximum = session.query(func.max(Measurement.tobs).filter(and_(Measurement.date >= start, Measurement.date <= end))).all()[0][0]
    average = session.query(func.avg(Measurement.tobs).filter(and_(Measurement.date >= start, Measurement.date <= end))).all()[0][0]
    list_result = [minimum,maximum,average]
   
    try:
        #  I try to sum 1 to minimum value to know the request was succesful, because it will bring an integer
        #  if not it will fail and will return a message
        minimum + 1
        return jsonify(list_result)
    except:
        # The fail message will tell the User which dates are available dependin on the min and max date calculated before
        return(f"""The date you entered is not found.
        Please try with dates from {min_date} to {max_date}""")


def star_end(start,end):
    min_date = session.query(func.min(Measurement.tobs).filter(and_(Measurement.date >= start, Measurement.date <= end))).all()[0][0]
    max_date = session.query(func.max(Measurement.tobs).filter(and_(Measurement.date >= start, Measurement.date <= end))).all()[0][0]
    avg_date = session.query(func.avg(Measurement.tobs).filter(and_(Measurement.date >= start, Measurement.date <= end))).all()[0][0]
    range_result = [min_date,max_date,avg_date]

    try:
        min_date + 1
        return jsonify(range_result)
    except:
        return(f"""The date you entered is not found.
        Please try with dates from {min_date} to {max_date}""")

if __name__ == "__main__":
    app.run(debug=True)