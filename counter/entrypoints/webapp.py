from io import BytesIO

from flask import Flask, request, jsonify

from counter import config


def create_app():
    app = Flask(__name__)

    count_action = config.get_count_action()

    @app.route("/object-count", methods=["POST"])
    def object_detection():
        threshold = float(request.form.get("threshold", 0.5))
        uploaded_file = request.files["file"]
        request.form.get("model_name", "rfcn")
        image = BytesIO()
        uploaded_file.save(image)
        count_response = count_action.execute(image, threshold)
        return jsonify(count_response)

    @app.route("/predict", methods=["POST"])
    def predict():
        """
        This is the endpoint to return predictions for objects detected in the image
        """
        # Get the threshold and model name from the request
        threshold = float(request.form.get("threshold", 0.5))
        uploaded_file = request.files["file"]

        if not uploaded_file:
            return jsonify({"error": "No file uploaded"}), 400

        # Read image file into memory
        image = BytesIO()
        uploaded_file.save(image)

        # Call the count action to get the count of objects detected
        predictions = count_action.predict(image, threshold)
        return jsonify(predictions)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run("0.0.0.0", debug=True)
