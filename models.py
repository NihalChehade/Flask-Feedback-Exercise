from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """user"""

    __tablename__ = "users"

    username = db.Column(db.String(20), 
                         primary_key=True,)

    password = db.Column(db.Text, 
                         nullable=False)
    
    email = db.Column(db.String(50),
                      nullable = False,
                      unique = True)
    
    first_name = db.Column(db.String(30),
                           nullable = False)
    
    last_name = db.Column(db.String(30),
                          nullable = False)
    

    # start_register
    @classmethod
    def register(cls, username, pwd, email, fname, lname):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8, email=email, first_name=fname, last_name=lname )
    # end_register

    # start_authenticate
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False

class Feedback(db.Model):
    """feedback"""
    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, 
                   primary_key=True, 
                   autoincrement=True)
    
    title= db.Column(db.String(100), 
                         nullable=False, 
                         unique=True)
    
    content = db.Column(db.Text, 
                         nullable=False)
    
    username =db.Column(db.String(20),
                        db.ForeignKey('users.username', ondelete="cascade"))
    
    user = db.relationship('User', backref="feedbacks")



