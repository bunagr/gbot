from flask import Flask, jsonify, request
import toml

# Load configuration from the TOML file
config = toml.load("config.toml")
URL = config["api"]["url"]
SECRET = config["api"]["secret"]

# Initialize Flask app
app = Flask(__name__)

# Maintenance mode flag
maint_mode = True

@app.route("/api", methods=["GET"])
def api():
    """API endpoint to check the status."""
    global maint_mode
    # Check if the API is in maintenance mode
    if maint_mode:
        return jsonify({
            "status": "maintenance",
            "message": "🚧 The API is currently in maintenance mode."
        }), 503  # Return HTTP status code 503 for service unavailable
    
    # If not in maintenance mode, handle the request (e.g., API logic goes here)
    return jsonify({
        "status": "ok",
        "message": "The API is up and running!"
    })

@app.route("/maintenance", methods=["POST"])
def toggle_maintenance():
    """Toggle maintenance mode."""
    global maint_mode

    # Check if the correct secret is provided
    secret = request.json.get("secret")
    if secret != SECRET:
        return jsonify({"error": "Unauthorized"}), 403  # Unauthorized

    # Toggle the maintenance mode
    maint_mode = not maint_mode

    # Return the updated maintenance mode status
    return jsonify({
        "status": "success",
        "maintenance_mode": maint_mode,
        "message": "Maintenance mode has been enabled." if maint_mode else "Maintenance mode has been disabled."
    })


@app.route("/")
def home():
    """Home endpoint to check if the server is running."""
    return "Flask API is running!"


if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True)
