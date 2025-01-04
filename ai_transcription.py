import openai
import os
from ai_transcription import extract_metrics_from_transcription

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_metrics_from_transcription(transcription):
    """
    Sends the transcription to OpenAI API and extracts item name, location, cost, and selling price.
    """
    prompt = f"""
    You are a helpful assistant for an inventory management app. 
    Parse the following transcription to extract these details:
    - Item Name
    - Location
    - Cost (£)
    - Selling Price (£)

    Transcription: "{transcription}"

    Format your response as a JSON object with these keys:
    {{
        "item_name": "...",
        "location": "...",
        "cost": "...",
        "selling_price": "..."
    }}
    """

    try:
        # Call the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can use other models like gpt-4 if available
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0
        )
        # Parse and return the response as JSON
        content = response['choices'][0]['message']['content']
        return eval(content)  # Convert the JSON string into a dictionary
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return None