from flask import Flask, render_template, request, jsonify
import urllib.request
import json
import requests
from bs4 import BeautifulSoup
import re
import json
import pymongo

app = Flask(__name__)

URL = "http://www.flipkart.com"


def mongodbConnection():
    conn = pymongo.MongoClient("mongodb://localhost:27017")
    mydb = conn["Reviews"]
    mycol = mydb["FlipkartReview"]
    return mycol


def get_html(url):
    fp = urllib.request.urlopen(url)
    mybytes = fp.read()

    mystr = mybytes.decode("utf8")
    fp.close()
    return mystr


def remove_non_ascii(mystring):
    return re.sub(r'[^\x00-\x7f]', r'', mystring)


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ", "")
        query = {"Product": searchString}
        mycol = mongodbConnection()
        mydoc = mycol.find(query, {'_id': False})
        if (mydoc.explain()['executionStats']['nReturned'] != 0):
            # for x in mydoc:
            #     print(x)
            #     print("-----------------------")
            return render_template('results.html', reviews=mydoc)  # show the results to user
        else:
            myReviews = []
            PAGE = 1
            PAGENEXT = True
            url = URL + "/search?q=" + searchString.replace(" ", "%20")
            mystr = get_html(url)
            e = 0
            soup = BeautifulSoup(mystr)
            links = soup.findAll(name="script", id="jsonLD")
            links_dict = json.loads(links[0].string)

            soup = BeautifulSoup(get_html(links_dict['itemListElement'][0]['url']))
            links_dict['itemListElement'][0]
            base_url = links_dict['itemListElement'][0]['url'].split("/p/")[0]
            soup.find_all("a", href=re.compile("product-reviews/"))
            try:
                product_review_url = "https://www.flipkart.com" + \
                                     soup.find_all("a", href=re.compile("product-reviews/"))[0].get("href").split(
                                         sep="&lid=")[0]
            except:
                return "review not found"

            while PAGENEXT:
                print("Getting Page {}".format(PAGE))
                soup = BeautifulSoup(get_html(product_review_url))
                mydict = soup.findAll(name="script", id="is_script")

                json_text = re.search(r'^\s*window\.__INITIAL\_STATE__\s*=\s*({.*?})\s*;\s*$',
                                      mydict[0].string, flags=re.DOTALL | re.MULTILINE).group(1)

                script_dictionary = json.loads(json_text)

                list_of_reviews = [value for value in script_dictionary['pageDataV4']['page']['data']['10002'] if
                                   value['slotType'] == "WIDGET" if (value['widget']['type'] == "REVIEWS")]

                if (len(list_of_reviews) == 0):
                    list_of_reviews = [value for value in script_dictionary['pageDataV4']['page']['data']['10002'] if
                                       value['slotType'] == "WIDGET" if (value['widget']['type'] == "ASPECT_REVIEWS")]
                # return list_of_reviews
                for reviews in list_of_reviews:
                    Reviews_Dict = {"id": 0, "Product": "", "Name": "", "Rating": 0, "CommentHead": "",
                                    "Comment": ""}
                    Reviews_Dict['id'] = e
                    Reviews_Dict['Product'] = searchString
                    Reviews_Dict['Name'] = reviews['widget']['data']['renderableComponents'][0]['value']['author']
                    Reviews_Dict["CommentHead"] = reviews['widget']['data']['renderableComponents'][0]['value'][
                        'title']
                    Reviews_Dict["Rating"] = reviews['widget']['data']['renderableComponents'][0]['value']['rating']
                    Reviews_Dict["Comment"] = reviews['widget']['data']['renderableComponents'][0]['value']['text']

                    Reviews_Dict['Name'] = remove_non_ascii(Reviews_Dict['Name'])
                    Reviews_Dict['CommentHead'] = remove_non_ascii(Reviews_Dict['CommentHead'])
                    Reviews_Dict['Comment'] = remove_non_ascii(Reviews_Dict['Comment'])
                    myReviews.append(Reviews_Dict)
                    e += 1
                    # print(myReviews)
                # return myReviews
                PAGE = PAGE + 1
                nextpage = "page={}".format(PAGE)
                mydata = soup.findAll(name="a", href=re.compile(nextpage))
                if (len(mydata) == 0):
                    PAGENEXT = False

                else:
                    for data in soup.findAll(name="a", href=re.compile(nextpage)):
                        if (data.findAll(name="span", text="Next")):
                            product_review_url = URL + data.get("href")
                            PAGENEXT = True
                            break
                        else:
                            PAGENEXT = False
            mycol.insert_many(myReviews)
            mydoc = mycol.find(query, {'_id': False})
            # for x in mydoc:
            #     print(x)
            #     print("-----------------------")
        return render_template('results.html', reviews=mydoc)
    #        return myReviews
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(port=8000, debug=True)  # running the app on the local machine on port 8000
