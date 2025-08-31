from flask import Flask
import os
import subprocess

app = Flask(__name__)

# File to track bot PID, avoid duplicate start
BOT_PID_FILE = "/tmp/bot.pid"

@app.route("/")
def home():
    # Agar bot already running hai, to firse start mat karo
    if os.path.exists(BOT_PID_FILE):
        return "Bot already running ✅"

    try:
        # Start bot in background (Extractor/__main__.py)
        p = subprocess.Popen(["python", "-m", "Extractor"])

        # PID file me write karo
        with open(BOT_PID_FILE, "w") as f:
            f.write(str(p.pid))

        return "Bot started ✅"
    except Exception as e:
        print("Bot failed to start:", e)
        return f"Bot failed to start ❌\nError: {e}"

if __name__ == "__main__":
    # Render automatically PORT assign karta hai
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
