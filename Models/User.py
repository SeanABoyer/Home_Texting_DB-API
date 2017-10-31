import datetime
from Other.SharedResources import db, g_user

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