import os
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from review_orchestrator import orchestrate_review

ps_start = time.time()

load_dotenv()

app = Flask(__name__)
CORS(app)


@app.get("/api/health")
def health():
  return jsonify({"status": "ok", "uptime": time.time() - ps_start})


@app.post("/api/review")
def review():
  payload = request.get_json(silent=True) or {}

  try:
    result = orchestrate_review(payload)
    return jsonify(result)
  except ValueError as e:
    return jsonify({"error": str(e)}), 400
  except Exception as e:
    app.logger.exception("review error")
    return jsonify({"error": "Failed to generate review"}), 500


if __name__ == "__main__":
  port = int(os.getenv("PORT", 5001))
  app.run(host="0.0.0.0", port=port, debug=True)
