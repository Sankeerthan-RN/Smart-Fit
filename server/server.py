import os
from flask import Flask, request
import main
import sizeClassifier
app = Flask(__name__)

@app.route('/handle_form', methods=['POST'])
def handle_form():
    print("Posted file: {}".format(request.files['file']))
    file = request.files['file']
    file.save(os.path.join("data\images", file.filename))
    height = float(request.form.to_dict()["height"])
    pixel,shoulderlen,shirtlen,pantlen,armlen,img_path= main.main("data\images\\"+str(file.filename),height)

    return {
        "shoulderlen":shoulderlen,
        "shirtlen":shirtlen,
        "pantlen": pantlen,
        "imagePath": "C:/Users/sange/Desktop/smartfit circular/server/"+img_path,
    }

@app.route('/get_size', methods=['POST'])
def check_size():
    content = request.get_json()
    print(content)
    chest_size = float(content["chest_size"])
    shirt_len = float(content["shirt_len"])
    across_shoulder = float(content["across_shoulder"])
    brand = content["brand"]
    shirt_size = sizeClassifier.classifySize(chest_size,shirt_len,across_shoulder,brand)

    return {
        "shirt_size":shirt_size
    }

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)