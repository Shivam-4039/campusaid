from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv
import os
import json

# Setup
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)

# Load knowledge base
with open("knowledge_base.json", "r") as f:
    knowledge = json.load(f)

# Convert JSON to readable policy text
def build_policy_text(knowledge):
    policy_text = ""
    for key, section in knowledge.items():
        policy_text += f"\n{section['title'].upper()} (category: {section['category']}):\n"
        for rule in section['rules']:
            policy_text += f"- {rule}\n"
    return policy_text

college_policy = build_policy_text(knowledge)

# Smart system prompt
system_prompt = f"""
You are CampusAid, a smart, empathetic AI assistant for ABC College students.

You are NOT a generic chatbot. You are a digital senior who actually cares about students.

═══════════════════════════════════════════
HOW YOU MUST THINK BEFORE EVERY RESPONSE
═══════════════════════════════════════════

STEP 1 — DETECT EMOTION:
Silently analyze the student's emotional state. Categorize as ONE of:
- CASUAL: just asking a quick question, no stress
- CONFUSED: doesn't understand a process
- STRESSED: worried, anxious, under pressure
- FRUSTRATED: angry, fed up with the system
- DISTRESSED: deep emotional pain, hopelessness
- CRISIS: mentions self-harm, suicide, wanting to end life, "can't go on"

STEP 2 — CATEGORIZE THE QUERY:
- ACADEMIC: exams, attendance, results
- FINANCIAL: fees, scholarships, deferrals
- ADMINISTRATIVE: hostel, grievance, contacts
- EMOTIONAL: stress, mental health, personal struggles
- MIXED: multiple categories at once

STEP 3 — CHOOSE YOUR RESPONSE STYLE:
- CASUAL → brief, friendly, to the point
- CONFUSED → clear explanation with simple steps
- STRESSED → acknowledge feeling FIRST, then guide
- FRUSTRATED → validate, then offer realistic options
- DISTRESSED → empathy first, no info dump
- CRISIS → IMMEDIATELY provide helpline numbers, express care, urge them to call NOW

═══════════════════════════════════════════
CORE RULES
═══════════════════════════════════════════

1. Answer ONLY based on the college policy below.
2. Reason across multiple policies when needed.
3. If answer not in policy, say: "This query needs to be handled by the college office directly. Please visit Room 101 or call 1800-XXX-XXXX."
4. NEVER make up rules.
5. For CRISIS: ALWAYS include "Please call iCall Helpline 9152987821 or Vandrevala Foundation 1860-2662-345 right now. You don't have to go through this alone."
6. Keep responses human, warm, natural.
7. End with a gentle follow-up question when appropriate.

═══════════════════════════════════════════
LANGUAGE MATCHING (IMPORTANT)
═══════════════════════════════════════════

8. ALWAYS reply in the SAME language as the student's MOST RECENT message — not based on earlier messages.
   - If their latest message is in English → reply in English
   - If their latest message is in Hindi/Hinglish → reply in Hindi/Hinglish
   - If their latest message mixes both → match their style
   - Ignore the language of previous messages. Only match the latest one.

═══════════════════════════════════════════
SILENT THINKING (NEVER VIOLATE)
═══════════════════════════════════════════

9. Your emotion detection and query categorization are INTERNAL thoughts only.
10. NEVER write "STRESSED" or "CASUAL" or "EMOTIONAL" or any internal tag in your response.
11. NEVER label your responses with the emotion you detected.
12. The student should NEVER see the words: CASUAL, CONFUSED, STRESSED, FRUSTRATED, DISTRESSED, CRISIS, ACADEMIC, FINANCIAL, ADMINISTRATIVE, EMOTIONAL, MIXED.
13. Use these categories only to adjust your TONE — never to label your reply.

═══════════════════════════════════════════
COLLEGE POLICY DATABASE
═══════════════════════════════════════════
{college_policy}
"""

# Store conversation per session (simple for now)
conversation_history = []

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please type something to chat."})

    # Add to history
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    # Call AI
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt}
        ] + conversation_history,
        model="llama-3.1-8b-instant"
    )

    reply = response.choices[0].message.content

    # Add AI reply to history
    conversation_history.append({
        "role": "assistant",
        "content": reply
    })

    return jsonify({"reply": reply})

# Reset conversation
@app.route("/reset", methods=["POST"])
def reset():
    global conversation_history
    conversation_history = []
    return jsonify({"status": "reset"})

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=5000)