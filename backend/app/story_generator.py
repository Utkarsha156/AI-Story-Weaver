import os
import requests
import json
import base64
from uuid import uuid4

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
STABILITY_AI_API_KEY = os.environ.get('STABILITY_AI_API_KEY')
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL_NAME = "llama3-8b-8192"
IMAGE_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

def get_follow_up_question(chat_history):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    system_prompt = (
        "You are a state-driven assistant. Your task is to fill three slots in order: [genre, character, setting]. "
        "Look at the conversation and determine the next empty slot. "
        "If the 'genre' slot is empty, ask for the genre. "
        "If 'genre' is filled but 'character' is empty, ask for the main character. "
        "If 'genre' and 'character' are filled but 'setting' is empty, ask for the setting. "
        "Once all three slots are filled, your ONLY response must be the exact text: READY_TO_GENERATE. "
        "Do not ask more than one question at a time. Do not invent details. Be brief."
    )
    conversation = [{"role": "system", "content": system_prompt}] + chat_history
    payload = {"model": GROQ_MODEL_NAME, "messages": conversation, "max_tokens": 60, "temperature": 0.7}
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        print(f"Groq API Error: {e}")
        return "Sorry, I'm having trouble thinking right now. Could you repeat that?"

def generate_story_text(chat_history, theme="India"):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    user_details = "\n".join([f"- {msg['content']}" for msg in chat_history if msg['role'] == 'user'])
    
    # ENHANCED PROMPT - More specific about paragraph count and structure
    system_prompt = (
        f"You are a master storyteller creating a {theme}n themed children's story. "
        f"CRITICAL INSTRUCTIONS: "
        f"1. Your story must contain EXACTLY 10 paragraphs - no more, no less. "
        f"2. Each paragraph should be 3-4 sentences long. "
        f"3. Separate each paragraph with exactly two newlines (\\n\\n). "
        f"4. Do not include any titles, headings, page numbers, or introductory text. "
        f"5. Start directly with paragraph 1 of the story. "
        f"6. Make the story complete with beginning, middle, and end across these 10 paragraphs. "
        f"7. Include rich {theme}n cultural elements. "
        f"8. Stop after exactly 10 paragraphs - do not continue the story beyond this. "
        f"Remember: EXACTLY 10 PARAGRAPHS, each separated by \\n\\n"
    )
    
    payload = {
        "model": GROQ_MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt}, 
            {"role": "user", "content": f"Create a complete story in exactly 10 paragraphs based on these details:\n{user_details}"}
        ],
        "max_tokens": 2000,  # Reduced to prevent over-generation
        "temperature": 0.7,  # Reduced for more consistent output
        "stop": ["Paragraph 11", "11.", "END", "The End"]  # Stop tokens to prevent over-generation
    }
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        full_text = response.json()['choices'][0]['message']['content']
        
        print(f"DEBUG: Raw AI response length: {len(full_text)} characters")
        
        # STRICT PARAGRAPH PROCESSING
        # Split by double newlines and clean
        raw_paragraphs = [p.strip() for p in full_text.split('\n\n') if p.strip()]
        
        # Remove any numbered prefixes (1., 2., Paragraph 1:, etc.)
        clean_paragraphs = []
        for para in raw_paragraphs:
            # Remove paragraph numbering patterns
            import re
            cleaned = re.sub(r'^(Paragraph\s*\d+[:.]\s*|\d+[:.]\s*)', '', para.strip())
            if cleaned and len(cleaned.split()) > 10:  # Only keep substantial paragraphs
                clean_paragraphs.append(cleaned)
        
        print(f"DEBUG: After cleaning, got {len(clean_paragraphs)} substantial paragraphs")
        
        # FORCE EXACTLY 10 PARAGRAPHS
        if len(clean_paragraphs) > 10:
            print(f"DEBUG: Trimming from {len(clean_paragraphs)} to exactly 10 paragraphs")
            final_paragraphs = clean_paragraphs[:10]
        elif len(clean_paragraphs) < 10:
            print(f"DEBUG: Only got {len(clean_paragraphs)} paragraphs, need 10")
            final_paragraphs = clean_paragraphs
            # Add continuation paragraphs if needed
            while len(final_paragraphs) < 10:
                final_paragraphs.append("The adventure continued as our characters discovered new wonders and faced new challenges in their journey.")
        else:
            final_paragraphs = clean_paragraphs
        
        # FINAL VERIFICATION
        final_paragraphs = final_paragraphs[:10]  # Absolute safety limit
        print(f"DEBUG: Returning exactly {len(final_paragraphs)} paragraphs")
        
        # Log first few words of each paragraph for debugging
        for i, para in enumerate(final_paragraphs):
            preview = ' '.join(para.split()[:8]) + '...' if len(para.split()) > 8 else para
            print(f"DEBUG: Paragraph {i+1}: {preview}")
        
        return final_paragraphs
        
    except requests.exceptions.RequestException as e:
        print(f"Groq Story Gen Error: {e}")
        return ["Error: Could not generate the story text."]

def generate_image_for_paragraph(text, theme="India"):
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    prompt = f"An illustration for a children's story with a vibrant {theme}n theme. The scene is: {text}. Style: digital painting, bright colors, child-friendly, detailed illustration."
    payload = {"inputs": prompt}
    try:
        response = requests.post(IMAGE_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        image_data = response.content
        image_filename = f"{uuid4()}.jpeg"
        image_path = os.path.join('app', '..', 'static', 'images', image_filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        with open(image_path, "wb") as f:
            f.write(image_data)
        return f"/static/images/{image_filename}"
    except requests.exceptions.RequestException as e:
        print(f"Hugging Face Image Gen Error: {e}")
        return None