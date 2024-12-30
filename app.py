from flask import Flask, request, jsonify
from ice_breaker import ice_breaker_with

app = Flask(__name__)


@app.route("/process", methods=["POST"])
def process():
    name = request.get_json("name", False)
    summary, profile_pic_url = ice_breaker_with(name=name["name"])
    return jsonify(
        {"summary_and_facts": summary.to_dict(), "picture_url": profile_pic_url}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8000)
