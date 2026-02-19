from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/travel', methods=['GET'])
def get_travel_guide():
    """ Returns a travel guide suggestion based on user input. """
    destination = request.args.get('destination')
    if not destination:
        return jsonify({'error': 'Missing destination parameter'}), 400

    # Sample travel guide data (you can expand this)
    travel_guides = {
        'Paris': 'Visit the Eiffel Tower and enjoy a Seine River cruise.',
        'New York': 'Explore Central Park and check out the Statue of Liberty.',
        'Tokyo': 'Experience the culture at Shibuya and visit the historic temples.'
    }

    suggestion = travel_guides.get(destination)
    if suggestion:
        return jsonify({'destination': destination, 'suggestion': suggestion}), 200
    else:
        return jsonify({'error': 'No travel guide available for this destination.'}), 404

if __name__ == '__main__':
    app.run(debug=True)