from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import User, Password, Base
import util
import uuid
from typing import Tuple
from datetime import datetime
import exceptions

# Connects to the database
engine = create_engine(util.path_to_db())
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def create_user(username: str, plaintext_password: str) -> str:
	if session.query(User).filter(User.username == username).first() is not None:
		raise exceptions.UsernameTakenException()
	uid = str(uuid.uuid4())
	hashed_password = util.encrypt_new_password(plaintext_password)
	session.add(User(
		uid=uid,
		username=username,
		hashed_password=hashed_password
	))
	session.commit()
	return uid


def create_password(uid: str, raw_password: str, password_name: str, password: str):
	if session.query(Password).filter(Password.uid == uid).filter(Password.name == password_name).first() is not None:
		raise exceptions.AlreadyAPasswordWithThatNameException()
	hashed_password = 