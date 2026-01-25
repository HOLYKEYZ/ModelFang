"""
ModelFang Analyst UI Server

Simple Flask server for local visualization and execution.
"""

import json
import os
import threading
from pathlib import Path
from flask import Flask, jsonify, request, render_template

from modelfang.api import run_attack
from modelfang.config.loader import load_models_config

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))

# Create directories if they don't exist
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

@app.route("/")
def index():
    """Render the main dashboard."""
    try:
        models_conf = load_models_config()
        targets = [
            {"id": m.model_id, "name": m.model_name, "provider": m.provider} 
            for m in models_conf.get_targets()
        ]
    except Exception:
        targets = []
    
    return render_template("index.html", targets=targets)

@app.route("/api/execute", methods=["POST"])
def execute_attack():
    """Execute an attack via API."""
    data = request.json
    attack_id = data.get("attack_id", "template:standard")
    model_id = data.get("model_id")
    context = data.get("context", {})
    
    if not model_id:
        return jsonify({"error": "Model ID is required"}), 400
        
    try:
        # Run in a separate thread to not block (simplified for demo)
        # In production this would be a task queue (Celery/Redis)
        result = run_attack(
            attack_id=attack_id,
            target_model_id=model_id,
            context=context,
            config_dir=os.environ.get("MODELFANG_CONFIG_DIR")
        )
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/models")
def list_models():
    """List available models."""
    try:
        conf = load_models_config()
        return jsonify({
            "targets": [m.model_id for m in conf.get_targets()],
            "evaluators": [m.model_id for m in conf.get_evaluators()]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def start_server(host="127.0.0.1", port=5000, debug=True):
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    start_server()
