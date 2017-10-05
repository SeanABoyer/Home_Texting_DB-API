import datetime
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context 
from app import app

app.config.from_object('config')
db = SQLAlchemy(app)

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
class Device(db.Model):
    __tablename__ = "Device"
    id = db.Column(db.Integer, primary_key=True)
    macAddress = db.Column(db.String(23), unique=True, nullable=False)
    deviceName = db.Column(db.String(30), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    user = db.relationship('User',backref=db.backref('Device',lazy=True))

    def __repr__(self):
        return '<Device %r>' % self.macAddress
    
    def asJsonObj(self):
        device = {"ID":self.id,
                  "MACADDRESS":self.macAddress,
                "DEVICENAME":self.deviceName    
        }
        return device
class Conversation(db.Model):
    __tablename__ = "Conversation"
    id = db.Column(db.Integer, primary_key=True)
    phoneNumber =db.Column(db.String(16), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('Device.id'), nullable=False)
    device = db.relationship('Device',backref=db.backref('Conversation',lazy=True))
     
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
    device = Device(macAddress="0000000000000002",user=user,deviceName="Steve' Phone")
    
    conv1 = Conversation(phoneNumber="123-456-7891",device=device)
    Message(time=datetime.datetime.now() - datetime.timedelta(0,60*130),to_phoneNumber="123-456-7891",from_phoneNumber="555-555-1234",message="Hello John",conversation=conv1)
    Message(time=datetime.datetime.now()- datetime.timedelta(0,60*120),to_phoneNumber="555-555-1234",from_phoneNumber="123-456-7891",message="Hey Steve",conversation=conv1)
    Message(time=datetime.datetime.now()- datetime.timedelta(0,60*110),to_phoneNumber="123-456-7891",from_phoneNumber="555-555-1234",message="How are you doing?",conversation=conv1)
    Message(time=datetime.datetime.now()- datetime.timedelta(0,60*100),to_phoneNumber="555-555-1234",from_phoneNumber="123-456-7891",message="I am doing well, how about you Steve?",conversation=conv1)
    Message(time=datetime.datetime.now()- datetime.timedelta(0,60*90),to_phoneNumber="123-456-7891",from_phoneNumber="555-555-1234",message="Pretty good. Busy",conversation=conv1)
    Message(time=datetime.datetime.now()- datetime.timedelta(0,60*80),to_phoneNumber="555-555-1234",from_phoneNumber="123-456-7891",message="Okay, Bye Steve",conversation=conv1)
    
    conv = Conversation(phoneNumber="123-456-7890",device=device)
    Message(time=datetime.datetime.now()- datetime.timedelta(0,60*70),to_phoneNumber="555-555-1234",from_phoneNumber="123-456-7890",message="Hello Steve",conversation=conv)
    Message(time=datetime.datetime.now()- datetime.timedelta(0,60*60),to_phoneNumber="123-456-7890",from_phoneNumber="555-555-1234",message="Hey Jane",conversation=conv)
    
    Contact(firstName="John",lastName="Doe",phoneNumber="123-456-7891",user=user)
    Contact(firstName="Jane",lastName="Doe",phoneNumber="123-456-7890",user=user)    
    
    db.session.add(user)
    db.session.commit()

    