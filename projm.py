import os
import json
import queue
import threading
import sounddevice as sd
import pyttsx3
import arabic_reshaper
from bidi.algorithm import get_display
from vosk import Model, KaldiRecognizer
from openai import OpenAI
import customtkinter as ctk
import random

# ================= PROMPTS DATABASE =================
PROMPTS_DB = {
    "medical": [
        "Explain the symptoms of common flu to a patient.",
        "Provide first-aid advice for minor injuries.",
        "What are possible causes of this symptom?",
        "Explain a medical condition in simple terms.",
        "Give general health advice (non-diagnostic).",
        "What questions should a patient ask a doctor?",
        "Explain how a medical test works.",
        "Provide lifestyle tips for better health.",
        "Explain medication usage and precautions.",
        "How can someone manage chronic pain safely?"
    ],
    "technology": [
        "Explain this technology concept in simple terms.",
        "Describe how artificial intelligence works.",
        "Give beginner tips for learning programming.",
        "Explain the difference between hardware and software.",
        "What are the latest trends in technology?",
        "Explain cybersecurity risks and prevention.",
        "How does the internet work?",
        "Explain cloud computing to a beginner.",
        "Give advice on choosing a computer or phone.",
        "Explain this technical error and how to fix it."
    ],
    "finance": [
        "Explain basic financial concepts to a beginner.",
        "Give tips for managing personal finances.",
        "Explain how the stock market works.",
        "What are safe investment strategies?",
        "Explain budgeting in simple terms.",
        "What are common financial mistakes to avoid?",
        "Explain cryptocurrency risks and benefits.",
        "Give advice for saving money efficiently.",
        "Explain loans and interest rates.",
        "How can someone improve their financial planning?"
    ],
    "education": [
        "Explain this topic like I am a student.",
        "Create a simple lesson plan for this subject.",
        "Summarize this concept for studying.",
        "Explain this theory with examples.",
        "Help me understand this academic topic.",
        "Create practice questions for learning.",








        
        "Explain this topic step by step.",
        "Provide study tips for this subject.",
        "Simplify this complex idea.",
        "Explain the importance of this topic."
    ],
    "legal": [
        "Explain this legal concept in simple language.",
        "What are general legal rights in this situation?",
        "Explain legal terms related to this issue.",
        "What steps should someone take legally?",
        "Explain the difference between civil and criminal law.",
        "Give general legal guidance (not legal advice).",
        "Explain how contracts work.",
        "What are common legal mistakes to avoid?",
        "Explain this law in a practical way.",
        "What questions should someone ask a lawyer?"
    ],
    "business": [
        "Give business advice for beginners.",
        "Explain how startups work.",
        "Provide tips for managing a small business.",
        "Explain marketing strategies simply.",
        "How can a business improve productivity?",
        "Explain business risks and opportunities.",
        "Give tips for customer retention.",
        "Explain basic accounting concepts.",
        "How can a business grow sustainably?",
        "Explain entrepreneurship fundamentals."
    ],
    "psychology": [
        "Explain this psychological concept simply.",
        "Give advice for managing stress.",
        "Explain common emotional responses.",
        "How can someone improve mental well-being?",
        "Explain behavioral patterns.",
        "Provide coping strategies for anxiety.",
        "Explain motivation and habits.",
        "Give tips for emotional regulation.",
        "Explain communication psychology.",
        "How does mindset affect behavior?"
    ],
    "science": [
        "Explain this scientific concept simply.",
        "Describe how this natural phenomenon works.",
        "Explain this experiment or discovery.",
        "Summarize this scientific theory.",
        "Explain cause and effect scientifically.",
        "Describe real-world applications of this science.",
        "Explain scientific terms in plain language.",
        "How does this process occur in nature?",
        "Explain recent scientific advancements.",
        "Simplify this complex scientific idea."
    ],
    "general": [
        "Answer the user's question clearly and simply.",
        "Explain this topic in an easy-to-understand way.",
        "Give a concise and accurate explanation.",
        "Provide examples to clarify the answer.",
        "Explain this step by step.",
        "Give practical advice related to this question.",
        "Summarize the main points clearly.",
        "Provide a beginner-friendly explanation.",
        "Explain pros and cons.",
        "Answer in a conversational tone."
    ]
}

# ================= KEYWORDS MAP =================
KEYWORDS_MAP = {
    "medical": ["doctor","physician","nurse","hospital","clinic","health","medical","medicine","disease","symptom","pain","treatment","patient","surgery","infection","virus","fever","headache","cough","diagnosis"],
    "technology": ["technology","tech","computer","programming","software","hardware","ai","algorithm","network","internet","cloud","robot","robotics","iot","app","coding"],
    "finance": ["finance","money","investment","stock","budget","saving","bank","loan","tax","cryptocurrency","income","profit","loss","accounting"],
    "education": ["education","learning","study","student","teacher","school","college","university","exam","lesson","course","homework","research"],
    "legal": ["law","legal","lawyer","court","case","contract","rights","crime","penalty","evidence","verdict"],
    "business": ["business","startup","entrepreneur","marketing","management","accounting","productivity","growth","customer"],
    "psychology": ["psychology","mental","stress","behavior","anxiety","emotion","mindset","habits","motivation","coping"],
    "science": ["science","experiment","theory","research","cause","effect","natural","phenomenon","discovery","process"]
}

# ================= GENETIC ALGORITHM PROMPT SELECTION =================
def keyword_frequency(text, keywords):
    text = text.lower()
    return sum(text.count(k) for k in keywords)

