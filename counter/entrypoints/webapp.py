from io import BytesIO

from flask import Flask, request, jsonify

from counter import config

# Leo: I needed to instantiate in this method, so I can initiate in the tests.
def create_app():
    
    app = Flask(__name__)
    
    count_action = config.get_count_action()
    
    @app.route('/object-count', methods=['POST'])
    def object_detection():
        
        threshold = float(request.form.get('threshold', 0.5))
        uploaded_file = request.files['file']
        model_name = request.form.get('model_name', "rfcn")
        image = BytesIO()
        uploaded_file.save(image)
        count_response = count_action.execute(image, threshold)
        return jsonify(count_response)
    
    return app


# Leo: Also, I'm not sure if this is the best way of doing this.I'll leave it as it was, just in case.
if __name__ == '__main__':
    app = create_app()
    app.run('0.0.0.0', debug=True)
