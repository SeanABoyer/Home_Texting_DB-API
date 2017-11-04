import os

#        FLASK        #
from flask import Flask, make_response, jsonify, render_template
from flask_restful import Api
from Other.config import DatabaseFile, debug
from flask_scss import Scss
from flask_cors import CORS


#        CONTROLLERS        #
from Controllers.Conversation import Conversation as CConversation
from Controllers.Message import MessageByPhoneID as CMessageByPhoneID, MessageByPhoneNumber as CMessageByPhoneNumber
from Controllers.User import User as CUser
from Controllers.Utilities import ValidateIP as CValidateIP, ValidateLogin as CValidateLogin

from Other.SharedResources import db, g_user, auth



app = Flask(__name__, template_folder="FrontEnd/templates/", static_folder="FrontEnd/static")
app.debug = True;
app.config.from_object('Other.config')
Scss(app, static_dir='FrontEnd/static', asset_dir='FrontEnd/assets')
CORS(app)
################################
#        DATABASE STUFF        #
################################
with app.app_context():
    db.init_app(app)
    if debug:
        db.drop_all()
        db.create_all()
    else:
        if not os.path.isfile(DatabaseFile):
            db.create_all()

###########################
#        API STUFF        #
###########################
api = Api(app)
api.add_resource(CUser,"/user/")
api.add_resource(CConversation,"/conversation/<string:CONVERSATIONNUMBER>/")
MessageByPhoneNumberRouters = ["/message/by/PhoneNumber/<int:CONVERSATIONNUMBER>/<int:MINSBACK>/","/message/by/PhoneNumber/"]
api.add_resource(CMessageByPhoneNumber,*MessageByPhoneNumberRouters)
api.add_resource(CMessageByPhoneID,"/message/by/ID/<int:CONVERSATIONNUMBER>/<int:ID>/")
api.add_resource(CValidateIP,"/validateIP/")
api.add_resource(CValidateLogin,"/validateLogin/")

################################
#        FRONTEND STUFF        #
################################
@app.route("/")
def index():
    return render_template('index.html');

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

###########################################
#                Utilities                #
###########################################
# @auth.verify_password
# def _verifyPassword(username,password):
#     userObj = User.query.filter(User.username == username).first()
#     if userObj is None:
#         return False
#  
#     global g_user
#      
#     g_user = userObj.asJsonObj()
#     del g_user["PASSWORD"]
#     return custom_app_context.verify(password, userObj.asJsonObj()["PASSWORD"])

# @app.errorhandler(404)
# def not_found(error):
#     return make_response(jsonify({"ERROR":"Not Found"}),404)
# @app.errorhandler(401)
# def unauth_access(error):
#     return make_response(jsonify({"ERROR":"Unauthorized Access"}),401)
# @app.errorhandler(400)
# def bad_request(error):
#     return make_response(jsonify({"ERROR":str(error)}),400)

app.run(host="0.0.0.0",port=80)