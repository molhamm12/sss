from flask import Flask, request, jsonify
import openai
import logging
import requests

app = Flask(__name__)

# إعداد مفاتيح API مباشرة في الكود
openai.api_key = "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"
deepai_api_key = "76f97ccf-8b48-4fad-b318-1d39ac9a8dc2"

# رابط الفيديو
video_url = 'https://drive.google.com/uc?id=1M3-XwNSloN5pn3fuXYACEqJlca-9JcXb'

# إعداد تسجيل السجلات
logging.basicConfig(level=logging.DEBUG)

def analyze_video(video_url):
    try:
        response = requests.post(
            "https://api.deepai.org/api/video-recognition",
            data={
                'video': video_url,
            },
            headers={'api-key': deepai_api_key}
        )
        app.logger.debug(f"Request sent to DeepAI: URL={response.url}, Status Code={response.status_code}, Response={response.text}")
        response.raise_for_status()  # Raises HTTPError, if one occurred
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        app.logger.error(f"HTTP error occurred: {http_err}")  # Python 3.6
        return {"error": f"HTTP error occurred: {http_err}"}
    except Exception as err:
        app.logger.error(f"Other error occurred: {err}")  # Python 3.6
        return {"error": f"Other error occurred: {err}"}

@app.route("/chat", methods=['POST'])
def chat():
    try:
        if request.content_type != 'application/json':
            return jsonify({"response": "Unsupported Media Type: Content-Type must be application/json"}), 415

        incoming_msg = request.json.get('message', '').strip()
        app.logger.debug(f"Received message: {incoming_msg}")

        if not incoming_msg:
            return jsonify({"response": "The message is empty. Please provide a valid message."}), 400

        # تحليل الفيديو باستخدام DeepAI
        analysis_result = analyze_video(video_url)
        app.logger.debug(f"Analysis result: {analysis_result}")

        if 'output' in analysis_result:
            labels = analysis_result['output']
            if labels:
                answer = "The video contains: " + ", ".join(labels)
            else:
                answer = "No recognizable objects found in the video."
        else:
            error_msg = analysis_result.get('error', 'Unknown error occurred')
            answer = f"Error analyzing the video: {error_msg}. Please try again with a different video."

        app.logger.debug(f"Sending response: {answer}")
        return jsonify({"response": answer})
    except Exception as e:
        app.logger.error(f"Error: {str(e)}", exc_info=True)
        return jsonify({"response": "Sorry, an error occurred. Please try again later."}), 500

if __name__ == "__main__":
    app.run(debug=True)
