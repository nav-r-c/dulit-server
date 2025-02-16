from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
from models import Programme, Speaker

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

from pymongo import MongoClient

uri = os.getenv('MONGODB_URI')
# print(f"{uri=}")

try:
    client = MongoClient(uri)
    print("Mongodb Connected!")
except Exception as e:
    print("MongoDB Connection Error:", e)


# MongoDB Configuration
app.config['MONGO_URI'] = os.getenv('MONGODB_URI')
mongo = PyMongo(app)

# Attach collections to models (if using models)
Programme.collection = mongo.db.programmes
Speaker.collection = mongo.db.speakers

# Register Routes
from routes.doc_routes import doc_bp
from routes.programme_routes import programme_bp
from routes.speaker_routes import speaker_bp

app.register_blueprint(doc_bp)
app.register_blueprint(programme_bp)
app.register_blueprint(speaker_bp)

if __name__ == "__main__":
    print("🚀 Flask server running on http://127.0.0.1:3000")
    app.run(port=3000, debug=True)
