import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create dictionary with date as the key and precipitation as the value
    precip_data = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    #put return into list
    precipitation_dict = []
    for date, prcp in precip_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        precipitation_dict.append(prcp_dict)

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the data for all stations
    stations = session.query(Station.station).all()

    session.close()
    #use list comprehension to pull first element from list of lists
    indy_stations = [station[0] for station in stations]

    return jsonify(indy_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create query and define variable for last date in the set
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #set first four digts of date field as a variable and change to int for formatting
    year = int(latest_date[0][:4])
    #set variable for 2016 dates...this represents 2017-1 which equals 2016
    last_year = year-1
    #change last year back to string for query purpose...also adding characters 4-10 
    #from the most recent date above
    last_years=str(last_year)+latest_date[0][4:10]
    #query to obtain data
    year_of_dates = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date>=last_years).all()
    #close session
    session.close()

    tobs_list = []
    for date, tobs in year_of_dates:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def range(start):
    
    session = Session(engine)
    
    #query for dates between the start and end dates, which are entered in the URL
    lowest = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).first()
    average = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).first()
    maximum = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).first()

    #put items into list
    tobs_returns = [lowest, average, maximum]
    return jsonify(tobs_returns)
    

@app.route("/api/v1.0/<start>/<end>")
def ranges(start, end):
    
    session = Session(engine)
    #query for dates between the start and end dates, which are entered in the URL
    lowest = session.query(func.min(Measurement.tobs)).filter(Measurement.date.between(start, end)).first()
    average = session.query(func.avg(Measurement.tobs)).filter(Measurement.date.between(start, end)).first()
    maximum = session.query(func.max(Measurement.tobs)).filter(Measurement.date.between(start, end)).first()

    #put items into list
    tobs_returns = [lowest, average, maximum]
    return jsonify(tobs_returns)

if __name__ == '__main__':
    app.run(debug=True)