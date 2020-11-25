# Dependencies
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, and_, or_, distinct, desc
from datetime import datetime, timedelta
from flask import Flask, jsonify

# Reflect base and create session to query
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})
Base = automap_base()
Base.prepare(engine, reflect=True)
session = Session(engine)

# Define classes names
Measurement = Base.classes.measurement
Station = Base.classes.station

# Get the max and min date to know where the user can query from on the last 2 queries
max_date = session.query(func.max(Measurement.date)).scalar()
min_date = session.query(func.min(Measurement.date)).scalar()

# First query
prec_data = session.query(Measurement).filter(Measurement.date >= "2016-08-23").group_by(Measurement.date).all()
prec_dict = {}
for x in prec_data:
    prec_dict[f"{x.date}"] = x.prcp

# Second query
stations = session.query(Station).all()
station_list = []
for x in stations:
    station_list.append(x.station)

# Third query
active_station = session.query(Measurement.station, func.count(Measurement.station).label("tobs")).group_by(Measurement.station).order_by(desc("tobs")).first()[0]
temp_obs = session.query(Measurement).filter(and_(Measurement.station == active_station, Measurement.date >= "2016-08-23")).all()
temp_list = {}
for temp in temp_obs:
    temp_list[temp.date] = temp.tobs

app = Flask(__name__)

@app.route("/")
def home():
    return(f"""<h1>Hello. This is the main webpage.</h1> <br>
    Here are the routes available: <br>
    <ol>
        <li><a target="_blank" href="/api/v1.0/precipitation">/api/v1.0/precipitation</a></li>
        <li><a target="_blank" href="/api/v1.0/stations">/api/v1.0/stations</a></li>
        <li><a target="_blank" href="/api/v1.0/tobs">/api/v1.0/tobs</a></li>
        <li><a target="_blank" href="/api/v1.0/start">/api/v1.0/start</a></li>
        <li><a target="_blank" href="/api/v1.0/start/end">/api/v1.0/start/end</a></li>
    </ol>""")

@app.route("/api/v1.0/precipitation")
def prec():
    return  jsonify(prec_dict)

@app.route("/api/v1.0/stations")
def stns ():
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    minimum = session.query(func.min(Measurement.tobs).filter(Measurement.date >= start)).all()[0][0]
    maximum = session.query(func.max(Measurement.tobs).filter(Measurement.date >= start)).all()[0][0]
    average = session.query(func.avg(Measurement.tobs).filter(Measurement.date >= start)).all()[0][0]
    list_result = [minimum,maximum,average]
    
    try:
        minimum + 1
        return jsonify(list_result)
    except:
        return(f"""The date you entered is not found.
        Please try with dates from {min_date} to {max_date}""")

@app.route("/api/v1.0/<start>/<end>")
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