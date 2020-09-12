
import pymongo
from bing_image_downloader import downloader
from flask import Flask, render_template, request
from flask_cors import  cross_origin
import os

app = Flask(__name__, static_folder='C:\\Users\\mohan\\Documents\\ineuron\\WebScraping\\ImageScraper\\ImageDir')


# Claim: With reference to the below link, it is not possible to extract google images completely as it
# is restricted in the recent times we can only get tile images from google and we cannot get full images
# https://stackoverflow.com/questions/36438261/extracting-images-from-google-images-using-src-and-beautifulsoup

# Hence I am using Bing images to perform the same operation


@app.route("/", methods=['POST', 'GET'])
@cross_origin()
def home():
    return render_template("index.html")


@app.route("/searchImages", methods=['POST', 'GET'])
@cross_origin()
def search_images():
    if request.method == 'POST':
        try:
            searchString = request.form['keyword']
            downloader.download(searchString, limit=10, output_dir="ImageDir")

        except:
            print("Couldnt fetch data from Bing")
    else:
        return render_template("index.html")

    return show_images(searchString)


@app.route("/showImages", methods=['POST', 'GET'])
@cross_origin()
def show_images(searchString):
    user_images = os.listdir('ImageDir/'+searchString+"/")
    user_images = [searchString+"/"+user_image for user_image in user_images]
    # return {i:image.replace("\\","/") for i,image in enumerate(user_images)}
    #user_images = [user_image.replace("\\","/") for user_image in user_images]
    try:
        if (len(user_images) > 0):
            return render_template('showImage.html', user_images=user_images)
        else:
            return "Please try with a different string"
    except Exception as e:
        print('no Images found ', e)
        return "Please try with a different string"

if __name__ == "__main__":
    app.run(port=8000, debug=True)  # running the app on the local machine on port 8000