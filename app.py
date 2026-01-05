import streamlit as st

# ================= CONFIG =================
st.set_page_config(page_title="Sudan Crisis Chatbot", layout="wide")
st.markdown(
    """
    <style>
    .stApp {
        background-color: black;
        color: red;
    }
    .stTextInput>div>div>input {
        color: red;
        background-color: black;
    }
    .stButton>button {
        background-color: red;
        color: black;
        border: 2px solid black;
    }
    </style>
    """, unsafe_allow_html=True
)

# ================= INTENTS & RESPONSES =================
intents = {
    "independence": ["sudan azad kaise hua", "1956", "anglo egyptian", "egypt monarchy 1952", "sudanization 1953", "1 january 1956", "azad kb hua"],
    "divide": ["sudan break", "tootna", "north south divide", "culture religion", "north muslim", "south christian", "discrimination"],
    "first_civil_war": ["first civil war", "pehli jang", "1955 1972", "anya nya", "rebellion"],
    "force_rule": ["force rule", "zulm", "military control", "culture thopi", "promises toda"],
    "sharia_law": ["sharia law", "september laws", "nimeiri", "1983 sharia"],
    "second_civil_war": ["second civil war", "doosri jang", "1983 2005", "john garang", "spla"],
    "addis_ababa": ["addis ababa", "1972 agreement", "south autonomy"],
    "south_sudan_independence": ["south sudan azad", "2011 independence"],
    "rsf": ["rsf", "rapid support forces", "janjaweed"],
    "current": ["current", "abhi", "rsf saf war", "famine", "genocide"]
}

responses = {
    "independence": {"english":"Sudan gained independence on 1 January 1956 from Anglo-Egyptian control without a major war.",
                     "roman":"Sudan 1 January 1956 ko Anglo-Egyptian control se azad hua bina bari jang ke.",
                     "urdu":"سوڈان یکم جنوری 1956 کو اینگلو-مصری کنٹرول سے آزاد ہوا۔"},
    "divide": {"english":"Sudan divided due to cultural and religious differences between North and South.",
               "roman":"Sudan North aur South ke culture aur religion ke farq ki wajah se divide hua.",
               "urdu":"سوڈان شمال اور جنوب کے ثقافتی و مذہبی اختلافات کی وجہ سے تقسیم ہوا۔"},
    "first_civil_war":{"english":"First Civil War (1955-1972) started due to fear of Northern domination.",
                       "roman":"Pehli civil war 1955-1972 North ke domination ke khauf ki wajah se hui.",
                       "urdu":"پہلی خانہ جنگی 1955-1972 شمالی غلبے کے خوف سے شروع ہوئی۔"},
    "force_rule":{"english":"South Sudan felt forced rule due to lack of political power and military control.",
                  "roman":"South ne force rule mehsoos ki kyun ke political power nahi thi aur military control tha.",
                  "urdu":"جنوبی سوڈان کو زبردستی حکمرانی کا سامنا کرنا پڑا۔"},
    "sharia_law":{"english":"Sharia Law was imposed in 1983 by Nimeiri, escalating conflict.",
                  "roman":"1983 mein Nimeiri ne Sharia Law lagaya jis se jang barh gayi.",
                  "urdu":"1983 میں نمیری نے شریعت نافذ کی جس سے تنازعہ بڑھا۔"},
    "second_civil_war":{"english":"Second Civil War (1983-2005) was led by SPLA under John Garang.",
                        "roman":"Doosri civil war 1983-2005 John Garang aur SPLA ne lead ki.",
                        "urdu":"دوسری خانہ جنگی 1983-2005 جان گارانگ کی قیادت میں ہوئی۔"},
    "addis_ababa":{"english":"Addis Ababa Agreement (1972) ended the first civil war.",
                    "roman":"Addis Ababa Agreement 1972 ne pehli jang khatam ki.",
                    "urdu":"ایڈس ابابا معاہدہ 1972 نے پہلی جنگ ختم کی۔"},
    "south_sudan_independence":{"english":"South Sudan became independent on 9 July 2011.",
                                "roman":"South Sudan 9 July 2011 ko azad hua.",
                                "urdu":"جنوبی سوڈان 9 جولائی 2011 کو آزاد ہوا۔"},
    "rsf":{"english":"RSF was formed in 2013 from Janjaweed militias.",
           "roman":"RSF 2013 mein Janjaweed se bani.",
           "urdu":"آر ایس ایف 2013 میں جنجوید سے بنی۔"},
    "current":{"english":"Sudan is facing RSF vs SAF conflict since 2023.",
             "roman":"Sudan 2023 se RSF aur SAF ki jang ka shikar hai.",
             "urdu":"سوڈان 2023 سے آر ایس ایف اور ایس اے ایف کی جنگ کا شکار ہے۔"}
}

used_answers = set()

# ================= LANGUAGE DETECTION =================
def detect_lang(text):
    if any('\u0600' <= c <= '\u06FF' for c in text):
        return "urdu"
    if text.lower() == text:
        return "roman"
    return "english"

# ================= CHAT FUNCTION =================
def get_answer(user_q, user_name="Rafay"):
    q = user_q.lower()
    lang = detect_lang(user_q)
    for intent, keys in intents.items():
        if any(k in q for k in keys):
            ans = responses[intent][lang]
            if ans in used_answers:
                ans = "Sorry, I’m under training."
            else:
                used_answers.add(ans)
            return f"{user_name}: {user_q}", f"Bot: {ans}"
    return f"{user_name}: {user_q}", "Bot: Sorry, I’m under training."

# ================= SESSION =================
if "history" not in st.session_state:
    st.session_state.history = []

# ================= UI =================
st.title("🌍 Sudan Crisis Chatbot")
st.markdown("Developed by Rafay Boss")

# Suggested questions
st.markdown("**Suggested Questions:**")
cols = st.columns(3)
suggestions = [v[0] for v in intents.values()]
for i, q in enumerate(suggestions):
    if cols[i % 3].button(q):
        user_msg, bot_msg = get_answer(q)
        st.session_state.history.append((user_msg, bot_msg))

# User input
user_input = st.text_input("Ask in English / Roman Urdu / اردو")
if user_input:
    user_msg, bot_msg = get_answer(user_input)
    st.session_state.history.append((user_msg, bot_msg))

# Display chat
for u, b in st.session_state.history:
    st.markdown(f"**{u}**")
    st.markdown(f"{b}")
