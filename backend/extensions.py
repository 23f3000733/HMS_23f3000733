from flask_sqlalchemy import SQLAlchemy
from flask_security import Security
from flask_cors import CORS

db = SQLAlchemy()
security = Security()
cors = CORS()
