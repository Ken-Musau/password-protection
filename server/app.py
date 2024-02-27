#!/usr/bin/env python3

from flask import jsonify, make_response, request, session
from flask_restful import Resource

from config import app, db, api
from models import User


class Home(Resource):
    def get(self):
        return make_response("<h1>Welcome home</h1>")


class ClearSession(Resource):

    def delete(self):

        session['page_views'] = None
        session['user_id'] = None

        return {}, 204


class UsersById(Resource):
    def delete(self, id):
        user = User.query.get(id)

        if not user:
            return make_response({"message": "User not found"}, 404)

        try:
            db.session.delete(user)
            db.session.commit()
            return make_response({"message": "User deleted"}, 200)
        except Exception as e:
            # Handle database errors or other exceptions
            db.session.rollback()
            return make_response({"message": "Error deleting user"}, 500)


api.add_resource(UsersById, "/users/<int:id>")


class Signup(Resource):

    def post(self):
        json = request.get_json()
        user = User(
            username=json['username'],
            password_hash=json['password']
        )
        db.session.add(user)
        db.session.commit()
        return user.to_dict(), 201


class CheckSession(Resource):
    def get(serlf):
        user = User.query.filter(User.id == session.get("user_id")).first()

        if user:
            return user.to_dict()

        else:
            return {}, 204


class Login(Resource):
    def post(self):
        json = request.get_json()

        user = User.query.filter(User.username == json["username"]).first()

        if user.authenticate(json["password"]):
            session['user_id'] = user.id

            return user.to_dict(), 200
        return {"Invalid username or password"}, 404


class Logout(Resource):
    def delete(self):
        session['user_id'] = None

        return {}, 204

    pass


api.add_resource(Home, '/', endpoint='/')
api.add_resource(ClearSession, '/clear', endpoint='clear')
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
