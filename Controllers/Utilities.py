from flask import jsonify
from flask_restful import Resource
#        Authentication        #
from Other.Authentication import require_auth
from Other.SharedResources import g_user

class ValidateIP(Resource):
    def get(self):
        return jsonify({"answer":"True"})
    
    
class ValidateLogin(Resource):
    method_decorators = [require_auth]
    def get(self):
        return jsonify({"answer":"True",
                        "phoneNumber":g_user.userObj["PHONENUMBER"]})