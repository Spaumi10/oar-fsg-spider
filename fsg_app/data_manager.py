import sqlite3

from flask import current_app, g
from oar_scraper import fsg_data

# from fsg_app.db import get_db


def store_data(data):
    """Inserts scrapped data into database. To be used outside of flask app.
    Arguments:
    data -- The fsg_data that comes from OAR scrape.
    """

    con = sqlite3.connect("instance/fsg_app.sqlite")
    cur = con.cursor()
    for entry in data:
        cur.execute(
            "INSERT INTO crimes (crime_name, ors, ranking, felony_class) VALUES(:crime_name, :ors, :ranking, :felony_class)",
            entry,
        )

    con.commit()
    con.close()


store_data(fsg_data)
