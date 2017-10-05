import os.path
import hashlib, uuid
from flask import Flask, jsonify, abort, make_response
from flask.globals import request
from flask_httpauth import HTTPBasicAuth
from werkzeug.exceptions import NotFound

from config import DatabaseFile, debug
from models import *
from passlib.apps import custom_app_context 

app = Flask(__name__)
auth = HTTPBasicAuth()
userID = None
 
################################################################################
#                                MESSAGE
################################################################################
@app.route('/message/', methods=['POST'])
@auth.login_required
def API_create_message():
    jsonMustHave = ["phone_number","macaddress","to","from","message"]
    if not request.json or not set(jsonMustHave).issubset(set(request.json)):
        abort(400,"JSON Request must contain:"+str(jsonMustHave))
        
    if request.json["to"] != request.json["phone_number"] and request.json["from"] != request.json["macaddress"]:
        abort(404)
        
    try:
        conversation = retrieve_conversation(request.json["phone_number"],request.json["macaddress"])
    except NotFound:
        conversation = create_conversation(request.json["phone_number"], request.json["macaddress"])
    messageObj = Message(to_phoneNumber=request.json["to"],
                   from_phoneNumber=request.json["from"],
                   message=request.json["message"],
                   time=datetime.datetime.now(),
                   conversation_id=conversation.id)
    db.session.add(messageObj)
    db.session.commit()
    return jsonify(messageObj.asJsonObj())


@app.route('/message/<phone_number>/<macaddress>', methods=['GET'])
@auth.login_required
def API_retrieve_messages(phone_number,macaddress):
    return API_retrieve_messages_with_start_end(phone_number,macaddress,0)

@app.route('/message/<phone_number>/<macaddress>/<start>', methods=['GET'])
@auth.login_required
def API_retrieve_messages_with_start_end(phone_number,macaddress,start):
    messages = []
    conversation = retrieve_conversation(phone_number,macaddress)
    if start == 0:
        messagesObj = Message.query.filter_by(conversation_id=conversation.id).all()
    else:
        messagesObj = Message.query.filter(Message.conversation_id ==conversation,id, Message.time >=datetime.datetime.now() - datetime.timedelta(0,60*int(start))).all()
        
    for messageObj in messagesObj:
        messages.append(messageObj.asJsonObj())
    return jsonify(messages)

################################################################################
#                                CONVERSATION
################################################################################
def create_conversation(conversation_phone_number,device_macaddress):
    try:
        device = retrieve_device(device_macaddress)
    except NotFound:
        device = create_device(device_macaddress)
    conversationObj = Conversation(phoneNumber=conversation_phone_number,device_id=device.id)
    db.session.add(conversationObj)
    db.session.commit()
    return conversationObj

def retrieve_conversation(conversation_phone_number,device_macaddress):
    deviceObj = retrieve_device(device_macaddress)
    conversationObj = Conversation.query.filter_by(device_id=deviceObj.id,phoneNumber=conversation_phone_number).first()
    if conversationObj is None:
        raise NotFound
    return conversationObj

################################################################################
#                                DEVICE
################################################################################

@app.route('/device/', methods=['POST'])
@auth.login_required
def API_create_device():
    jsonMustHave = ["device_macaddress"]
    if not request.json or not set(jsonMustHave).issubset(set(request.json)):
        abort(400,"JSON Request must contain:"+str(jsonMustHave))
    
    return jsonify(create_device(request.json["device_macaddress"]).asJsonObj())

def create_device(device_macaddress):
    deviceObj = Device(macAddress=device_macaddress,user_id=userID)
    db.session.add(deviceObj)
    db.session.commit()
    return deviceObj
def retrieve_device(device_macaddress):
    deviceObj = Device.query.filter(Device.macAddress == device_macaddress).first()
    if deviceObj is None:
        raise NotFound
    return deviceObj

@app.route('/device/deviceName',methods=['PUT'])
@auth.login_required
def update_deivceName():
    jsonMustHave = ["device_macaddress","device_name"]
    if not request.json or not set(jsonMustHave).issubset(set(request.json)):
        abort(400,"JSON Request must contain:"+str(jsonMustHave))

    deviceObj = Device.query.filter(Device.macAddress == request.json["device_macaddress"]).first()
    if deviceObj is None:
        abort(404)
    deviceObj.deviceName = request.json["device_name"]
    db.session.commit()
    return jsonify(deviceObj.asJsonObj())

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

    global userID
    userID = userObj.asJsonObj()["ID"]
    return custom_app_context.verify(password, userObj.asJsonObj()["PASSWORD"])

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"ERROR":"Not Found"}),404)
@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({"ERROR":str(error)}),400)


if __name__ == '__main__':
    if debug:
        db.drop_all()
        db.create_all()
        TestData()
        app.run()
    else:
        if not os.path.isfile(DatabaseFile):
            db.create_all()
        app.run()

    