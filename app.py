import streamlit as st
import openai

# 1. Page Setup & Title
st.set_page_config(page_title="Strange Situation Simulator", layout="wide")
st.title("👶 AI Strange Situation Simulator")
st.caption("A developmental psychology tool for observing infant attachment behavior.")

# 2. Sidebar Controls for the Instructor / Operator
st.sidebar.header("⚙️ Simulation Settings")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

attachment_style = st.sidebar.selectbox(
    "Choose Attachment Style:",
    ["SECURE", "INSECURE-AVOIDANT", "INSECURE-RESISTANT", "DISORGANIZED"]
)

# Initialize Session States
if "messages" not in st.session_state:
    st.session_state.messages = []
if "episode" not in st.session_state:
    st.session_state.episode = 1
if "distress" not in st.session_state:
    st.session_state.distress = 20

# System Prompt Generator
SYSTEM_PROMPT = f"""
You are simulating a 14-month-old infant named "Alex" undergoing Mary Ainsworth's Strange Situation.
Attachment Style: {attachment_style}.

Maintain strict 14-month-old behavioral fidelity. Use short phrases or physical actions in asterisks.
Respond ONLY in this exact format:

*Action*: (Describe what Alex physically does)
Distress: [0-100]
Primary Focus: [Toys / Door / Parent / Stranger]
"""

# 3. Main Dashboard Layout (Two Columns)
col_chat, col_data = st.columns([2, 1])

with col_chat:
    st.subheader("💬 Room Interaction")
    
    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Pre-Set Action Buttons for 1st Year Undergrads
    st.write("---")
    st.write("**Quick Researcher Cues:**")
    c1, c2, c3 = st.columns(3)
    
    selected_action = None
    if c1.button("🚪 Parent Leaves Room"):
        selected_action = "*Parent quietly gets up and leaves the room, closing the door.*"
        st.session_state.episode = min(8, st.session_state.episode + 1)
    if c2.button("👋 Parent Returns"):
        selected_action = "*Parent opens the door, enters, and holds out arms saying 'Hi Alex!'*"
        st.session_state.episode = min(8, st.session_state.episode + 1)
    if c3.button("🙋 Stranger Enters"):
        selected_action = "*A friendly stranger enters the room and sits down quietly.*"
        st.session_state.episode = min(8, st.session_state.episode + 1)

    # Custom Text Input
    user_input = st.chat_input("Or type a custom adult action...")
    action_to_send = user_input or selected_action

    # Handle Input & Call OpenAI API
    if action_to_send:
        if not api_key:
            st.error("Please enter an OpenAI API Key in the sidebar to run the simulation!")
        else:
            client = openai.OpenAI(api_key=api_key)
            
            # Add user action
            st.session_state.messages.append({"role": "user", "content": action_to_send})
            with st.chat_message("user"):
                st.write(action_to_send)

            # Call AI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
            )
            ai_reply = response.choices[0].message.content
            
            # Parse Distress Level out of the response string for the meter
            if "Distress:" in ai_reply:
                try:
                    distress_val = int(ai_reply.split("Distress:")[1].split("\n")[0].strip().replace("%",""))
                    st.session_state.distress = distress_val
                except:
                    pass

            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            st.rerun()

# 4. Live Data & Metrics Panel
with col_data:
    st.subheader("📊 Observational Telemetry")
    
    # Progress Tracker for Ainsworth's 8 Episodes
    st.write(f"**Current Stage:** Episode {st.session_state.episode} / 8")
    st.progress(st.session_state.episode / 8)
    
    st.write("---")
    
    # Visual Stress Level
    st.write("**Infant Distress Level:**")
    st.progress(st.session_state.distress / 100)
    st.metric("Distress Level", f"{st.session_state.distress}%")
    
    st.info("💡 **Instructor Note:** Watch for discrepancies between external behavior in the chat and internal distress meters!")