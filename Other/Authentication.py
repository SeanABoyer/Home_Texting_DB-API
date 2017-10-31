
from functools import wraps
from flask import request, abort
from passlib.apps import custom_app_context
from Other.SharedResources import g_user
 #        Models        #
from Models.User import User as MUser
def check_auth(username,password):
    userObj = MUser.query.filter(MUser.username == username).first()
    if userObj is None:
        return False
     
    g_user.userObj= userObj.asJsonObj()
    del g_user.userObj["PASSWORD"]
    return custom_app_context.verify(password, userObj.asJsonObj()["PASSWORD"])

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            abort(401)
        return f(*args, **kwargs)
    return decorated