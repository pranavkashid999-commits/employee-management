from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, session
from Modules.user_model import User
from Database.db import db
from Utils.responce import SUCCESS_RESPONCE, ERROR_RESPONCE

auth_routs = Namespace(
    "Auth",
    description="Authentication Related Api"
)

user_model = auth_routs.model(
    "UserRegister",
    {
        "username": fields.String(required=True),
        "password": fields.String(required=True),
        "role": fields.String(required=True)
    }
)

login_model = auth_routs.model(
    "UserLogin",
    {
        "username": fields.String(required=True),
        "password": fields.String(required=True)
    }
)


@auth_routs.route("/register")
class Register(Resource):

    @auth_routs.expect(user_model)
    def post(self):
        data = request.get_json()

        existing_user = User.query.filter_by(
            username=data["username"]
        ).first()

        if existing_user:
            return ERROR_RESPONCE("user already exists", 400)

        user = User(
            username=data["username"],
            password=generate_password_hash(data["password"]),
            role=data["role"]
        )

        db.session.add(user)
        db.session.commit()

        return SUCCESS_RESPONCE(
            "User Registered Successfully",
            {},
            200
        )


@auth_routs.route("/login")
class Login(Resource):

    @auth_routs.expect(login_model)
    def post(self):
        data = request.get_json()

        user = User.query.filter_by(
            username=data["username"]
        ).first()

        if user and check_password_hash(
            user.password,
            data["password"]
        ):
            session["user_id"] = user.id
            session["role"] = user.role

            return SUCCESS_RESPONCE(
                "Login Successfully",
                {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role
                },
                200
            )

        return ERROR_RESPONCE(
            "Invalid Username And Password",
            401
        )