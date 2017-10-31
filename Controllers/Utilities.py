from flask import jsonify
from flask_restful import Resource
#        Authentication        #
from Other.Authentication import require_auth

class ValidateIP(Resource):
    def get(self):
        return jsonify({"answer":"True"})
    
    
class ValidateLogin(Resource):
    method_decorators = [require_auth]
    def get(self):
        return jsonify({"answer":"True"})