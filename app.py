# 1. Import libraries
import datetime as dt
from dateutil import relativedelta
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, desc, func

from flask import Flask, jsonify

# 2. Database Setup
engine = create_engine("sqlite:///Instructions/Resources/hawaii.sqlite")

# reflect database and its tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# save a reference to its tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# 2. Create an app, passing __name__
app = Flask(__name__)

# 3. Index route
@app.route("/")
def welcome():
    """List all available API routes."""
    return(
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

# 4. Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Create a session
    session = Session(engine)
    
    """Return a dictionary with dates and precipitation amounts"""
    #Query measurements
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    
    #Create a dictionary for the results
    precipitation = {}
    for date, prcp in results:
        precipitation[date] = prcp
        
    return jsonify(precipitation)

# 5. Stations route
@app.route("/api/v1.0/stations")
def stations():
    #Create a session
    session = Session(engine)
    
    """Return a list of stations"""
    #Query measurements
    results = session.query(Station.name.distinct()).all()
    session.close()
    
    #Create a dictionary for the results
    stations = []
    for name in results:
        stations.append(name)
        
    return jsonify(list(np.ravel(stations)))
    
# 6. TOBS route
@app.route("/api/v1.0/tobs")
def tobs():
    #Create a session
    session = Session(engine)
    
    datetext = get_last_date(session)
    recent_date = dt.datetime.strptime(datetext, '%Y-%m-%d')
    year_ago = recent_date - relativedelta.relativedelta(years=1)
    
    """Return a list of stations"""
    #Query measurements
    results = session.query(Measurement.tobs).\
        filter(Measurement.date > year_ago).\
        filter(Measurement.date <= recent_date).all()
    session.close()
    
    #Create a dictionary for the results
    temps = []
    for tobs in results:
        temps.append(tobs)
        
    return jsonify(list(np.ravel(temps)))

# 7. Start Date
@app.route("/api/v1.0/<start>")
def start(start):
    #Create Session
    session = Session(engine)
    
    """Returns the min, mean, and max temps between the date given and the most recent date available"""
    #Get most recent date in database
    recent_date = get_last_date(session)[0]
    session.close()
    
    #Call the 'overloaded' function with the most recent date as the end date
    return start_end(start, str(recent_date))
    
# 8. End Date
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    #Create a session
    session = Session(engine)
    
    """Returns the min, mean, and max temps between the 2 dates given"""
    startdate = dt.datetime.strptime(start, '%Y-%m-%d')
    enddate = dt.datetime.strptime(end, '%Y-%m-%d')
    
    #Query the min, mean, and max temps between the dates given
    tmin, tmean, tmax = calc_temps(session, startdate, enddate)
    session.close()
    
    return jsonify([tmin, tmean, tmax])
    
# 9. Utility function to get most recent date in database
def get_last_date(session):
    return session.query(Measurement.date).order_by(desc(Measurement.date)).first()

# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(session, start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), 
                         func.avg(Measurement.tobs), 
                         func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).first()
    
# n. Tester/Main
if __name__ == "__main__":
    app.run(debug=True)
