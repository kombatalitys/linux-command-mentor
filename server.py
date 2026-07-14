import os
from flask import Flask, request, jsonify
from supabase import create_client, Client
from google import genai  # Correct import structure for google-genai SDK

app = Flask(__name__)

# 1. Grab Secure Environment Variables from Render
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Initialize Clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
ai_client = genai.Client(api_key=GEMINI_API_KEY)  # Modern SDK initialization

# =====================================================================
# 1. USER REGISTRATION ENDPOINT
# =====================================================================
@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400
    
    try:
        supabase.auth.sign_up({"email": email, "password": password})
        return jsonify({"message": "Registration successful! Check your email for a confirmation link."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# =====================================================================
# 2. USER LOGIN ENDPOINT
# =====================================================================
@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400
        
    try:
        auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        access_token = auth_response.session.access_token
        return jsonify({"token": access_token}), 200
    except Exception as e:
        return jsonify({"error": "Invalid email or password."}), 401

# =====================================================================
# 3. SECURED CHAT ENDPOINT (With Context Tracking)
# =====================================================================
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    user_message = data.get("prompt")
    user_token = request.headers.get("Authorization")
    
    if not user_token:
        return jsonify({"error": "Access denied. Missing authorization token."}), 401
    if not user_message:
        return jsonify({"error": "Prompt cannot be empty."}), 400
        
    try:
        token = user_token.replace("Bearer ", "")
        user_info = supabase.auth.get_user(token)
        user_id = user_info.user.id
    except Exception as e:
        return jsonify({"error": "Invalid or expired session. Please log in again."}), 401

    try:
        # A. Save user's prompt into their private history
        supabase.table("chat_history").insert({
            "user_id": user_id, 
            "sender": "User", 
            "text": user_message
        }).execute()
        
        # B. Retrieve the last 10 messages for context mapping
        history = supabase.table("chat_history") \
            .select("sender", "text") \
            .eq("user_id", user_id) \
            .order("timestamp", desc=False) \
            .limit(10) \
            .execute()
        
        # C. Turn database entries into memory context
        context = "Here is our past conversation context. Treat it as memory:\n\n"
        for message in history.data:
            context += f"{message['sender']}: {message['text']}\n"
        
        prompt_with_context = f"{context}\nNow respond to the last User message appropriately as a helpful assistant."
        
        # D. Run Gemini API Call using modern google-genai structure
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',  # Or 'gemini-1.5-pro' depending on your preference
            contents=prompt_with_context,
        )
        ai_response = response.text
        
        # E. Save the AI's generated response back to the database
        supabase.table("chat_history").insert({
            "user_id": user_id, 
            "sender": "AI", 
            "text": ai_response
        }).execute()
        
        return jsonify({"response": ai_response})
        
    except Exception as e:
        return jsonify({"error": f"Internal system or API error: {str(e)}"}), 500