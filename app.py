from flask import Flask, request
from tensorflow import keras
from dotenv import load_dotenv
import functionController
import os, json

load_dotenv()


def file_exists(file_path):
    return os.path.exists(file_path)


# Example usage
file_path = "models/model.h5"
if not file_exists(file_path):
    import gdown

    destination = "models/model.h5"
    url = f"https://drive.google.com/uc?id=1nc_0DXH7FlLt-YITYmEdAMiaZ6QobMJD"
    gdown.download(url, destination, quiet=False)

app = Flask(__name__)

# Load the H5 model
app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER")
model = keras.models.load_model("models/model.h5")


@app.route("/")
def home():
    return "This is Home!"


@app.route("/upload", methods=["POST"])
def upload():
    # Check image exist
    if "image" not in request.files:
        return "No image file uploaded", 400
    # Check if file exist
    if request.files["image"].filename == "":
        return "No selected image file", 400
    # Check if the file is an allowed image format (e.g., JPEG, PNG)
    allowed_extensions = {"jpg", "jpeg", "png"}
    if request.files["image"].filename.split(".")[-1].lower() not in allowed_extensions:
        return "Invalid image file format", 400

    # Save Image and get image path
    image_path = functionController.uploadImage(request)

    # Get cat Labels with machine learning models
    datajson = functionController.predict(model, image_path)
    # datajson = json.loads(datajson)

    # Get cat information
    catRaces = datajson["label"]
    datajson["race"] = functionController.getCat(False, catRaces)

    return json.dumps(datajson)


@app.route("/cats")
def cats():
    result = functionController.getCat()
    return result


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
