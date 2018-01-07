from datetime import datetime
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import dateutil.relativedelta
from dateutil import parser

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the stations and measurements tables
Station = Base.classes.stations
Measurement = Base.classes.measurements

# Create our session (link) from Python to the DB
session = Session(engine)

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
        f"Avalable Routes:<br/>"
        f"/api/v1.0/precipitation - Dates and temperature observations from last year<br/>"

        f"/api/v1.0/stations"
        f"- List of stations in Hawaii <br/>"

        f"/api/v1.0/tobs"
        f"- List of Temperature Observations (tobs) for the previous year<br/>"

        f"/api/v1.0/start"
        f"- list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.<br/>"

        f"/api/v1.0/start/end"
        f"- list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Query for the dates and temperature observations from the last year."""

    # compute previous year relative to cuurent date
    d1 = datetime.today()
    d2 = d1 - dateutil.relativedelta.relativedelta(months=12)
    # query to return previous years average tobs for each date
    results = session.query(Measurement.date, func.round(func.avg(Measurement.tobs),2))\
            .filter(func.strftime("%Y",Measurement.date) == d2.strftime("%Y"))\
            .group_by(Measurement.date).all()

    # Create a list of dicts with `date` and  average`tobs` as the keys and values
    tobs = []
    for result in results:
        row = {}
        row["date"] = result[0]
        row["tobs"] = result[1]
        tobs.append(row)

    return jsonify(tobs)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    # Query all stations  from the stations table
    results = session.query(Station.id,Station.name).all()

    # return list of stations
    station_list = list(np.ravel(results))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a json list of Temperature Observations (tobs) for the previous year"""

    # compute previous year relative to cuurent date
    d1 = datetime.today()
    d2 = d1 - dateutil.relativedelta.relativedelta(months=12)
    # Query avg tobs  for all dates in previous year
    results = session.query(func.round(func.avg(Measurement.tobs),2))\
            .filter(func.strftime("%Y",Measurement.date) == d2.strftime("%Y")).group_by(Measurement.date).all()

    #return list of tobs
    return jsonify(list(np.ravel(results)))

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def daily_normals(start,end="None"):

    """Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

    When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

    When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
    
    #parse and compute start date
    dt_start = parser.parse(start)
    min_date = dt_start.strftime("%Y-%m-%d")
    #parse and compute end date if entered else init to max date available
    if end != "None":
        dt_end = parser.parse(end)
        max_date = dt_end.strftime("%Y-%m-%d")
    else:
        max_date = session.query(func.max(Measurement.date))\
             .all()[0][0]

    #calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    result = session.query(func.min(Measurement.tobs), func.round(func.avg(Measurement.tobs),2), func.max(Measurement.tobs)).\
             filter(Measurement.date >= min_date).filter(Measurement.date <= max_date).all()

    #return list
    return jsonify(result)
  
if __name__ == '__main__':
    app.run()