def detect_categories_with_weights(text, keywords_map):
    category_weights = {}
    for category, keywords in keywords_map.items():
        score = keyword_frequency(text, keywords)
        if score > 0:
            category_weights[category] = score
    return category_weights

def genetic_prompt_selector(user_text):
    category_weights = detect_categories_with_weights(user_text, KEYWORDS_MAP)
    if not category_weights:
        return {"general": PROMPTS_DB["general"][:3]}
    
    result = {}
    for category, weight in category_weights.items():
        prompts = PROMPTS_DB.get(category, [])
        if not prompts:
            continue
        selection_count = min(len(prompts), max(1, weight))
        selected_prompts = random.sample(prompts, selection_count)
        result[category] = selected_prompts
    return result

def format_prompt_output(genetic_result):
    lines = []
    for category, prompts in genetic_result.items():
        joined = ", ".join(prompts)
        lines.append(f"{category.upper()}:\n{joined}")
    return "\n\n".join(lines)

# ================= CONFIG =================
os.environ["OPENAI_API_KEY"] = "puy Your API key here"
client = OpenAI()

VOSK_MODELS = {
    "English": "vosk-model-small-en-us-0.15",
    "Arabic": "vosk-model-ar-mgb2-0.4"
}

SPEECH_LANG = "English"
MODE = "answer"
TARGET_LANG = "Arabic"

listening = False
speaking = False

audio_queue = queue.Queue()
tts_queue = queue.Queue()

# ================= ARABIC FIX =================
def fix_arabic(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

# ================= SIMPLE SPEAK =================
def SpeakText(command):
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()

# ================= TTS THREAD =================
def tts_worker():
    global speaking, listening
    
    while True:
        text = tts_queue.get()
        if text is None:
            break
        speaking = True
        listening = False
        SpeakText(text)
        speaking = False
        listening = True

threading.Thread(target=tts_worker, daemon=True).start()

# ================= VOSK =================
model = Model(VOSK_MODELS[SPEECH_LANG])
recognizer = KaldiRecognizer(model, 16000)

def reload_vosk(language):
    global model, recognizer, listening
    listening = False
    model = Model(VOSK_MODELS[language])
    recognizer = KaldiRecognizer(model, 16000)

# ================= GPT =================
def ask_gpt(prompt):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"[GPT Error: {e}]"

def process_text(text):
    if MODE == "fact":
        return ask_gpt(f"Fact check this:\n{text}")
    elif MODE == "translate":
        return ask_gpt(f"Translate to {TARGET_LANG}:\n{text}")
    elif MODE == "genetic_algorithm":
        ga_result = genetic_prompt_selector(text)
        return format_prompt_output(ga_result)
    return ask_gpt(text)

# ================= AUDIO =================
def audio_callback(indata, frames, time, status):
    if listening and not speaking:
        audio_queue.put(bytes(indata))

def listen_loop():
    global listening
    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=audio_callback
    ):
        while True:
            if not listening:
                continue
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    handle_text(text)

# ================= PROCESS =================
def handle_text(text):
    global listening
    listening = False
    display_text = fix_arabic(text) if SPEECH_LANG == "Arabic" else text

    chat_box.configure(state="normal")
    chat_box.insert("end", f"You: {display_text}\n")
    chat_box.configure(state="disabled")

    reply = process_text(text)
    display_reply = fix_arabic(reply) if SPEECH_LANG == "Arabic" else reply

    chat_box.configure(state="normal")
    chat_box.insert("end", f"Assistant: {display_reply}\n\n")
    chat_box.configure(state="disabled")
    chat_box.see("end")

    tts_queue.put(reply)

# ================= GUI ACTIONS =================
def start_listening():
    global listening
    listening = True
    status_label.configure(text="Listening...", text_color="green")

def stop_listening():
    global listening
    listening = False
    status_label.configure(text="Stopped", text_color="red")

def change_mode(choice):
    global MODE
    MODE = choice

def change_speech_language(choice):
    global SPEECH_LANG
    SPEECH_LANG = choice
    reload_vosk(choice)

# ================= GUI =================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("760x680")
root.title("Bilingual Offline Voice Assistant")

status_label = ctk.CTkLabel(root, text="Stopped", font=("Arial", 16, "bold"))
status_label.pack(pady=10)

lang_frame = ctk.CTkFrame(root)
lang_frame.pack(pady=5)
ctk.CTkLabel(lang_frame, text="Speech Language:").grid(row=0, column=0)
ctk.CTkOptionMenu(
    lang_frame,
    values=["English", "Arabic"],
    command=change_speech_language
).grid(row=0, column=1)

mode_frame = ctk.CTkFrame(root)
mode_frame.pack(pady=5)
ctk.CTkLabel(mode_frame, text="Mode").grid(row=0, column=0)
ctk.CTkOptionMenu(
    mode_frame,
    values=["answer", "fact", "translate", "genetic_algorithm"],
    command=change_mode
).grid(row=0, column=1)

chat_box = ctk.CTkTextbox(root, width=720, height=360)
chat_box.pack(pady=10)
chat_box.configure(state="disabled")

control_frame = ctk.CTkFrame(root)
control_frame.pack(pady=10)
ctk.CTkButton(control_frame, text="Start", command=start_listening).grid(row=0, column=0, padx=5)
ctk.CTkButton(control_frame, text="Stop", command=stop_listening).grid(row=0, column=1, padx=5)

# Start listening thread
threading.Thread(target=listen_loop, daemon=True).start()
root.mainloop()
