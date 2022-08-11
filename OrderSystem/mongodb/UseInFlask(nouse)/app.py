from flask import Flask, request, render_template
from pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017//test_db"
mongo = PyMongo(app)

@app.route
