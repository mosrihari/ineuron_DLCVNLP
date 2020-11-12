# Flask Application

from flask import Flask, request, render_template, jsonify
from flask_cors import CORS, cross_origin
from keras.preprocessing.image import load_img
from Utilities.utils import decodeImage
from predict import PredictImages
import logging

app = Flask(__name__)
CORS(app)


@app.route("/", methods=['GET'])
@cross_origin()
def home1():
    return render_template("index.html")

@app.route("/predict",methods=["GET","POST"])
@cross_origin()
def predictRoute():
    logging.info("in prediction")
    imgstring = request.json['image']
    decodeImage(imgstring)
    myimage = load_img("myimage.jpeg",target_size=(64, 64))
    predictObject = PredictImages(myimage)
    predictions = predictObject.predict()
    return jsonify(predictions)

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="127.0.0.1", debug=True, port=80)


