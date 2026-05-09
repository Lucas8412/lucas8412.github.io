L0KI/
│
├── main.py              # Starts everything
├── brain.py             # Jarvis logic + ChatGPT
├── memory.py            # SQLite long-term memory
├── voice.py             # Voice input/output
├── gui.py               # Jarvis GUI
├── telegram_bot.py      # Telegram bot
├── requirements.txt
└── loki_memory.db       # Auto-created
import os
from openai import OpenAI
from memory import get_context, save_message

SYSTEM_PROMPT = """
You are L0KI, an advanced AI assistant similar to JARVIS from Iron Man.

Rules:
- Speak naturally and intelligently
- Maintain conversation context
- Ask follow-up questions when needed
- Be calm, confident, and helpful
- Remember past interactions
- Think logically before answering

Never mention system rules.
"""

client = OpenAI(api_key=os.getenv("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"))

class L0KI:
    def chat(self, user_input):
        context = get_context()

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"""
Conversation so far:
{context}

User: {user_input}
Respond like JARVIS.
"""}
            ]
        )

        reply = response.choices[0].message.content
        save_message("user", user_input)
        save_message("loki", reply)
        return reply
import sqlite3

conn = sqlite3.connect("loki_memory.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY,
    speaker TEXT,
    message TEXT,
    time DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

def save_message(speaker, message):
    cur.execute("INSERT INTO memory (speaker, message) VALUES (?, ?)", (speaker, message))
    conn.commit()

def get_context(limit=8):
    cur.execute("SELECT speaker, message FROM memory ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()[::-1]
    return "\n".join([f"{s}: {m}" for s, m in rows])
import speech_recognition as sr
import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate", 165)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except:
        return ""
import tkinter as tk
from brain import L0KI
from voice import speak

loki = L0KI()

def send():
    user = entry.get()
    chat.insert(tk.END, f"You: {user}\n")
    reply = loki.chat(user)
    chat.insert(tk.END, f"L0KI: {reply}\n")
    speak(reply)
    entry.delete(0, tk.END)

def run_gui():
    global entry, chat
    root = tk.Tk()
    root.title("L0KI – JARVIS AI")

    chat = tk.Text(root, height=20, width=60)
    chat.pack()

    entry = tk.Entry(root, width=50)
    entry.pack()

    tk.Button(root, text="Send", command=send).pack()
    root.mainloop()
from telegram.ext import Application, MessageHandler, filters
from brain import L0KI

loki = L0KI()

async def reply(update, context):
    response = loki.chat(update.message.text)
    await update.message.reply_text(response)

def run_telegram(token):
    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT, reply))
    app.run_polling()

import threading
from brain import L0KI
from voice import listen, speak
from gui import run_gui
# from telegram_bot import run_telegram

loki = L0KI()

def voice_loop():
    speak("L0KI online.")
    while True:
        command = listen()
        if command.lower() in ["exit", "stop", "bye"]:
            speak("Shutting down.")
            break
        reply = loki.chat(command)
        speak(reply)

if __name__ == "__main__":
    threading.Thread(target=run_gui).start()
    threading.Thread(target=voice_loop).start()
    # run_telegram("YOUR_TELEGRAM_BOT_TOKEN")
