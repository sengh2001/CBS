"""Adds demo data for the application.

__author__ = "Balwinder Sodhi"
__copyright__ = "Copyright 2022"
__license__ = "MIT"
__version__ = "0.1"
__status__ = "Development"
"""

import argparse
import json


from common import *
from models import *

def setup_db(config):
    print("========== Setting up PRODUCTION database ==========")
    import psycopg2
    
    db_args = config["db_args"]
    db_name = config["db_name"]
    
    conn = psycopg2.connect(**db_args)
    conn.autocommit = True  # Necessary for PostgreSQL to execute DDL statements
    
    cur = conn.cursor()
    
    print("Dropping the schema: {}".format(db_name))
    cur.execute("DROP SCHEMA IF EXISTS {} CASCADE".format(db_name))
    
    print("Creating the schema: {}".format(db_name))
    cur.execute("CREATE SCHEMA {}".format(db_name))
    
    cur.close()
    conn.close()

    db.init(db_name, **db_args)
    create_schema()
    print("Created DB tables.")

    u = User()
    u.first_name, u.last_name = "EIS", "Admin"
    u.email = "bhankharz13@gmail.com"
    u.role = "SUP"
    u.org_unit = "/"
    u.save()
    print("Added the admin user.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cfg_file_path", type=str,
                        help="Configuration file path.")
    args = parser.parse_args()
    with open(args.cfg_file_path, "r") as cfg_file:
        cfg = json.load(cfg_file)
        setup_db(cfg)
        