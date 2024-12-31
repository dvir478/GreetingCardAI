from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import os
import openai
from flask.cli import load_dotenv

app = Flask(__name__)

# Load OpenAI API key
load_dotenv()
openai.api_key = os.getenv("API_KEY")
if not openai.api_key:
    raise ValueError("API_KEY env var is not set.")

@app.route("/")
def greeting_card():
    prompt = "paint me a short greeting card for a real holiday that is occurring today{24.12.2024} somewhere in the world, specifying the name of the holiday in the greeting card."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Specify the GPT-3.5 model
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        result_text = response['choices'][0]['message']['content'].strip()  # Get the result text
    except openai.OpenAIError as e:
        return f"An error occurred: {e}", 500

    # Split result into title and content
    try:
        title, content = result_text.split("\n", 1)
    except ValueError:
        title = result_text
        content = ""

    return f"""
    <html>
        <body style="background-color: lightblue; text-align: center; padding-top: 50px; font-family: Arial;">
            <h1 style="color: darkblue;">{title}</h1>
            <p style="font-size: 20px; color: darkblue;">{content}</p>
        </body>
    </html>
    """

@app.route("/send_prompt", methods=["POST"])
def send_prompt():
    # Get the prompt from the form
    prompt = request.form.get("prompt")
    if not prompt:
        return "Prompt is required", 400

    # Send the prompt to the ChatGPT API using the new API call
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Specify the ChatGPT model
            messages=[
                {"role": "user", "content": prompt}
            ],          # Directly pass the prompt
            max_tokens=100,         # Limit the response length if needed
            n=1,                    # Request a single response
            stop=None,              # No specific stop sequence
            temperature=0.7         # Control randomness of the response
        )
        result_text = response['choices'][0]['message']['content'].strip()  # Get the response text
    except openai.OpenAIError as e:
        return f"An error occurred: {e}", 500

    # Save the result to a file
    with open("result.txt", "w") as file:
        file.write(result_text)

    return f"""
    <html>
        <body style="text-align: center; padding-top: 50px; font-family: Arial;">
            <h1>ChatGPT Response</h1>
            <p>{result_text}</p>
            <a href="/">Back to Home</a>
        </body>
    </html>
    """

@app.route("/download")
def download_card():
    # Generate greeting card image using the dynamically generated text
    prompt = "Write me a short greeting card for a real holiday that is occurring today somewhere in the world, specifying the name of the holiday in the greeting card."

    # Send the prompt to the ChatGPT API using the new API call
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo",  # Specify the ChatGPT model
            messages=[
                {"role": "user", "content": prompt}
            ],          # Directly pass the prompt
            max_tokens=100,         # Limit the response length if needed
            n=1,                    # Request a single response
            stop=None,              # No specific stop sequence
            temperature=0.7         # Control randomness of the response
        )
        result_text = response['choices'][0]['message']['content'].strip()  # Get the response text
    except openai.OpenAIError as e:
        return f"An error occurred: {e}", 500

    # Split the result_text into title and content (assuming the response is in "Title\nContent" format)
    try:
        title, content = result_text.split("\n", 1)
    except ValueError:
        title = result_text  # If no newline exists, treat the whole result as the title
        content = ""  # Leave content empty

    # Generate greeting card image with the generated text
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'lightblue')
    draw = ImageDraw.Draw(image)

    # Load a font
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()

    # Add text to the image (title and content from the generated result)
    text_x = width // 2
    draw.text((text_x - 200, 100), title, font=font, fill='darkblue')
    draw.text((text_x - 200, 200), content, font=font, fill='darkblue')

    # Save the image
    image_path = "greeting_card.png"
    image.save(image_path)

    # Serve the image file
    return send_file(image_path, mimetype='image/png', as_attachment=True)

# Web server run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
