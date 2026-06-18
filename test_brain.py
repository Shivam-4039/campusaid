from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load knowledge base from JSON file
with open("knowledge_base.json", "r") as f:
    knowledge = json.load(f)

# Convert JSON to readable policy text
def build_policy_text(knowledge):
    policy_text = ""
    for key, section in knowledge.items():
        policy_text += f"\n{section['title'].upper()}:\n"
        for rule in section['rules']:
            policy_text += f"- {rule}\n"
    return policy_text

college_policy = build_policy_text(knowledge)

system_prompt = f"""
You are CampusAid, a smart and empathetic AI assistant for ABC College students.

Your job is to help students with their queries about college policies, rules, deadlines, and procedures.

RULES YOU MUST FOLLOW:
1. Answer ONLY based on the college policy provided below.
2. If a question involves multiple policies, reason across all of them and give ONE clear answer.
3. If the answer is not in the policy, say exactly: "This query needs to be handled by the college office directly. Please visit Room 101 or call 1800-XXX-XXXX."
4. Always be empathetic. If a student sounds stressed, acknowledge it before answering.
5. Keep answers clear, structured, and easy to understand.
6. Never make up rules that are not in the policy.

COLLEGE POLICY:
{college_policy}
"""

conversation_history = []

print("=" * 50)
print("Welcome to CampusAid 🎓")
print("Your AI companion for ABC College")
print("Type 'exit' to quit")
print("=" * 50)
print()

while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "exit":
        print("CampusAid: Take care! All the best with your studies. 👋")
        break

    if not user_input:
        continue

    conversation_history.append({
        "role": "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt}
        ] + conversation_history,
        model="llama-3.1-8b-instant"
    )

    reply = response.choices[0].message.content

    conversation_history.append({
        "role": "assistant",
        "content": reply
    })

    print(f"\nCampusAid: {reply}\n")