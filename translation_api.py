from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from googletrans import Translator
import asyncio as asynchio
#using googletrans as a simplified translation API since non-commercial usage

app = Flask(__name__)
CORS(app, support_credentials=True)

MAX_TEXT_LENGTH = 15000

async def get_translations(texts, locale):
    translater = Translator()
    return_translation = []
    for text in texts:
        try:
            translated_text = await translater.translate(text, dest=locale)
            return_translation.append(translated_text)
        except Exception as e:
            return_translation.append({"error": f"Error translating '{text}': {str(e)}"})
            #Log "Translation Error" for enterprise system
            print(f"Error translating '{text}': {str(e)}")
    return return_translation

async def get_translation(text, locale):
    translater = Translator()
    try:
        return await translater.translate(text, dest=locale)
    except Exception as e:
        #Log "Translation Error" for enterprise system
        print(f"Error translating '{text}': {str(e)}")
        return {"error": f"Error translating '{text}': {str(e)}"}
    
@app.route("/running", methods=["GET"])
def running():
    return jsonify({"status": "running"}), 200

@app.route("/translate/<locale>", methods=["POST"])
def translate_many(locale):
    try:
        data = request.get_json()
        if "text_obj" not in data:
            #log "Invalid Input Error" for enterprise system
            return jsonify({"error": "Invalid input data"}), 418

        text_obj = data.get("text_obj")

        # Ensure at least one text field is provided
        if not any(text_obj.values()):
            #log "Missing Text Fields Error" for enterprise system
            return jsonify({"error": "Missing text fields"}), 400

        texts = [text for text in text_obj.values() if text is not None]

        return_text = asynchio.run(get_translations(texts, locale))
        if any(isinstance(item, dict) and "error" in item for item in return_text):
            #log "Translation Failed Error" for enterprise system
            return jsonify({"error": "One or more translations failed", "details": return_text}), 500

        print(f"Translated texts: {return_text}")
        return jsonify({
            f"text_{i+1}": translated.text for i, translated in enumerate(return_text)
        })
    except Exception as e:
        #Log "Unexpected Error" for enterprise system
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route("/translate_custom/<locale>", methods=["POST"])
def translate_one(locale):
    try:
        data = request.get_json()
        if not data or "text_obj" not in data:
            #log "Invalid Input Error" for enterprise system
            return jsonify({"error": "Invalid input data"}), 418

        text_obj = data.get("text_obj")
        if len(text_obj) > MAX_TEXT_LENGTH:
            #Log "Maximum Characters Exceeded Error" exceeded for enterprise system 
            return jsonify({"error": "Text length exceeds limit."}), 413

        return_text = asynchio.run(get_translation(text_obj, locale))
        if isinstance(return_text, dict) and "error" in return_text:
            #Log "Return Text Error" for enterprise system
            return jsonify({"error": return_text["error"]}), 500

        return jsonify({"custom_text": return_text.text})
    except Exception as e:
        #Log "Unexpected Error" for enterprise system
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == "__main__":
    # solely for dev environment
    app.run(debug=True)


##COMMENTS AND SCRATCH WORK

### cmds
# gcloud auth list
# gcloud services enable translate.googleapis.com
# proj id: sharp-leaf-455813-s9


#Google Translate API
# PROJECT_ID = "sharp-leaf-455813-s9"
# assert PROJECT_ID
# PARENT = f"projects/{PROJECT_ID}/locations/global"

# def print_supported_languages(display_language_code: str):
#     client = translate.TranslationServiceClient()

#     response = client.get_supported_languages(
#         parent=PARENT,
#         display_language_code=display_language_code,
#     )

#     languages = response.languages
#     print(f" Languages: {len(languages)} ".center(60, "-"))
#     for language in languages:
#         language_code = language.language_code
#         display_name = language.display_name
#         print(f"{language_code:10}{display_name}")