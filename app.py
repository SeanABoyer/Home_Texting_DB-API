#!/usr/bin/env/python3
import datetime
import os.path
import paho.mqtt.client as mqtt

from passlib.apps import custom_app_context 
from flask import Flask, jsonify, abort, make_response
from flask.globals import request
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import NotFound
from config import DatabaseFile, debug


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
g_user = None
 
################################################################################
#                                MODELS
################################################################################
 
class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(45), nullable=False)
    creation_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    def __repr__(self):
        return '<User %r>' % self.username
    
    def asJsonObj(self):
        user = {"ID":self.id,
                "USERNAME":self.username,
                "PASSWORD":self.password,
                "CREATION_TIME":self.creation_time    
            }
        return user
class Message(db.Model):
    __tablename__ = "Message"
    id = db.Column(db.Integer, primary_key=True)
    to_phoneNumber = db.Column(db.String(16), nullable=False)
    from_phoneNumber = db.Column(db.String(16), nullable=False)
    message = db.Column(db.String(1024), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('Conversation.id'), nullable=False)
    conversation = db.relationship('Conversation',backref=db.backref('Message',lazy=True))

    def __repr__(self):
        return '<Message %r>' % self.from_phoneNumber
    
    def asJsonObj(self):
        message = {"ID":self.id,
                   "TO":self.to_phoneNumber,
                   "FROM":self.from_phoneNumber,
                   "MESSAGE":self.message,
                   "TIME":self.time
            }
        return message
