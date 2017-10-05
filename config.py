import os

debug = False
if debug:
    filename = "Test.db"
else:
    filename = "Prod.db"

DatabaseFile = os.getcwd().replace("\\","/")+"/"+filename
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///'+DatabaseFile