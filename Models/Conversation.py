from Other.SharedResources import db, g_user
#    MODELS    #
from Models.User import User

class Conversation(db.Model):
    __tablename__ = "Conversation"
    id = db.Column(db.Integer, primary_key=True)
    phoneNumber =db.Column(db.String(16), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    user = db.relationship(User,backref=db.backref('Conversation',lazy=True))
     
    def __repr__(self):
        return '<Conversation %r>' % self.phoneNumber
    
    def asJsonObj(self):
        conversation = {"ID":self.id,
                        "CONVERSATIONNUMBER":self.phoneNumber
        }
        return conversation