class Conversation(db.Model):
    __tablename__ = "Conversation"
    id = db.Column(db.Integer, primary_key=True)
    phoneNumber =db.Column(db.String(16), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    user = db.relationship('User',backref=db.backref('Conversation',lazy=True))
     
    def __repr__(self):
        return '<Conversation %r>' % self.phoneNumber
    
    def asJsonObj(self):
        conversation = {"ID":self.id,
                        "PHONENUMBER":self.phoneNumber
        }
        return conversation
class Contact(db.Model):
    __tablename__ = "Contact"
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(30), nullable=False)
    lastName = db.Column(db.String(30), nullable=False)
    phoneNumber = db.Column(db.String(16), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    user = db.relationship('User',backref=db.backref('Contact',lazy=True))
        
#     user_id
    def __repr__(self):
        return '<Contact %r>' % self.firstName
    
    def asJsonObj(self):
        contact = {"ID":self.id,
                   "PHONENUMBER":self.phoneNumber,
                   "FIRSTNAME":self.firstName,
                   "LASTNAME":self.lastName
        }
        return contact    
    
def TestData():
    user = User(username="Steve",password=custom_app_context.hash("S3cert"))
#     device = Device(macAddress="0000000000000002",user=user,deviceName="Steve' Phone")
    
    conv1 = Conversation(phoneNumber="123-456-7891",device=user)
    Message(time=datetime.datetime.now() - datetime.timedelta(0,60*130),to_phoneNumber="123-456-7891",from_phoneNumber="555-555-1234",message="Hello John",conversation=conv1)
    Message(time=datetime.datetime.now()- datetime.timedelta(0,60*120),to_phoneNumber="555-555-1234",from_phoneNumber="123-456-7891",message="Hey Steve",conversation=conv1)
    Message(time=datetime.datetime.now()- datetime.timedelta(0,60*110),to_phoneNumber="123-456-7891",from_phoneNumber="555-555-1234",message="How are you doing?",conversation=conv1)
    Message(time=datetime.datetime.now()- datetime.timedelta(0,60*100),to_phoneNumber="555-555-1234",from_phoneNumber="123-456-7891",message="I am doing well, how about you Steve?",conversation=conv1)
    Message(time=datetime.datetime.now()- datetime.timedelta(0,60*90),to_phoneNumber="123-456-7891",from_phoneNumber="555-555-1234",message="Pretty good. Busy",conversation=conv1)
    Message(time=datetime.datetime.now()- datetime.timedelta(0,60*80),to_phoneNumber="555-555-1234",from_phoneNumber="123-456-7891",message="Okay, Bye Steve",conversation=conv1)
    
    conv = Conversation(phoneNumber="123-456-7890",device=user)
    Message(time=datetime.datetime.now()- datetime.timedelta(0,60*70),to_phoneNumber="555-555-1234",from_phoneNumber="123-456-7890",message="Hello Steve",conversation=conv)
    Message(time=datetime.datetime.now()- datetime.timedelta(0,60*60),to_phoneNumber="123-456-7890",from_phoneNumber="555-555-1234",message="Hey Jane",conversation=conv)
    
    Contact(firstName="John",lastName="Doe",phoneNumber="123-456-7891",user=user)
    Contact(firstName="Jane",lastName="Doe",phoneNumber="123-456-7890",user=user)    
    
    db.session.add(user)
    db.session.commit()

################################################################################
#                                MESSAGE
################################################################################
@app.route('/message/', methods=['POST'])
@auth.login_required
def API_create_message():
    jsonMustHave = ["phone_number","to","from","message","type"]
    if not request.json or not set(jsonMustHave).issubset(set(request.json)):
        abort(400,"JSON Request must contain:"+str(jsonMustHave))
        
    if request.json["to"] != request.json["phone_number"] and request.json["from"] != request.json["phone_number"]:
        abort(404)
        
    try:
        conversation = retrieve_conversation(request.json["phone_number"])
    except NotFound:
        conversation = create_conversation(request.json["phone_number"])
    messageObj = Message(to_phoneNumber=request.json["to"],
                   from_phoneNumber=request.json["from"],
                   message=request.json["message"],
                   time=datetime.datetime.now(),
                   conversation_id=conversation.id)
    db.session.add(messageObj)
    db.session.commit()
    client.publish(g_user["USERNAME"]+"/"+request.json["phone_number"],request.json["type"])
    return jsonify(messageObj.asJsonObj())


@app.route('/message/<phone_number>/', methods=['GET'])
@auth.login_required
def API_retrieve_messages(phone_number):
    return API_retrieve_messages_with_start(phone_number,0)

@app.route('/message/<phone_number>/<start>', methods=['GET'])
@auth.login_required
def API_retrieve_messages_with_start(phone_number,start):
    messages = []
    conversation = retrieve_conversation(phone_number)
    if start == 0:
        messagesObj = Message.query.filter_by(conversation_id=conversation.id).all()
    else:
        messagesObj = Message.query.filter(Message.conversation_id ==conversation.id, Message.time >=datetime.datetime.now() - datetime.timedelta(0,60*int(start))).all()
        
    for messageObj in messagesObj:
        messages.append(messageObj.asJsonObj())
    return jsonify(messages)

################################################################################
#                                CONVERSATION
################################################################################
def create_conversation(conversation_phone_number):
    conversationObj = Conversation(phoneNumber=conversation_phone_number,user_id=g_user["ID"])
    db.session.add(conversationObj)
    db.session.commit()
    return conversationObj

def retrieve_conversation(conversation_phone_number):
    conversationObj = Conversation.query.filter_by(user_id=g_user["ID"],phoneNumber=conversation_phone_number).first()
    if conversationObj is None:
        raise NotFound
    return conversationObj

################################################################################
#                                USER
################################################################################
@app.route('/user/',methods=['POST'])
def create_user():
    jsonMustHave = ["username","password"]
    if not request.json or not set(jsonMustHave).issubset(set(request.json)):
        abort(400,"JSON Request must contain:"+str(jsonMustHave))
    
    if retrieve_user(request.json["username"]) is None:
        userObj = User(username = request.json["username"],password = custom_app_context.hash(request.json["password"]),creation_time = datetime.datetime.now())
        db.session.add(userObj)
        db.session.commit()
        userJson = userObj.asJsonObj()
        del userJson["PASSWORD"]
        del userJson["ID"]
        return jsonify(userJson)
    else:
        abort(400,"User already exists.")

def retrieve_user(username):
    UserObj = User.query.filter(User.username == username).first()
    return UserObj
################################################################################
#                                OTHER STUFF
################################################################################
@auth.verify_password
def verify_password(username,password):
    userObj = User.query.filter(User.username == username).first()
    if userObj is None:
        return False

    global user
    
    g_user = userObj.asJsonObj()
    del g_user["PASSWORD"]
    return custom_app_context.verify(password, userObj.asJsonObj()["PASSWORD"])

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"ERROR":"Not Found"}),404)
@app.errorhandler(401)
def unauth_access(error):
    return make_response(jsonify({"ERROR":"Unauthorized Access"}),401)
@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({"ERROR":str(error)}),400)


@app.route('/validIP/', methods=['GET'])
def validIP():
    return jsonify({"answer":"True"})

@app.route('/validLogin/', methods=['GET'])
@auth.login_required
def validLogin():
    return jsonify({"answer":"True"})


if __name__ == '__main__':
    if debug:
        db.drop_all()
        db.create_all()
        TestData()
    else:
        if not os.path.isfile(DatabaseFile):
            db.create_all()
client = mqtt.Client("HomeText")
client.connect("0.0.0.0",1883,60)
app.run(host="0.0.0.0",port=80)

    