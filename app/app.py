import streamlit as st
from medical_record_generator import generate_record
from speech_to_text import get_voice
from database import save_record, get_all_records, search_by_name, get_stats
from emotion_detection import detect_emotion

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(page_title="AI Medical System", layout="centered")

st.title("🩺 AI Patient Medical Record System")

# ---------------- DASHBOARD ---------------- #
st.subheader("📊 Dashboard")
stats = get_stats()
st.metric("Total Records", stats["total_records"])

# ---------------- INPUT ---------------- #
st.subheader("📝 Enter Patient Details")

patient_name = st.text_input("Enter Patient Name")

# session state for conversation
if "conversation" not in st.session_state:
    st.session_state.conversation = ""

if st.button("🎤 Use Voice Input"):
    st.session_state.conversation = get_voice()

conversation = st.text_area(
    "Enter Doctor-Patient Conversation",
    value=st.session_state.conversation
)

actions_input = st.text_input("Observed Actions (comma separated)")
actions = [a.strip() for a in actions_input.split(",") if a.strip()]

# ---------------- CAMERA ---------------- #
st.subheader("📷 Camera Input")

img_file = st.camera_input("Take a picture")

if img_file:
    st.image(img_file, caption="Captured Image", width=300)

# ---------------- EMOTION DETECTION ---------------- #
st.subheader("🧠 AI Emotion Detection")

if "emotion" not in st.session_state:
    st.session_state.emotion = "Not detected"

if st.button("Start Emotion Detection"):
    emotion = detect_emotion()
    st.session_state.emotion = emotion

st.write("Detected Emotion:", st.session_state.emotion)

# ---------------- GENERATE ---------------- #
if "record" not in st.session_state:
    st.session_state.record = None

if st.button("Generate Medical Record"):

    if not conversation:
        st.warning("Please enter conversation")
    else:
        record = generate_record(conversation, patient_name, actions)

        # Add emotion insight
        emotion_note = ""
        if st.session_state.emotion in ["sad", "angry"]:
            emotion_note = "Patient appears uncomfortable"
        elif st.session_state.emotion == "happy":
            emotion_note = "Patient appears stable"
        else:
            emotion_note = "No visible distress"

        record["Emotion"] = st.session_state.emotion
        record["Emotion Insight"] = emotion_note

        st.session_state.record = record

# ---------------- DISPLAY RECORD ---------------- #
if st.session_state.record:

    record = st.session_state.record

    st.subheader("📋 Generated Medical Record")

    st.write("👤 Patient Name:", record["Patient Name"])
    st.write("🩺 Symptoms:", ", ".join(record["Symptoms"]))
    st.write("⏱ Duration:", record["Duration"])
    st.write("💓 Vitals:", ", ".join(record["Vitals"]))
    st.write("👁 Observed Actions:", ", ".join(record["Observed Actions"]))
    st.write("😊 Emotion:", record["Emotion"])
    st.write("🧠 Emotion Insight:", record["Emotion Insight"])
    st.write("🧾 Diagnosis:", record["Diagnosis"])
    st.write("📝 Notes:", record["Notes"])

    # Save button
    if st.button("💾 Save Record"):
        save_record(record)
        st.success("✅ Record saved to database!")

# ---------------- HISTORY ---------------- #
st.subheader("📂 Patient History")

if st.button("Show All Records"):
    records = get_all_records()

    if records:
        for r in records:
            st.write("----")
            st.write("👤", r.get("Patient Name"))
            st.write("🩺", ", ".join(r.get("Symptoms", [])))
            st.write("😊", r.get("Emotion"))
            st.write("🧾", r.get("Diagnosis"))
    else:
        st.info("No records found")

# ---------------- SEARCH ---------------- #
st.subheader("🔍 Search Patient")

search_name = st.text_input("Enter Patient Name to Search")

if st.button("Search"):
    results = search_by_name(search_name)

    if results:
        for r in results:
            st.write("----")
            st.write("👤", r.get("Patient Name"))
            st.write("🩺", ", ".join(r.get("Symptoms", [])))
            st.write("😊", r.get("Emotion"))
            st.write("🧾", r.get("Diagnosis"))
    else:
        st.warning("No matching patient found")