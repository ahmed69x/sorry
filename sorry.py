# streamlit_app.py
import streamlit as st
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
import csv

# ---------------- CONFIG / SECRETS UTIL ----------------
def get_secret(key, fallback=None):
    try:
        return st.secrets["email"].get(key)
    except Exception:
        return os.environ.get(key.upper(), fallback)

SMTP_SERVER = get_secret("smtp_server", "smtp.gmail.com")
SMTP_PORT = int(get_secret("smtp_port", 587))
SMTP_USER = get_secret("smtp_user", "")
SMTP_PASS = get_secret("smtp_pass", "")

# Emails you provided
OWNER_EMAIL = "ahmed.hasssan766@gmail.com"
GF_EMAIL = "fifi.ali.abdullah@gmail.com"

# Credentials
_USERNAME = "aq"
GF_USERNAME = "ah"
OWNER_PASSWORD = "ayeshiqt"
GF_PASSWORD = "ayeshiq"

LOG_FILE = "annoy_log.csv"

# ---------------- UTILITIES ----------------
def send_email(subject, body, to_email, cc_email=None):
    """
    Sends an email using configured SMTP settings (if provided).
    Returns (success:bool, message:str).
    """
    if not SMTP_USER or not SMTP_PASS:
        return False, "SMTP not configured"
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    if cc_email:
        msg["Cc"] = cc_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as smtp:
            smtp.ehlo()
            if SMTP_PORT in (587, 25):
                smtp.starttls()
                smtp.ehlo()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
        return True, "Email sent"
    except Exception as e:
        return False, str(e)

def append_log(row):
    """
    Append a row to the CSV log. Expected row layout:
    [timestamp_utc, who_pressed, note, improvement]
    """
    write_header = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["timestamp_utc", "who_pressed", "note", "improvement"])
        writer.writerow(row)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="I’m Sorry ❤️", layout="wide", initial_sidebar_state="collapsed")

