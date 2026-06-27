from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from detector import detect_with_groq
from audit import save_log, get_log

from confidence import calculate_confidence    # milestone 4
from labels import get_label
from detector import stylometric_score

import uuid
from datetime import datetime

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"]
)


@app.route("/")
def home():

    return jsonify(
        {
            "message": "Provenance Guard API Running"
        }
    )


@app.route("/submit", methods=["POST"])
def submit():

    data = request.get_json()

    text = data["text"]

    creator = data["creator_id"]

    llm = detect_with_groq(text)
    
    style = stylometric_score(text)

    final = calculate_confidence(llm["llm_score"], style)

    # llm_score = llm["llm_score"] * 0.8

    # final = calculate_confidence(llm_score, style)
    
    #final = calculate_confidence(llm["llm_score"],style)
    
    label = get_label(final["attribution"])
    
    content_id = str(uuid.uuid4())

    entry = {
        "content_id": content_id,
        "creator_id": creator,
        "timestamp": datetime.utcnow().isoformat(),
        "llm_score": llm["llm_score"],
        "stylometric_score": style,
        "confidence": final["confidence"],
        "attribution": final["attribution"],
        "status": "classified"
        }
    
    print("LLM:", llm)      # for debugging purp
    print("STYLE:", style)  # for debugging purp

    save_log(entry)

    return jsonify(
        {
        "content_id": content_id,
        "creator_id": creator,
        "llm_score": llm["llm_score"],
        "stylometric_score": style,
        "confidence": final["confidence"],
        "attribution": final["attribution"],
        "label": label
        }
    )


@app.route("/log")
def log():

    return jsonify(
        {
            "entries": get_log()
        }
    )


if __name__ == "__main__":
    app.run(debug=True)