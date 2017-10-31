import datetime
import traceback

from flask_restful import Resource, reqparse
from flask import request, jsonify, json
from werkzeug.exceptions import NotFound
from Other.SharedResources import db, g_user, client

#        Authentication        #
from Other.Authentication import require_auth
#        Controllers        #
from Controllers.Conversation import Conversation as CConversation
#        Models        #
from Models.Message import Message as MMessage
class MessageByPhoneNumber(Resource):
    method_decorators = [require_auth]
    
    def get(self,CONVERSATIONNUMBER,MINSBACK):     
        messages = []
        conversation = CConversation._retrieveConversation(CONVERSATIONNUMBER)
        if int(MINSBACK) == 0:
            messagesObj = MMessage.query.filter_by(conversation_id=conversation.id).all()
        else:
            messagesObj = MMessage.query.filter(MMessage.conversation_id ==conversation.id, Message.time >=datetime.datetime.now() - datetime.timedelta(0,60*int(MINSBACK))).all()
             
        for messageObj in messagesObj:
            messages.append(messageObj.asJsonObj())
        return jsonify(messages)
    
    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('CONVERSATIONNUMBER',required=True, type=int, location='json')
        parser.add_argument('FROM',required=True, type=int, location='json')
        parser.add_argument('TO',required=True, type=int, location='json')
        parser.add_argument('MESSAGE',required=True, type=str, location='json')
        parser.add_argument('CLIENT',required=True, type=str, location='json')
        args = parser.parse_args(strict=True)
        try:
            conversation = CConversation._retrieveConversation(args.get("CONVERSATIONNUMBER"))
        except NotFound:
            conversation = CConversation._createConversation("",args.get("CONVERSATIONNUMBER"))
        messageObj = MMessage(to_phoneNumber=args.get("TO"),
                       from_phoneNumber=args.get("FROM"),
                       message=args.get("MESSAGE"),
                       time=datetime.datetime.now(),
                       conversation_id=conversation.id)
        db.session.add(messageObj)
        db.session.commit()
        
        try:
            #TODO check table to see if any messages need to be sent.
            client.connect("0.0.0.0",1883,60)
            mqtt_message = {
                "CONVERSATIONNUMBER":args.get("CONVERSATIONNUMBER"),
                "CLIENT":args.get("CLIENT"),
                "MESSAGEID":messageObj.id}
            client.publish(g_user.userObj["USERNAME"],json.dumps(mqtt_message))
            client.disconnect()
        except OSError:
            #TODO Write to a table, to check again later.
            pass
        except Exception:
            traceback.print_exc()
          
        return jsonify(messageObj.asJsonObj())

class MessageByPhoneID(Resource):
    method_decorators = [require_auth]
    def get(self,CONVERSATIONNUMBER,ID):
        conversation = CConversation._retrieveConversation(CONVERSATIONNUMBER);
        messageobj = MMessage.query.filter(MMessage.conversation_id==conversation.id,MMessage.id==ID).first()
        return jsonify(messageobj.asJsonObj())