# ---------------- STYLE (including big red button) ----------------
st.markdown("""
<style>
/* Background + font */
body, .main {
    background: linear-gradient(135deg, #fdf2f8, #fde2e4);
    color: #4a4a4a;
    font-family: "Poppins", sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* Slide card */
.slide {
    background-color: white;
    border-radius: 18px;
    padding: 3rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    text-align: center;
    max-width: 980px;
    margin: 3rem auto;
    min-height: 72vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* Titles */
.slide h1 {
    color: #d63384;
    margin-bottom: 0.6rem;
}

/* Paragraph */
.slide p {
    font-size: 1.15rem;
    line-height: 1.7;
    color: #333;
    margin-top: 0.8rem;
}

/* Default button style (small navigation) */
.small-nav .stButton>button {
    background-color: #ffd6e8 !important;
    color: #d63384 !important;
    font-weight: 600;
    border-radius: 10px !important;
    padding: 8px 16px !important;
    box-shadow: none !important;
}

/* Big red stop button - this targets the final button container below */
.big-red-container .stButton>button {
    background: linear-gradient(180deg, #ff5c5c, #e53935) !important;
    color: white !important;
    font-size: 20px !important;
    padding: 18px 28px !important;
    border-radius: 14px !important;
    box-shadow: 0 14px 30px rgba(229,57,53,0.24) !important;
    border: none !important;
    transform: translateZ(0);
    transition: transform 0.12s ease-in-out, box-shadow 0.12s ease-in-out;
}

/* Big red pulse animation */
.big-red-container .stButton>button:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 22px 40px rgba(229,57,53,0.28) !important;
}

/* Extra visual pulse using pseudo-element via wrapper */
.big-red-pulse {
    display:inline-block;
    border-radius: 18px;
    padding: 6px;
    animation: pulse 2.2s infinite;
}
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(229,57,53,0.18); }
  70% { box-shadow: 0 0 0 18px rgba(229,57,53,0.00); }
  100% { box-shadow: 0 0 0 0 rgba(229,57,53,0.00); }
}

/* Footer small */
footer { text-align:center; color: gray; margin-top: 2rem; font-size:0.9rem; }

/* Responsive adjustments */
@media (max-width: 600px) {
  .slide { padding: 2rem; margin: 1.5rem auto; min-height: 64vh; }
  .big-red-container .stButton>button { width: 100% !important; }
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE DEFAULTS ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "slide_index" not in st.session_state:
    st.session_state.slide_index = 0
if "owner_email" not in st.session_state:
    st.session_state.owner_email = OWNER_EMAIL
if "gf_email" not in st.session_state:
    st.session_state.gf_email = GF_EMAIL

# ---------------- AUTH ----------------
def do_login(username, password):
    if username == GF_USERNAME and password == GF_PASSWORD:
        st.session_state.logged_in = True
        st.session_state.user = GF_USERNAME
        return True
    if username == OWNER_USERNAME and password == OWNER_PASSWORD:
        st.session_state.logged_in = True
        st.session_state.user = OWNER_USERNAME
        return True
    return False

if not st.session_state.logged_in:
    st.title("Hi Ayeshi Please log in")
    st.write("A place you can come to if i'm about to be annoying")
    with st.form("login_form"):
        username = st.selectbox("Login as", options=[OWNER_USERNAME, GF_USERNAME])
        pwd = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Enter ❤️")
    if submitted:
        if do_login(username, pwd):
            st.rerun()
        else:
            st.error("Wrong username or password 💔")
    st.stop()

# ---------------- SIDEBAR (minimal) ----------------
st.sidebar.title("Signed in as")
st.sidebar.write(f"**{st.session_state.user}**")

# ---------------- SLIDES CONTENT ----------------
slides = [
    {
        "title": "I'm really sorry :( ❤️",
        "text": (
            "I know I’ve annoyed you, and I’m truly sorry. I should have listened better, cared more deeply, and respected your peace. I have been thinking about how my words and actions affect you, "
            "and not affecting you negatively is my responsibility. Please let me make it right."
        )
    },
    {
        "title": "You matter to me",
        "text": (
            "You matter more than anything to me and a lot more than my problems be it the defensiveness or bad habits and i do want to grow better for you. Your feelings are valid. I understand i upset you and i did learn from it."
        )
    },
    {
        "title": "I will stop and listen",
        "text": (
            "If I'm ever annoying you again, please press the big red stop button. I promise I'll stop, listen, and change my behavior."
        )
    },
    {
        "title": "I appreciate you",
        "text": (
            "I appreciate everything you do for me and us and the hope, courage and patience you give me. I will try to be understanding, kinder and more thoughtful every day."
        )
    },
    {
        "title": "Can we try again?",
        "text": (
            "If you feel ready, I'd love a chance to talk, listen properly, and work this out together."
        )
    },
]

# Ensure index bounds
if st.session_state.slide_index < 0:
    st.session_state.slide_index = 0
if st.session_state.slide_index > len(slides) - 1:
    st.session_state.slide_index = len(slides) - 1

# ---------------- MAIN SLIDE RENDER ----------------
slide = slides[st.session_state.slide_index]
st.markdown(f"""
<div class="slide">
  <h1>{slide['title']}</h1>
  <p>{slide['text']}</p>
</div>
""", unsafe_allow_html=True)

# Navigation controls (kept visually smaller)
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    # Wrap in a container with a class name to narrow CSS targeting (small nav)
    st.markdown('<div class="small-nav">', unsafe_allow_html=True)
    if st.session_state.slide_index > 0:
        if st.button("💖 Prev"):
            st.session_state.slide_index -= 1
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="small-nav">', unsafe_allow_html=True)
    if st.session_state.slide_index < len(slides) - 1:
        if st.button("💞 Next"):
            st.session_state.slide_index += 1
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- FINAL SLIDE ACTION (Big Red Button + feedback box) ----------------
# Show these controls only on the last slide (index == last)
if st.session_state.slide_index == len(slides) - 1:
    # SHOW FOR BOTH GF and OWNER so button/boxes are always visible (fixes missing button issue)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### If I’m annoying you right now — press this 👇")
    st.info("Pressing this will send a notification and help me learn what to improve.")

    # Optional short note
    note = st.text_area("Optional short note (e.g.'dirty ass', 'stop being dumb', 'too loud', 'stop memes')", max_chars=250, key="note_text")

    # Optional 'what can I do better' field
    improvement = st.text_area("What can I do better? (optional (helps me learn)", max_chars=800, key="improve_text")

    # Show a visually large red button using CSS wrapper class 'big-red-container'
    st.markdown('<div class="big-red-pulse" style="display:flex; justify-content:center; margin-top:14px;">', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="big-red-container">', unsafe_allow_html=True)
        # Functional button (this is the real, clickable button)
        if st.button("🔴 I’m annoyed — Stop now", key="stop_btn", help="Owner will be notified immediately.", use_container_width=True):
            ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            # who pressed is the username (aq or ah)
            who_pressed = st.session_state.user or "unknown"
            # save both note and improvement to CSV
            append_log([ts, who_pressed, note or "", improvement or ""])
            # prepare and send email
            owner_email_target = st.session_state.owner_email or OWNER_EMAIL
            gf_email_target = st.session_state.gf_email or GF_EMAIL
            subject = "Apology App: 'I'm annoyed' button pressed"
            body = (
                f"Hello,\n\nThis is an automated notification from the Apology App.\n\n"
                f"User '{who_pressed}' pressed the 'I'm annoyed' button at (UTC): {ts}\n\n"
                f"Short note: {note or 'None'}\n\n"
                f"What they suggest I can do better: {improvement or 'None'}\n\n"
                f"Please stop and check in with them.\n\n— The Apology App"
            )
            success, msg = send_email(subject, body, to_email=owner_email_target, cc_email=gf_email_target)
            if success:
                st.success("Ahmed has been notified and apologies for him being dumb sometimes. Thank you.")
            else:
                # keep behavior clear: log happens regardless; email may need SMTP
                st.error(f"Could not send email: {msg}  (Email requires SMTP configuration.)")
            st.balloons()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # If owner, also show logs panel under the button (so they can inspect)
    if st.session_state.user == OWNER_USERNAME:
        st.info("Recent logs (most recent first):")
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    rows = list(csv.reader(f))
                if len(rows) > 1:
                    header, *data = rows
                    data = data[::-1]  # most recent first
                    st.table([header] + data[:20])
                else:
                    st.write("No logs yet.")
            except Exception as e:
                st.write("Could not read log file:", e)

# ---------------- FOOTER ----------------
st.markdown("<footer>Made for AQ by AH</footer>", unsafe_allow_html=True)

# ---------------- LOGOUT ----------------
if st.button("🚪 Log out"):
    for k in ["logged_in", "user", "slide_index"]:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()



