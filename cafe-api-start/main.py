from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import randint
app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api_key='TopSecretAPIKEY'


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


@app.route("/")
def home():
    return render_template("index.html")
    

@app.route('/random', methods=['GET'])
def random():
    id = randint(1, 21)
    cafe = Cafe.query.filter_by(id=id).first()
    cafe_as_dict = {column: str(getattr(cafe, column)) for column in cafe.__table__.c.keys()}
    return jsonify(cafe_as_dict)


@app.route('/all', methods=['GET'])
def all_cafes():
    cafes = db.session.query(Cafe).all()
    cafe_list = []
    for cafe in cafes:
        cafe_as_dict = {column: str(getattr(cafe, column)) for column in cafe.__table__.c.keys()}
        cafe_list.append(cafe_as_dict)
    return jsonify(cafe_list)


@app.route('/search', methods=['GET'])
def search():
    loc = request.args.get('loc')
    cafes = Cafe.query.filter_by(location=loc).all()
    cafe_list = []
    for cafe in cafes:
        cafe_as_dict = {column: str(getattr(cafe, column)) for column in cafe.__table__.c.keys()}
        cafe_list.append(cafe_as_dict)
    if len(cafe_list) == 0:
        return jsonify(error={'Not Found': "Sorry, we don't have a cafe at that location"})
    return jsonify(cafe_list)


@app.route('/add', methods=['POST'])
def add():
    name = request.args.get('name')
    map_url = request.args.get('map_url')
    new_cafe = Cafe(name=name,
                    map_url=map_url)
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={'success': "Successfully add the new cafe"})


@app.route('/update/<cafe_id>', methods=['PATCH'])
def update(cafe_id):
    try:
        cafe = Cafe.query.filter_by(id=cafe_id).first()
        cafe.coffee_price = request.args.get('new_price')
    except:
        return jsonify(error={'Not Found': "Sorry a cafe with that id was not found in the database"})
    else:
        db.session.commit()
        return jsonify(success="Successfully updated the price")


@app.route('/report-closed/<cafe_id>', methods=['DELETE'])
def delete(cafe_id):
    if request.args.get('api_key') == api_key:
        cafe = Cafe.query.filter_by(id=cafe_id).first()
        if cafe is None:
            return jsonify(error={'Not Found': "Sorry a cafe with that id was not found in the database"})
        db.session.delete(cafe)
        db.session.commit()
        return jsonify(success="Successfully deleted the cafe")
    else:
        return jsonify(error="Sorry that's not allowed. Make sure you have the correct api_key")
# # HTTP GET - Read Record

# # HTTP POST - Create Record

# # HTTP PUT/PATCH - Update Record

# # HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
