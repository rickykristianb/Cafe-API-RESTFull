from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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

    def to_dict(self):
        # Method 1
        # dictionary = {}
        # for column in self.__table__.columns:
        #     dictionary[column.name] = getattr(self, column.name)
        # return dictionary
        # Method 2 using dictionary comprehension
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record and return random cafe
@app.route("/random")
def random():
    cafe = db.session.query(Cafe).all()
    selected_cafe = choice(cafe)
    return jsonify(cafe=selected_cafe.to_dict())
    # return jsonify(cafe={
    #     "id": selected_cafe.id,
    #     "name": selected_cafe.name,
    #     "map_url": selected_cafe.map_url,
    #     "img_url": selected_cafe.img_url,
    #     "location": selected_cafe.location,
    #     "seats": selected_cafe.seats,
    #     "coffee_price": selected_cafe.coffee_price,
    #     "amenities": {
    #         "has_toilet": selected_cafe.has_toilet,
    #         "has_wifi": selected_cafe.has_wifi,
    #         "has_sockets": selected_cafe.has_sockets,
    #         "can_take_calls": selected_cafe.can_take_calls,
    #     }
    # })


## HTTP GET ALL CAFES in the Database and return it into json format
@app.route("/all")
def all_cafe():
    cafes_list = db.session.query(Cafe).all()
    cafes = [cafe.to_dict() for cafe in cafes_list]
    return jsonify(cafes=cafes)


## HTTP GET - FIND A CAFE BASED ON LOCATION    --> http://127.0.0.1:5000/search?location=Borough
@app.route("/search", methods=['GET'])
def search_cafe():
    args = request.args
    location = args.get("location")   # fetch the parameter value
    cafe_list = db.session.query(Cafe).all()
    cafes = [cafe.to_dict() for cafe in cafe_list if cafe.location.lower() == location.lower()]
    if cafes:
        return jsonify(cafes=cafes)
    else:
        return jsonify(error={
            "Not Found": "Sorry, we don't have a cafe at that location"
        })


## HTTP POST - Create Record
@app.route("/add", methods=['POST'])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        seats=request.form.get("seats"),
        has_toilet=bool(request.form.get("has_toilet")),
        has_wifi=bool(request.form.get("has_wifi")),
        has_sockets=bool(request.form.get("has_sockets")),
        can_take_calls=bool(request.form.get("can_take_calls")),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={
        "Success": "Successfully added the new cafe"
    })


## HTTP PUT/PATCH - Update Record  --> http://127.0.0.1:5000/update-price/22?new-price=2.5
@app.route("/update-price/<int:cafe_id>", methods=['PATCH'])
def update_price(cafe_id):
    cafe = Cafe.query.get(cafe_id)  # or can go to this code -> db.session.query(Cafe).get(cafe_id)
    if cafe:
        new_price = request.args.get("new-price")   # fetch the parameter value
        if new_price:
            cafe.coffee_price = new_price
            db.session.commit()
            return jsonify(Success="Successfully update the price")
        else:
            return jsonify(error="No price was found")
    else:
        return jsonify(error="No cafe id was found")


## HTTP DELETE - Delete Record  -> http://127.0.0.1:5000/report-closed/22?api-key=123
@app.route("/report-closed/<int:cafe_id>", methods=['GET', 'DELETE'])
def delete_cafe(cafe_id):
    authorized_api_key = "123"
    user_api_key = request.args.get("api-key")  # fetch the parameter value
    cafe = db.session.query(Cafe).get(cafe_id)
    if user_api_key == authorized_api_key:
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(success="Cafe was success deleted")
        else:
            return jsonify(error="The cafe was not found")
    else:
        return jsonify(error="You dont have authorization")


if __name__ == '__main__':
    app.run(debug=True)
