from flask import jsonify
from flask_restful import Resource, reqparse
from werkzeug.exceptions import NotFound
from Other.SharedResources import db, g_user
#        Authentication        #
from Other.Authentication import require_auth
#        Models        #

from Models.Conversation import Conversation as MConversation
class Conversation(Resource):
    method_decorators = [require_auth]
    def get(self,CONVERSATIONNUMBER):
        ConverastionArray = MConversation.query.filter(MConversation.user_id == g_user.userObj["ID"]).all()
        convArrayInJson = []
        for convObj in ConverastionArray:
            convArrayInJson.append(convObj.asJsonObj())
        return jsonify(convArrayInJson)
     
    def _createConversation(self,conversation_phone_number):
        conversationObj = MConversation(phoneNumber=conversation_phone_number,user_id=g_user.userObj["ID"])
        db.session.add(conversationObj)
        db.session.commit()
        return conversationObj
     
    def _retrieveConversation(CONVERSATIONNUMBER):
        conversationObj = MConversation.query.filter_by(user_id=g_user.userObj["ID"],phoneNumber=CONVERSATIONNUMBER).first()
        if conversationObj is None:
            raise NotFound
        return conversationObj