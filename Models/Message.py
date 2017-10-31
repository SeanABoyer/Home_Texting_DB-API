from Other.SharedResources import db, g_user
#    MODELS    #
from Models.Conversation import Conversation

class Message(db.Model):
    __tablename__ = "Message"
    id = db.Column(db.Integer, primary_key=True)
    to_phoneNumber = db.Column(db.String(16), nullable=False)
    from_phoneNumber = db.Column(db.String(16), nullable=False)
    message = db.Column(db.String(1024), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('Conversation.id'), nullable=False)
    conversation = db.relationship(Conversation,backref=db.backref('Message',lazy=True))

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