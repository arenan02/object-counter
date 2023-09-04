from io import BytesIO

from flask import Flask, jsonify, request

from counter import config

app = Flask(__name__)

count_action = config.get_count_action()
detection_action = config.get_detection_action()


def get_request_data() -> tuple[BytesIO, float]:
    """Get image and threshold from request data.

    Returns
    -------
    tuple[BytesIO, float]
        Image and threshold.
    """
    uploaded_file = request.files["file"]
    threshold = float(request.form.get("threshold", 0.5))
    image = BytesIO()
    uploaded_file.save(image)
    return image, threshold


@app.route("/object-count", methods=["POST"])
def object_detection():
    image, threshold = get_request_data()
    count_response = count_action.execute(image, threshold)
    return jsonify(count_response)


@app.route("/object-detection", methods=["POST"])
def get_objects():
    image, threshold = get_request_data()
    detection_response = detection_action.execute(image, threshold)
    return jsonify(detection_response)


if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
