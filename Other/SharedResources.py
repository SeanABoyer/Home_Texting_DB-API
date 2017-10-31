from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth

#        MQTT        #
import paho.mqtt.client as mqtt

db = SQLAlchemy()
auth = HTTPBasicAuth();

class User:
    def __init__(self):
        self.userObj = None
        
g_user = User()
client = mqtt.Client("HomeText")