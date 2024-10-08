from flask import Flask, request, jsonify
from api_client import APIClient

app = Flask(__name__)

@app.route('/api/category/<category_name>', methods=['GET'])
def get_category_data(category_name):
    """
    Endpoint to fetch data for a specific category based on filters and parameters.
    """
    # Create an instance of APIClient for the requested category
    try:
        api_client = APIClient(category_name=category_name, config_path="config.json")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Extract query parameters from the request
    query_params = request.args.to_dict()

    # Separate filters and additional parameters
    selected_filters = {}
    parameters = {}

    # Get the list of valid filters for the category
    filter_manager = api_client.filter_manager
    filters = filter_manager.get_filters(category_name)
    valid_filter_names = [f.name.lower() for f in filters]

    for key, value in query_params.items():
        key_lower = key.lower()
        if key_lower in valid_filter_names:
            # Handle range filters
            if filter_manager.is_range_filter(category_name, key):
                # Expecting values in the format 'min-max'
                try:
                    min_val, max_val = map(float, value.split('-'))
                    selected_filters[key] = {"min": min_val, "max": max_val}
                except ValueError:
                    return jsonify({"error": f"Invalid range format for filter '{key}'. Use 'min-max'."}), 400
            else:
                selected_filters[key] = value
        else:
            # Treat as an additional parameter
            parameters[key] = value

    # Fetch data using the APIClient
    data = api_client.fetch_products(selected_filters=selected_filters, parameters=parameters)

    if data:
        return jsonify(data), 200
    else:
        return jsonify({"error": "Failed to fetch data."}), 500

if __name__ == '__main__':
    # Run the server on localhost:5000
    app.run(debug=True)

    # Example request:
    #http://localhost:5000/api/category/COOLER?Subcategory=AirCooler&Price=100-1900&Brand=Noctua&sorting=PRICE_asc&size=12
