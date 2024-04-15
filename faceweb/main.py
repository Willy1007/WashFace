from flask import Flask, render_template, request
from PIL import Image
import numpy as np
import requests, cv2
from keras.applications.mobilenet_v2 import preprocess_input
from select_tool import select_1, select_2

app = Flask(__name__, static_url_path="/imgs", static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files['filename']
    img = Image.open(file)
    width, height = img.size
    img_np = np.array(img)
    
    if height > width:
        diff = height - width
        left = diff // 2
        right = diff - left
        padding = ((0, 0), (left, right), (0, 0))
    elif width > height:
        diff = width - height
        top = diff // 2
        bottom = diff - top
        padding = ((top, bottom), (0, 0), (0, 0))
    else:
        padding = ((0, 0), (0, 0), (0, 0))

    padded_image = np.pad(img_np, padding, mode="constant", constant_values=0)
    resized_image = cv2.resize(padded_image, (224, 224))
    img_array = np.expand_dims(resized_image, axis=0)
    img_array = preprocess_input(img_array)
    img_array = img_array.astype(np.float32)

    r = requests.post(
        "https://washmodel-p6kjjp4naq-uc.a.run.app:443/v1/models/mobile:predict",
        json={"instances": img_array.tolist()},
    )

    predicted_id = np.argmax(r.json()["predictions"][0])

    data = select_1(predicted_id)

    return render_template(
        "info.html",
        mark = data[0],
        name = data[1],
        score = data[2],
        effect = data[3],
        Advantage = data[4],
        Defect = data[5],
        Name_id = predicted_id
    )

@app.route('/range', methods=["POST"])
def range():
    age = request.form["age"][:1]
    skin = request.form["skin"][:1]
    pid = int(request.form["pid"])
    user_age = request.form["age"][1:]
    user_skin = request.form["skin"][1:]
    result = select_2(pid, age + skin)

    age_data = str(result[0]) if result[0] != None else "無使用者分享"
    skin_data = result[1] if result[1] != None else "無使用者分享"
    
    return render_template(
        "range.html",
        user_age = user_age,
        user_skin = user_skin,
        age = age_data,
        skin = skin_data,
        Name_id = pid
    )
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)