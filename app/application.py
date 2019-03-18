from app.config import Configuration
from flask import Flask

app = Flask(__name__)
app.config.from_object(Configuration)
