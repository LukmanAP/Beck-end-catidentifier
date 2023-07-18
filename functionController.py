import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.cloud import storage

load_dotenv()
url = os.getenv("storage_url")
credentials_info = {
    "type": "service_account",
    "project_id": os.getenv("project_id"),
    "private_key_id": os.getenv("private_key_id"),
    "private_key": os.getenv("private_key").replace("\\n", "\n"),
    "client_email": os.getenv("client_email"),
    "client_id": os.getenv("client_id"),
    "auth_uri": os.getenv("auth_uri"),
    "token_uri": os.getenv("token_uri"),
    "auth_provider_x509_cert_url": os.getenv("auth_provider_x509_cert_url"),
    "client_x509_cert_url": os.getenv("client_x509_cert_url"),
}
credentials_obj = service_account.Credentials.from_service_account_info(
    credentials_info
)

client = storage.Client(credentials=credentials_obj)
bucket = client.get_bucket(os.getenv("bucket_name"))

# Fungsi untuk menyimpan gambar dari request, return image path


def uploadImage(request):
    file = request.files["image"]

    blob = bucket.blob(file.filename)

    blob.content_type = "image/jpeg"

    blob.upload_from_string(file.read(), content_type=file.content_type)

    return file.filename


def predict(model, image_path):
    import cv2  # import library
    import numpy as np
    from urllib.request import urlopen

    image_size = (224, 224)  # Semua input di convert ke size ini

    # Load Image
    response = urlopen(url + image_path)
    image_array = np.asarray(bytearray(response.read()), dtype=np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)  # load image
    img = cv2.resize(img, image_size)  # resize
    img = (
        img.astype("float32") / 255.0
    )  # Convert dan normalize sehingga menjadi antara 0-1
    img = np.expand_dims(img, axis=0)  # tambah 1 dimensi

    predictions = model.predict(img)  # ngepredict dengan model

    class_labels = [
        "Bengal",
        "Bombay",
        "Persian",
        "Torbie",
        "Tuxedo",
    ]  # Ini untuk label output

    for i, prediction in enumerate(predictions[0]):  # Iterasi ke semua hasil prediksi
        class_label = class_labels[i]
        confidence = prediction * 100  # Sehingga bentuk persen
        print("Class:", class_label)
        print("Confidence:", confidence, "%")

    predicted_class_index = np.argmax(
        predictions[0]
    )  # Urutkan ke terbesar untuk dapat hasil terbaik
    predicted_class_label = class_labels[predicted_class_index]
    highest_confidence = predictions[0][predicted_class_index] * 100

    blob = bucket.blob(image_path)

    # Delete the image
    blob.delete()

    data = {}
    data["label"] = predicted_class_label
    data["percentage"] = highest_confidence
    return data


def getCat(getAll=True, label=""):
    import os
    import mysql.connector
    from dotenv import load_dotenv

    load_dotenv()

    # Configure the MySQL database connection
    db = mysql.connector.connect(
        host=os.getenv("HOST"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE"),
    )

    # Create a cursor object to interact with the database
    cursor = db.cursor()

    # Execute a SELECT query
    if getAll:
        query = "SELECT * FROM cats"
    else:
        query = "SELECT * FROM cats where cat_race like '" + label + "'"
    cursor.execute(query)

    # Fetch all the rows returned by the query
    data = cursor.fetchall()

    # Convert the data to a JSON response
    result = []
    for row in data:
        result.append(
            {
                "catId": row[0],
                "catRaces": row[1],
                "catDesc": row[2],
                "catCare": row[3],
                "catImage": row[4],
                # Add more columns as needed
            }
        )
    # Close the cursor and database connection
    cursor.close()
    db.close()

    # Return the JSON response
    return result
