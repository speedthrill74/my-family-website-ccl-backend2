from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://wtruxsbpjppohh:605c8c81c0ca161389d81b05705cca1907d2292c5558532eed6205227335c803@ec2-54-158-26-89.compute-1.amazonaws.com:5432/dc14rulkci8cbt"

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
CORS(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    user = db.Column(db.String)
    
    def __init__(self, text, user):
        self.text = text
        self.user = user
        
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String, nullable=False, unique=True)
    place = db.Column(db.String, nullable=False, unique=True)
    date = db.Column(db.String, nullable=False, unique=True)
    
    def __init__(self, event_name, place, date):
        self.event_name = event_name
        self.place = place
        self.date = date
        
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        
class FamilyData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    phone_number = db.Column(db.String, nullable=False, unique=True)
    address = db.Column(db.String, nullable=False, unique=True)
    
    def __init__(self, username, email, phone_number, address):
        self.username = username
        self.email = email
        self.phone_number = phone_number
        self.address = address
        
        
class PostSchema(ma.Schema):
    class Meta:
        fields = ("id", "text", "user")
        
post_schema = PostSchema()
multiple_post_schema = PostSchema(many=True)

class EventSchema(ma.Schema):
    class Meta:
        fields = ("id", "event_name", "place", "date")
        
event_schema = EventSchema()
multiple_event_schema = EventSchema(many=True)

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "password") #TODO Remove sensitive fields
        
user_schema = UserSchema()
multiple_user_schema = UserSchema(many=True)

class FamilyDataSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "email", "phone_number", "address")
        
family_data_schema = FamilyDataSchema()
multiple_family_data_schema = FamilyDataSchema(many=True)

@app.route("/post/add", methods=["POST"])
def add_post():
    if request.content_type != "application/json":
        return jsonify("ERROR Data must be sent as JSON")
    
    post_data = request.get_json()
    text = post_data.get("text")
    user = post_data.get("user")
    
    record = Post(text, user)
    db.session.add(record)
    db.session.commit()
    
    return jsonify(post_schema.dump(record))

@app.route("/post/get/", methods=["GET"])
def get_post_by_id():
    records = db.session.query(Post).all()
    return jsonify(multiple_post_schema.dump(records))

@app.route("/event/add", methods=["POST"])
def add_event():
    if request.content_type != "application/json":
        return jsonify("ERROR Data must be sent as JSON")
    
    event_data = request.get_json()
    event_name = event_data.get("event_name")
    place = event_data.get("place")
    date = event_data.get("date")
    
    record = Event(event_name, place, date)
    db.session.add(record)
    db.session.commit()
    
    return jsonify(event_schema.dump(record))

@app.route("/event/get/", methods=["GET"])
def get_event_by_id():
    records = db.session.query(Event).all()
    return jsonify(multiple_event_schema.dump(records))

@app.route("/user/add", methods=["POST"])
def add_user():
    if request.content_type != "application/json":
        return jsonify("ERROR: Data must be sent as JSON.")

    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    record_check = db.session.query(User).filter(User.username == username).first()
    if record_check is not None:
        return jsonify("Error: Username already exists.")

    record = User(username, hashed_password)
    db.session.add(record)
    db.session.commit()

    return jsonify(user_schema.dump(record))

@app.route("/user/get", methods=["GET"])
def get_all_users():
    records = db.session.query(User).all()
    return jsonify(multiple_user_schema.dump(records))

@app.route("/user/login", methods=["POST"])
def login():
    if request.content_type != "application/json":
        return jsonify("ERROR: Data must be sent as JSON.")

    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")

    record = db.session.query(User).filter(User.username == username).first()
    if record is None:
        return jsonify("User NOT verified")

    if not bcrypt.check_password_hash(record.password, password):
        return jsonify("User NOT verified")

    return jsonify("User verified")

@app.route("/family_data/add", methods=["POST"])
def add_family_data():
    if request.content_type != "application/json":
        return jsonify("ERROR Data must be sent as JSON")

    family_data_data = request.get_json()
    name = family_data_data.get("name")
    email = family_data_data.get("email")
    phone_number = family_data_data.get("phone_number")
    address = family_data_data.get("address")
    

    record_check = db.session.query(FamilyData).filter(FamilyData.name == name).all()
    if record_check is not None:
        return jsonify("Error: name already exists.")

    record = FamilyData(name, email, phone_number, address)
    db.session.add(record)
    db.session.commit()

    return jsonify(multiple_family_data_schema.dump(record))

@app.route("/family_data/get", methods=["GET"])
def get_all_family_data():
    records = db.session.query(FamilyData).all()
    return jsonify(multiple_family_data_schema.dump(records))


if __name__ == '__main__':
    app.run(debug=True)