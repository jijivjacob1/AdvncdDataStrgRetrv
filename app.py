from datetime import datetime
import numpy as np
# import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import dateutil.relativedelta

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the invoices and invoice_items tables
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

        f"/api/v1.0/<start>"
        f"- list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.<br/>"

        f"/api/v1.0/<start>/<end>"
        f"- Ilist of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list invoice totals by country.
    Each item in the list is a dictionary with keys `country` and `total`"""
    # Query all countries from the Invoices table
    d1 = datetime.today()
    d2 = d1 - dateutil.relativedelta.relativedelta(months=12)
    # print(d2.strftime("%Y"))
    results = session.query(Measurement.date, func.avg(Measurement.tobs))\
            .filter(func.strftime("%Y",Measurement.date) == d2.strftime("%Y"))\
            .group_by(Measurement.date).all()

    # Create a list of dicts with `country` and `total` as the keys and
    tobs = []
    for result in results:
        row = {}
        row["date"] = result[0]
        row["tobs"] = result[1]
        tobs.append(row)

    return jsonify(tobs)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list invoice totals by country.
    Each item in the list is a dictionary with keys `country` and `total`"""
    # Query all countries from the Invoices table
    results = session.query(Station.id,Station.name).all()

    # Create a list of dicts with `country` and `total` as the keys and
    # Convert list of tuples into normal list
    station_list = list(np.ravel(results))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list invoice totals by country.
    Each item in the list is a dictionary with keys `country` and `total`"""
    d1 = datetime.today()
    d2 = d1 - dateutil.relativedelta.relativedelta(months=12)
    # Query all countries from the Invoices table
    results = session.query(Measurement.tobs)\
            .filter(func.strftime("%Y",Measurement.date) == d2.strftime("%Y")).all()

    # Create a list of dicts with `country` and `total` as the keys and
    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(results))

    return jsonify(tobs_list)

# @app.route("/api/v1.0/<start>")
# def daily_normals(start):
#     """Return a list invoice totals by country.
#     Each item in the list is a dictionary with keys `country` and `total`"""
#     # Query all countries from the Invoices table
#     results = session.query(Station.id,Station.name).all()

#     # Create a list of dicts with `country` and `total` as the keys and
#     # Convert list of tuples into normal list
#     station_list = list(np.ravel(results))

#     return jsonify(station_list)   

# @app.route("/api/v1.0/<start>/<end>")
# def daily_normals(start,end):
#     """Return a list invoice totals by country.
#     Each item in the list is a dictionary with keys `country` and `total`"""
#     # Query all countries from the Invoices table
#     results = session.query(Station.id,Station.name).all()

#     # Create a list of dicts with `country` and `total` as the keys and
#     # Convert list of tuples into normal list
#     station_list = list(np.ravel(results))

#     return jsonify(station_list)   

if __name__ == '__main__':
    app.run()