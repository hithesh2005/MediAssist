import hashlib
import io
import json
import re
import time
import unicodedata
import uuid
import wave
from datetime import datetime
from urllib.parse import quote_plus
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import speech_recognition as sr
import mediassist as core
st.set_page_config(
    page_title="MediAssist",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="auto",
)
LANGUAGES = {
    "English": ("en", "en-IN"),
    "తెలుగు": ("te", "te-IN"),
    "हिन्दी": ("hi", "hi-IN"),
}
UI_TRANSLATIONS = {
    "te": {
        "AI-powered preliminary health assistance": "AI ఆధారిత ప్రాథమిక ఆరోగ్య సహాయం",
        "Chat language": "చాట్ భాష", "Speak assistant replies": "అసిస్టెంట్ సమాధానాలను వినండి",
        "Voice replies use your browser's available speech voice.": "వాయిస్ సమాధానాలు మీ బ్రౌజర్‌లో అందుబాటులో ఉన్న వాయిస్‌ను ఉపయోగిస్తాయి.",
        "＋ New chat": "＋ కొత్త చాట్", "About this model": "ఈ మోడల్ గురించి",
        "773 disease classes": "773 వ్యాధి వర్గాలు", "Model scores are not clinical probabilities.": "మోడల్ స్కోర్లు వైద్య నిర్ధారణ సంభావ్యతలు కావు.",
        "For emergencies, contact local emergency services or go to the nearest emergency department.": "అత్యవసర పరిస్థితుల్లో స్థానిక అత్యవసర సేవలను సంప్రదించండి లేదా సమీప అత్యవసర విభాగానికి వెళ్లండి.",
        "A conversational, multilingual health-assessment assistant": "బహుభాషా సంభాషణాత్మక ఆరోగ్య అంచనా సహాయకుడు",
        "MediAssist provides preliminary educational information only. It is not a doctor, does not provide a confirmed diagnosis, and does not prescribe treatment. Do not delay urgent care to use this chatbot.": "MediAssist ప్రాథమిక విద్యాపరమైన సమాచారాన్ని మాత్రమే అందిస్తుంది. ఇది వైద్యుడు కాదు; నిర్ధారిత రోగ నిర్ధారణ లేదా చికిత్సను అందించదు. అత్యవసర వైద్య సహాయాన్ని ఆలస్యం చేయవద్దు.",
        "Message MediAssist...": "MediAssist కు సందేశం పంపండి...", "Send": "పంపండి",
        "Sorry, I couldn't understand. Please try speaking again.": "క్షమించండి, మీ మాటలు అర్థం కాలేదు. దయచేసి మళ్లీ మాట్లాడండి.",
        "Speech recognition is unavailable. Check your internet connection.": "వాయిస్ గుర్తింపు అందుబాటులో లేదు. మీ ఇంటర్నెట్ కనెక్షన్‌ను తనిఖీ చేయండి.",
        "Your next step: connect with a healthcare professional": "తదుపరి చర్య: ఆరోగ్య నిపుణుడిని సంప్రదించండి",
        "Find care near you": "మీకు సమీపంలో వైద్య సేవలను కనుగొనండి",
        "Use your current device location or enter an area manually. Your browser will ask for location permission.": "మీ పరికరం ప్రస్తుత స్థానాన్ని ఉపయోగించండి లేదా ప్రాంతాన్ని నమోదు చేయండి. మీ బ్రౌజర్ స్థాన అనుమతిని అడుగుతుంది.",
        "Enter your city, area, or PIN code": "మీ నగరం, ప్రాంతం లేదా పిన్ కోడ్ నమోదు చేయండి",
        "e.g. Hanamkonda, Warangal or 506001": "ఉదా: హనుమకొండ, వరంగల్ లేదా 506001",
        "Your location is used only to create map-search links. It is not saved by this feature.": "మీ స్థానాన్ని మ్యాప్ శోధన లింక్‌ల కోసం మాత్రమే ఉపయోగిస్తాము. ఈ ఫీచర్ దాన్ని సేవ్ చేయదు.",
        "Explore locations on the map": "మ్యాప్‌లో ప్రదేశాలను చూడండి", "🏥 Hospitals": "🏥 ఆసుపత్రులు", "👨‍⚕️ Doctors": "👨‍⚕️ వైద్యులు", "➕ Clinics": "➕ క్లినిక్‌లు",
        "Open hospitals in Google Maps": "Google Maps లో ఆసుపత్రులను తెరవండి", "Open doctors in Google Maps": "Google Maps లో వైద్యులను తెరవండి", "Open clinics in Google Maps": "Google Maps లో క్లినిక్‌లను తెరవండి",
        "Need urgent help?": "తక్షణ సహాయం అవసరమా?",
        "MediAssist does not directly contact doctors, book appointments, or transmit your health information to hospitals.": "MediAssist నేరుగా వైద్యులను సంప్రదించదు, అపాయింట్‌మెంట్ బుక్ చేయదు లేదా మీ ఆరోగ్య సమాచారాన్ని ఆసుపత్రులకు పంపదు.",
    },
    "hi": {
        "AI-powered preliminary health assistance": "AI आधारित प्रारंभिक स्वास्थ्य सहायता",
        "Chat language": "चैट की भाषा", "Speak assistant replies": "सहायक के जवाब बोलकर सुनें",
        "Voice replies use your browser's available speech voice.": "आवाज़ वाले जवाब आपके ब्राउज़र में उपलब्ध आवाज़ का उपयोग करते हैं।",
        "＋ New chat": "＋ नई चैट", "About this model": "इस मॉडल के बारे में",
        "773 disease classes": "773 रोग श्रेणियाँ", "Model scores are not clinical probabilities.": "मॉडल स्कोर चिकित्सकीय संभावनाएँ नहीं हैं।",
        "For emergencies, contact local emergency services or go to the nearest emergency department.": "आपात स्थिति में स्थानीय आपातकालीन सेवाओं से संपर्क करें या नज़दीकी आपातकालीन विभाग जाएँ।",
        "A conversational, multilingual health-assessment assistant": "बहुभाषी संवादात्मक स्वास्थ्य मूल्यांकन सहायक",
        "MediAssist provides preliminary educational information only. It is not a doctor, does not provide a confirmed diagnosis, and does not prescribe treatment. Do not delay urgent care to use this chatbot.": "MediAssist केवल प्रारंभिक शैक्षिक जानकारी देता है। यह डॉक्टर नहीं है, निश्चित निदान या उपचार नहीं देता। आपातकालीन देखभाल में देरी न करें।",
        "Message MediAssist...": "MediAssist को संदेश भेजें...", "Send": "भेजें",
        "Sorry, I couldn't understand. Please try speaking again.": "क्षमा करें, मैं समझ नहीं पाया। कृपया फिर से बोलें।",
        "Speech recognition is unavailable. Check your internet connection.": "वाक् पहचान उपलब्ध नहीं है। अपना इंटरनेट कनेक्शन जाँचें।",
        "Your next step: connect with a healthcare professional": "अगला कदम: स्वास्थ्य विशेषज्ञ से संपर्क करें",
        "Find care near you": "अपने पास चिकित्सा सहायता खोजें",
        "Use your current device location or enter an area manually. Your browser will ask for location permission.": "अपने डिवाइस की वर्तमान लोकेशन का उपयोग करें या क्षेत्र दर्ज करें। आपका ब्राउज़र लोकेशन की अनुमति माँगेगा।",
        "Enter your city, area, or PIN code": "अपना शहर, क्षेत्र या पिन कोड दर्ज करें",
        "e.g. Hanamkonda, Warangal or 506001": "उदाहरण: हनमकोंडा, वारंगल या 506001",
        "Your location is used only to create map-search links. It is not saved by this feature.": "आपकी लोकेशन केवल मैप खोज लिंक बनाने के लिए उपयोग होती है। इसे इस सुविधा द्वारा सहेजा नहीं जाता।",
        "Explore locations on the map": "मैप पर स्थान देखें", "🏥 Hospitals": "🏥 अस्पताल", "👨‍⚕️ Doctors": "👨‍⚕️ डॉक्टर", "➕ Clinics": "➕ क्लिनिक",
        "Open hospitals in Google Maps": "Google Maps में अस्पताल खोलें", "Open doctors in Google Maps": "Google Maps में डॉक्टर खोलें", "Open clinics in Google Maps": "Google Maps में क्लिनिक खोलें",
        "Need urgent help?": "क्या आपको तुरंत मदद चाहिए?",
        "MediAssist does not directly contact doctors, book appointments, or transmit your health information to hospitals.": "MediAssist सीधे डॉक्टरों से संपर्क नहीं करता, अपॉइंटमेंट बुक नहीं करता और आपकी स्वास्थ्य जानकारी अस्पतालों को नहीं भेजता।",
    }
}
# ---------------------------------------------------------------
# Multilingual helpers: voice/status strings, cached translation,
# offline symptom glossary, Unicode-safe yes/no and severity parsing.
# ---------------------------------------------------------------
VOICE_TEXT = {
    "en": {
        "lang_label": "Language / భాష / भाषा",
        "mic_hint": "🎙️ Tap the mic, speak, then tap stop. Your words are sent automatically.",
        "mic_processing": "⏳ Processing your voice…",
        "mic_ok": "✅ Heard: “{text}”",
        "mic_empty": "No speech was recorded. Move closer to the microphone and try again.",
        "mic_error": "Voice input failed: {err}. You can type your message instead.",
        "translation_fallback": "I couldn't translate your message online, so I used a basic built-in word list. Results may be less accurate.",
        "translation_failed": "I couldn't translate your message online (check your internet connection). Please try again or type in English.",
        "followup": "Follow-up",
    },
    "te": {
        "lang_label": "Language / భాష / भाषा",
        "mic_hint": "🎙️ మైక్ నొక్కి మాట్లాడి, ఆపు నొక్కండి. మీ మాటలు ఆటోమేటిక్‌గా పంపబడతాయి.",
        "mic_processing": "⏳ మీ వాయిస్‌ను ప్రాసెస్ చేస్తోంది…",
        "mic_ok": "✅ విన్నది: “{text}”",
        "mic_empty": "ఏ మాటా రికార్డ్ కాలేదు. మైక్ దగ్గరగా ఉంచి మళ్లీ ప్రయత్నించండి.",
        "mic_error": "వాయిస్ ఇన్‌పుట్ విఫలమైంది: {err}. బదులుగా మీ సందేశాన్ని టైప్ చేయండి.",
        "translation_fallback": "మీ సందేశాన్ని ఆన్‌లైన్‌లో అనువదించలేకపోయాను, కాబట్టి ప్రాథమిక పదజాబితాను ఉపయోగించాను. ఫలితాలు తక్కువ ఖచ్చితంగా ఉండవచ్చు.",
        "translation_failed": "మీ సందేశాన్ని ఆన్‌లైన్‌లో అనువదించలేకపోయాను (ఇంటర్నెట్ కనెక్షన్ తనిఖీ చేయండి). మళ్లీ ప్రయత్నించండి లేదా ఇంగ్లీష్‌లో టైప్ చేయండి.",
        "followup": "తదుపరి ప్రశ్న",
    },
    "hi": {
        "lang_label": "Language / భాష / भाषा",
        "mic_hint": "🎙️ माइक दबाएँ, बोलें, फिर रोकें दबाएँ। आपकी बात अपने-आप भेज दी जाएगी।",
        "mic_processing": "⏳ आपकी आवाज़ प्रोसेस हो रही है…",
        "mic_ok": "✅ सुना: “{text}”",
        "mic_empty": "कोई आवाज़ रिकॉर्ड नहीं हुई। माइक के पास बोलकर दोबारा कोशिश करें।",
        "mic_error": "वॉइस इनपुट विफल रहा: {err}। आप अपना संदेश टाइप कर सकते हैं।",
        "translation_fallback": "मैं आपका संदेश ऑनलाइन अनुवाद नहीं कर सका, इसलिए बुनियादी शब्द-सूची का उपयोग किया। परिणाम कम सटीक हो सकते हैं।",
        "translation_failed": "मैं आपका संदेश ऑनलाइन अनुवाद नहीं कर सका (इंटरनेट कनेक्शन जाँचें)। कृपया दोबारा कोशिश करें या अंग्रेज़ी में लिखें।",
        "followup": "अगला प्रश्न",
    },
}

# Texts used by the browser (speech buttons, microphone notices).
BROWSER_TEXT = {
    "en": {
        "listen": "🔊 Listen", "replay": "↻ Replay", "stop": "⏹ Stop",
        "speaking": "Speaking…",
        "tap": "Tap 🔊 to listen.",
        "blocked": "Your browser blocked automatic playback. Tap 🔊 to listen.",
        "novoice": "No English voice is available on this device. Install one in your device's Text-to-speech settings. Until then, please read the reply.",
        "unsupported": "Voice playback isn't supported in this browser. You can still read the reply.",
        "error": "The voice couldn't play. Tap ↻ to try again.",
        "mic_insecure": "The microphone needs a secure (HTTPS) connection. Open MediAssist with https:// or on localhost, or type your message instead.",
        "mic_unsupported": "This browser doesn't support microphone recording. Use the latest Chrome, Edge, Safari or Firefox, or type your message.",
        "mic_denied": "Microphone access is blocked. Allow the microphone in your browser's site settings (lock icon near the address bar), then reload. You can still type your message.",
    },
    "te": {
        "listen": "🔊 వినండి", "replay": "↻ మళ్లీ వినండి", "stop": "⏹ ఆపండి",
        "speaking": "మాట్లాడుతోంది…",
        "tap": "వినడానికి 🔊 నొక్కండి.",
        "blocked": "మీ బ్రౌజర్ ఆటోమేటిక్ ప్లేబ్యాక్‌ను నిరోధించింది. వినడానికి 🔊 నొక్కండి.",
        "novoice": "ఈ పరికరంలో తెలుగు వాయిస్ అందుబాటులో లేదు. పరికర సెట్టింగ్స్‌లోని Text-to-speech విభాగంలో తెలుగు వాయిస్‌ను ఇన్‌స్టాల్ చేయండి. అప్పటివరకు సమాధానాన్ని చదవండి.",
        "unsupported": "ఈ బ్రౌజర్‌లో వాయిస్ ప్లేబ్యాక్ అందుబాటులో లేదు. మీరు సమాధానాన్ని చదవవచ్చు.",
        "error": "వాయిస్ ప్లే కాలేదు. మళ్లీ ప్రయత్నించడానికి ↻ నొక్కండి.",
        "mic_insecure": "మైక్రోఫోన్ పని చేయడానికి సురక్షిత (HTTPS) కనెక్షన్ అవసరం. MediAssist ను https:// లేదా localhost ద్వారా తెరవండి, లేదా మీ సందేశాన్ని టైప్ చేయండి.",
        "mic_unsupported": "ఈ బ్రౌజర్ మైక్రోఫోన్ రికార్డింగ్‌కు మద్దతు ఇవ్వదు. తాజా Chrome, Edge, Safari లేదా Firefox ఉపయోగించండి, లేదా మీ సందేశాన్ని టైప్ చేయండి.",
        "mic_denied": "మైక్రోఫోన్ యాక్సెస్ నిరోధించబడింది. బ్రౌజర్ సైట్ సెట్టింగ్స్‌లో (అడ్రస్ బార్ దగ్గర లాక్ గుర్తు) మైక్రోఫోన్‌ను అనుమతించి, పేజీని రీలోడ్ చేయండి. మీరు సందేశాన్ని టైప్ చేయవచ్చు.",
    },
    "hi": {
        "listen": "🔊 सुनें", "replay": "↻ दोबारा सुनें", "stop": "⏹ रोकें",
        "speaking": "बोल रहा है…",
        "tap": "सुनने के लिए 🔊 दबाएँ।",
        "blocked": "आपके ब्राउज़र ने अपने-आप आवाज़ चलाना रोक दिया। सुनने के लिए 🔊 दबाएँ।",
        "novoice": "इस डिवाइस में हिंदी आवाज़ उपलब्ध नहीं है। डिवाइस सेटिंग्स के Text-to-speech भाग में हिंदी आवाज़ इंस्टॉल करें। तब तक जवाब पढ़ें।",
        "unsupported": "इस ब्राउज़र में आवाज़ प्लेबैक उपलब्ध नहीं है। आप जवाब पढ़ सकते हैं।",
        "error": "आवाज़ नहीं चल सकी। दोबारा कोशिश करने के लिए ↻ दबाएँ।",
        "mic_insecure": "माइक्रोफ़ोन के लिए सुरक्षित (HTTPS) कनेक्शन ज़रूरी है। MediAssist को https:// या localhost से खोलें, या अपना संदेश टाइप करें।",
        "mic_unsupported": "यह ब्राउज़र माइक्रोफ़ोन रिकॉर्डिंग का समर्थन नहीं करता। कृपया नया Chrome, Edge, Safari या Firefox उपयोग करें, या अपना संदेश टाइप करें।",
        "mic_denied": "माइक्रोफ़ोन की अनुमति बंद है। ब्राउज़र की साइट सेटिंग्स (एड्रेस बार के पास लॉक आइकन) में माइक्रोफ़ोन की अनुमति दें और पेज रीलोड करें। आप अपना संदेश टाइप कर सकते हैं।",
    },
}
# English voice-missing text is generic; make it language-specific.
BROWSER_TEXT["en"]["novoice"] = (
    "No English voice is available on this device. Install one in your device's "
    "Text-to-speech settings. Until then, please read the reply."
)


def vt(key, **kwargs):
    """Static (offline) UI text in the selected language."""
    language = st.session_state.get("language", "en")
    table = VOICE_TEXT.get(language, VOICE_TEXT["en"])
    text = table.get(key) or VOICE_TEXT["en"][key]
    return text.format(**kwargs) if kwargs else text


def queue_notice(kind, text):
    """Show a message on the next run (the app reruns right after most actions)."""
    st.session_state.setdefault("notices", []).append((kind, text))


# ---- Translation (cached; failures are never cached) -----------------

@st.cache_data(show_spinner=False, max_entries=4096)
def _google_translate(text: str, target: str) -> str:
    from deep_translator import GoogleTranslator
    result = GoogleTranslator(source="auto", target=target).translate(text)
    if not result or not str(result).strip():
        raise ValueError("Empty translation result")
    return str(result).strip()


def _split_for_translation(value, limit=4000):
    if len(value) <= limit:
        return [value]
    pieces, current = [], ""
    for line in value.split("\n"):
        if current and len(current) + len(line) + 1 > limit:
            pieces.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    if current:
        pieces.append(current)
    return pieces


def translate_safe(text, target):
    """Return (translated_text, ok). Keeps surrounding whitespace; never raises."""
    value = str(text or "")
    core_text = value.strip()
    if not core_text or not re.search(r"[^\W\d_]", core_text):
        return value, True
    lead = value[: len(value) - len(value.lstrip())]
    trail = value[len(value.rstrip()):]
    try:
        pieces = [_google_translate(piece, target) for piece in _split_for_translation(core_text)]
    except Exception:
        st.session_state["translation_failed"] = True
        return value, False
    return lead + "\n".join(pieces) + trail, True


def _curated_translation(paragraph, language):
    """Hand-written translations for follow-up questions and fixed phrases."""
    p = paragraph.strip()
    if not p:
        return None
    known = getattr(core, "QUESTION_TRANSLATIONS", {}).get(language, {}).get(p)
    if known:
        return known
    try:
        if p == core.TEXT["en"]["answer_yes_no"]:
            return core.TEXT[language]["answer_yes_no"]
    except Exception:
        pass
    m = re.fullmatch(r"\*\*Follow-up (\d+) of (\d+)\*\*", p)
    if m:
        label = VOICE_TEXT.get(language, VOICE_TEXT["en"])["followup"]
        return f"**{label} {m.group(1)}/{m.group(2)}**"
    return None


_TOKEN_PATTERN = r"(https?://[^\s)]+|\*\*|\*|`|^#{1,6}\s)"


def _tr_paragraph(paragraph, language):
    curated = _curated_translation(paragraph, language)
    if curated:
        return curated
    try:
        output = []
        for part in re.split(_TOKEN_PATTERN, paragraph):
            if not part:
                continue
            if re.fullmatch(_TOKEN_PATTERN, part):
                output.append(part)
            else:
                output.append(translate_safe(part, language)[0])
        return "".join(output)
    except Exception:
        return paragraph


def tr(text):
    """Translate visible UI text while preserving Markdown and URLs."""
    language = st.session_state.get("language", "en")
    value = str(text)
    if language == "en" or not value.strip():
        return value
    exact = UI_TRANSLATIONS.get(language, {}).get(value)
    if exact:
        return exact
    return "\n\n".join(_tr_paragraph(p, language) for p in value.split("\n\n"))


# ---- Offline symptom glossary (used only if online translation fails) ----

def _fold(text):
    s = unicodedata.normalize("NFC", str(text)).lower()
    return s.replace("\u200c", "").replace("\u200d", "").replace("\u093c", "")


_GLOSSARY_RAW = [
    # Telugu
    ("జ్వరం", "fever"), ("దగ్గు", "cough"), ("తలనొప్పి", "headache"),
    ("జలుబు", "runny nose"), ("గొంతు నొప్పి", "sore throat"), ("గొంతు మంట", "sore throat"),
    ("కడుపు నొప్పి", "abdominal pain"), ("ఛాతి నొప్పి", "chest pain"),
    ("ఛాతీ నొప్పి", "chest pain"), ("గుండె నొప్పి", "chest pain"),
    ("వాంతి", "vomiting"), ("వాంతులు", "vomiting"), ("వికారం", "nausea"),
    ("విరేచనాలు", "diarrhea"), ("అలసట", "fatigue"), ("నీరసం", "weakness"),
    ("ఊపిరి ఆడ", "shortness of breath"), ("శ్వాస తీసుకోవడంలో", "shortness of breath"),
    ("తల తిరు", "dizziness"), ("దురద", "itching"), ("దద్దుర్లు", "skin rash"),
    ("కీళ్ల నొప్పి", "joint pain"), ("కీళ్ళ నొప్పి", "joint pain"),
    ("వెన్నునొప్పి", "back pain"), ("చలి", "chills"),
    ("ముక్కు కారడం", "runny nose"), ("ముక్కు దిబ్బడ", "nasal congestion"),
    ("ముక్కు మూసుకు", "nasal congestion"), ("తుమ్ము", "sneezing"),
    ("ఒళ్ళు నొప్పులు", "body pain"), ("ఒళ్లు నొప్పులు", "body pain"),
    ("ఒంటి నొప్పులు", "body pain"), ("శరీర నొప్పి", "body pain"),
    ("మూత్రంలో మంట", "burning urination"), ("చూపు మసక", "blurred vision"),
    ("ఆకలి లేదు", "loss of appetite"), ("మలబద్ధకం", "constipation"), ("వాపు", "swelling"),
    # Hindi
    ("बुखार", "fever"), ("खांसी", "cough"), ("खाँसी", "cough"),
    ("सिरदर्द", "headache"), ("सर दर्द", "headache"), ("सिर दर्द", "headache"),
    ("जुकाम", "runny nose"), ("सर्दी", "cold"), ("गले में दर्द", "sore throat"),
    ("गले में खराश", "sore throat"), ("गला खराब", "sore throat"),
    ("पेट दर्द", "abdominal pain"), ("पेट में दर्द", "abdominal pain"),
    ("सीने में दर्द", "chest pain"), ("छाती में दर्द", "chest pain"),
    ("उल्टी", "vomiting"), ("मितली", "nausea"), ("जी मिचला", "nausea"),
    ("दस्त", "diarrhea"), ("थकान", "fatigue"), ("कमजोरी", "weakness"),
    ("सांस लेने में", "shortness of breath"), ("साँस लेने में", "shortness of breath"),
    ("सांस फूल", "shortness of breath"), ("साँस फूल", "shortness of breath"),
    ("चक्कर", "dizziness"), ("खुजली", "itching"), ("चकत्ते", "skin rash"),
    ("दाने", "skin rash"), ("जोड़ों में दर्द", "joint pain"), ("जोड़ो में दर्द", "joint pain"),
    ("पीठ दर्द", "back pain"), ("पीठ में दर्द", "back pain"), ("कमर दर्द", "back pain"),
    ("ठंड लग", "chills"), ("कंपकंपी", "chills"), ("नाक बह", "runny nose"),
    ("नाक बंद", "nasal congestion"), ("छींक", "sneezing"), ("बदन दर्द", "body pain"),
    ("शरीर में दर्द", "body pain"), ("पेशाब में जलन", "burning urination"),
    ("धुंधला", "blurred vision"), ("भूख नहीं", "loss of appetite"),
    ("कब्ज", "constipation"), ("सूजन", "swelling"),
    # Romanised Telugu / Hindi
    ("jwaram", "fever"), ("daggu", "cough"), ("thalanoppi", "headache"),
    ("kadupu noppi", "abdominal pain"), ("bukhar", "fever"), ("bukhaar", "fever"),
    ("khansi", "cough"), ("sir dard", "headache"), ("pet dard", "abdominal pain"),
]
GLOSSARY = [(_fold(src), eng) for src, eng in _GLOSSARY_RAW]


def glossary_translate(text):
    folded = _fold(text)
    found = []
    for phrase, english in GLOSSARY:
        if phrase in folded and english not in found:
            found.append(english)
    return found


def model_language_text(text):
    """Convert Telugu/Hindi symptom text to English for the existing English model."""
    language = st.session_state.get("language", "en")
    value = str(text).strip()
    if language == "en" and value.isascii():
        return value
    translated, ok = translate_safe(value, "en")
    if ok and translated.strip():
        return translated.strip()
    terms = glossary_translate(value)
    if terms:
        queue_notice("warning", vt("translation_fallback"))
        ascii_part = re.sub(r"[^\x00-\x7F]+", " ", value)
        return (ascii_part + " " + " ".join(terms)).strip()
    queue_notice("warning", vt("translation_failed"))
    return value


# ---- Yes/no and severity parsing (Unicode-safe) ------------------------

def _tokens(text):
    """Split into words WITHOUT dropping Telugu/Devanagari vowel signs.

    The old regex [^\\w\\s] removed combining marks, so answers such as
    అవును, లేదు, नहीं and हाँ could never match.
    """
    s = _fold(text)
    s = "".join(" " if unicodedata.category(c)[0] in ("P", "S") else c for c in s)
    return s.split()


_YES_WORDS = {_fold(w) for w in [
    "yes", "y", "yeah", "yep", "yup", "sure", "correct", "true", "absolutely", "ok", "okay",
    "అవును", "అవున", "ఔను", "అవునండి", "ఉంది", "ఉన్నది", "ఉన్నాయి", "సరే",
    "हाँ", "हां", "हा", "जी", "है", "सही", "हांजी",
    "avunu", "avunandi", "haan", "haa", "ji",
]}
_NO_WORDS = {_fold(w) for w in [
    "no", "n", "nope", "nah", "false", "never",
    "లేదు", "కాదు", "లేవు", "లేదండి", "కాదండి",
    "नहीं", "नही", "नहि", "ना", "मत",
    "ledu", "kadu", "kaadu", "nahi", "nahin",
]}


def yes_no_value(text):
    """Accept natural short yes/no replies in English, Telugu and Hindi."""
    tokens = _tokens(text)
    if not tokens:
        return None
    if tokens[0] in _YES_WORDS and tokens[0] not in _NO_WORDS:
        return True
    if tokens[0] in _NO_WORDS:
        return False
    if len(tokens) <= 6:
        has_yes = any(t in _YES_WORDS for t in tokens)
        has_no = any(t in _NO_WORDS for t in tokens)
        if has_yes and not has_no:
            return True
        if has_no and not has_yes:
            return False
    return None


_SEVERITY_WORDS = {
    "mild": ["mild", "light", "slight", "తేలిక", "తక్కువ", "हल्का", "हल्की", "कम", "halka"],
    "moderate": ["moderate", "medium", "మధ్యస్థ", "మధ్యమ", "మోస్తరు", "मध्यम", "मोडरेट", "madhyam"],
    "severe": ["severe", "serious", "very bad", "తీవ్ర", "ఎక్కువ", "गंभीर", "ज्यादा", "ज़्यादा", "बहुत तेज",
               "gambhir", "teevra"],
}
_SEVERITY_FOLDED = {k: [_fold(w) for w in v] for k, v in _SEVERITY_WORDS.items()}


def _severity_from_text(text):
    folded = _fold(text)
    hits = [level for level, words in _SEVERITY_FOLDED.items() if any(w in folded for w in words)]
    return hits[0] if len(hits) == 1 else None


def severity_value(text):
    level = _severity_from_text(text)
    if level:
        return level
    if str(text).strip() and not str(text).isascii():
        translated, ok = translate_safe(str(text), "en")
        if ok:
            return _severity_from_text(translated)
    return None

st.markdown("""
<style>
    :root {
        --ma-ink: #f1f5f9; --ma-muted: #b6c2d1; --ma-teal: #2dd4bf;
        --ma-teal-dark: #0f766e; --ma-bg: #0b1220; --ma-card: #172235;
        --ma-border: #334155; --ma-input: #111c2e;
    }
    html, body, [data-testid="stAppViewContainer"], .stApp, [data-testid="stMain"] {
        background: var(--ma-bg) !important; color: var(--ma-ink) !important;
    }
    [data-testid="stHeader"] { background: #0b1220 !important; }
    [data-testid="stSidebar"] { background: #111c2e !important; border-right: 1px solid var(--ma-border); }
    [data-testid="stSidebar"] * { color: var(--ma-ink) !important; }
    .block-container { max-width: 900px; padding-top: 1.5rem; padding-bottom: 6rem; }
    .brand { color: var(--ma-teal) !important; font-size: 2rem; font-weight: 800; letter-spacing: -1px; }
    .subbrand { color: var(--ma-muted) !important; margin-top: -10px; }
    .disclaimer { background: #332b16 !important; border: 1px solid #8b6b27 !important; color: #ffe8a3 !important; padding: 12px 14px; border-radius: 12px; font-size: .92rem; }
    .disclaimer * { color: #ffe8a3 !important; }
    [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li, [data-testid="stText"], .stCaption,
    label, [data-testid="stWidgetLabel"], [data-testid="stCaptionContainer"] p { color: var(--ma-ink) !important; }
    [data-testid="stCaptionContainer"] p { color: var(--ma-muted) !important; }
    [data-testid="stChatMessage"] { background: var(--ma-card) !important; border: 1px solid var(--ma-border) !important; border-radius: 16px !important; color: var(--ma-ink) !important; padding: .8rem 1rem !important; }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] * { color: var(--ma-ink) !important; }
    [data-testid="stChatInput"], [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea, [data-testid="stNumberInput"] input {
        background: var(--ma-input) !important; border: 1px solid #52647c !important;
        border-radius: 12px !important; color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important; caret-color: var(--ma-teal) !important;
    }
    [data-testid="stChatInput"] textarea, [data-testid="stChatInput"] textarea:focus,
    [data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
        color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
        background: var(--ma-input) !important;
    }
    input::placeholder, textarea::placeholder, [data-testid="stChatInput"] textarea::placeholder {
        color: #aab8ca !important; opacity: 1 !important; -webkit-text-fill-color: #aab8ca !important;
    }
    [data-baseweb="select"] > div, [data-baseweb="popover"] [role="option"] { background: #172235 !important; color: #f1f5f9 !important; }
    [data-testid="stChatInput"] button, .stButton > button, [data-testid="stLinkButton"] a {
        background: #0f766e !important; color: #ffffff !important; border: 1px solid #2dd4bf !important; border-radius: 10px !important;
    }
    .stButton > button:hover, [data-testid="stLinkButton"] a:hover { background: #115e59 !important; color: #ffffff !important; }
    [data-testid="stAlert"] { background: #172235 !important; color: #f1f5f9 !important; }
    hr { border-color: var(--ma-border) !important; }
    @media (max-width: 640px) { .block-container { padding: 1rem .8rem 6rem .8rem; } .brand { font-size: 1.65rem; } }
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
    @media (max-width: 768px) {
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] { overflow-x: hidden !important; }
        .block-container { padding: 1rem .75rem 6rem .75rem !important; max-width: 100% !important; }
        [data-testid="stChatMessage"] { padding: .65rem .75rem !important; max-width: 100%; overflow-wrap: anywhere; word-break: break-word; }
        [data-testid="stChatMessage"] pre, [data-testid="stChatMessage"] code { white-space: pre-wrap !important; overflow-x: auto; }
        [data-testid="stChatMessage"] table, [data-testid="stMarkdownContainer"] table { display: block; overflow-x: auto; max-width: 100%; }
        iframe { max-width: 100% !important; }
        input, textarea, [data-baseweb="select"] input { font-size: 16px !important; }
        [data-testid="stTextInput"] input { min-height: 46px; }
        .stButton > button, [data-testid="stFormSubmitButton"] button, [data-testid="stLinkButton"] a { min-height: 46px; }
        [data-testid="stAudioInput"] { width: 100% !important; }
        [data-testid="stSidebar"] { max-width: 88vw !important; }
        [data-testid="stSidebarCollapsedControl"] button, [data-testid="stExpandSidebarButton"],
        [data-testid="stExpandSidebarButton"] button, [data-testid="stSidebarCollapseButton"] button { color: var(--ma-teal) !important; min-width: 44px; min-height: 44px; }
        [data-testid="stSidebarCollapsedControl"] svg, [data-testid="stExpandSidebarButton"] svg { fill: var(--ma-teal) !important; color: var(--ma-teal) !important; }
    }
    .st-key-ma_voice_support { display: none !important; }
</style>
""", unsafe_allow_html=True)
# ---------------------------------------------------------------
# Voice output: one shared speech engine in the browser + a small
# control bar (Listen / Replay / Stop) under every assistant reply.
# ---------------------------------------------------------------
_SPEECH_ENGINE_JS = r'''(function () {
  if (window.__maTTS) { return; }
  var synth = window.speechSynthesis;
  var S = { unlocked: false, epoch: 0, spoken: {}, lang: null, turn: null, chat: null,
            queue: Promise.resolve(), keep: null, activeUi: null };
  window.__maTTS = S;

  var ISO3 = { en: 'eng', te: 'tel', hi: 'hin' };
  var NAMES = { en: /english/i, te: /telugu|తెలుగు/i, hi: /hindi|हिन्दी|हिंदी/i };

  function supported() { return !!(window.speechSynthesis && window.SpeechSynthesisUtterance); }
  function safe(fn, arg) { try { if (fn) { fn(arg); } } catch (e) {} }
  function voicesNow() { try { return synth.getVoices() || []; } catch (e) { return []; } }
  function norm(l) { return String(l || '').replace(/_/g, '-').toLowerCase(); }

  function pickVoice(voices, locale, lang) {
    var want = norm(locale), i3 = ISO3[lang] || lang;
    var exact = null, prefix = null, iso = null, named = null;
    for (var i = 0; i < voices.length; i++) {
      var v = voices[i], vl = norm(v.lang);
      if (vl === want) { if (!exact) { exact = v; } }
      else if (vl === lang || vl.indexOf(lang + '-') === 0) { if (!prefix) { prefix = v; } }
      else if (vl === i3 || vl.indexOf(i3 + '-') === 0) { if (!iso) { iso = v; } }
      else if (NAMES[lang] && NAMES[lang].test(v.name || '')) { if (!named) { named = v; } }
    }
    return exact || prefix || iso || named || null;
  }

  // Android Chrome fills the voice list asynchronously and may never fire
  // "voiceschanged", so wait for the event AND poll (max ~3 s).
  function loadVoices(cb) {
    var done = false, iv = null, tries = 0;
    function onvc() { if (voicesNow().length) { finish(); } }
    function finish() {
      if (done) { return; }
      done = true;
      if (iv) { clearInterval(iv); }
      try { synth.removeEventListener('voiceschanged', onvc); } catch (e) {}
      cb(voicesNow());
    }
    try { synth.addEventListener('voiceschanged', onvc); } catch (e) {}
    iv = setInterval(function () { tries++; if (voicesNow().length || tries >= 20) { finish(); } }, 150);
  }

  // Long utterances get cut off in some Chrome builds, so speak sentence-sized chunks.
  function split(text) {
    var clean = String(text).replace(/\s+/g, ' ').trim();
    var parts = clean.match(/[^.!?।॥]+[.!?।॥]*\s*/g) || [clean];
    var out = [], cur = '';
    for (var i = 0; i < parts.length; i++) {
      if (cur && (cur + parts[i]).length > 170) { out.push(cur.trim()); cur = parts[i]; }
      else { cur += parts[i]; }
    }
    if (cur.trim()) { out.push(cur.trim()); }
    var final = [];
    out.forEach(function (s) {
      if (s.length <= 220) { final.push(s); return; }
      (s.match(/.{1,200}(\s|$)/g) || [s]).forEach(function (x) { if (x.trim()) { final.push(x.trim()); } });
    });
    return final;
  }

  function cancelAll() {
    S.epoch++;
    try { synth.cancel(); } catch (e) {}
    S.queue = Promise.resolve();
    if (S.activeUi) { safe(S.activeUi.state, 'idle'); S.activeUi = null; }
  }

  function start(job, ui) {
    return new Promise(function (resolve) {
      var epoch = S.epoch;
      function withVoices(voices) {
        if (S.epoch !== epoch) { resolve(); return; }
        var voice = pickVoice(voices, job.locale, job.lang);
        if (!voice) { safe(ui.state, 'novoice'); resolve(); return; }
        if (S.activeUi && S.activeUi !== ui) { safe(S.activeUi.state, 'idle'); }
        S.activeUi = ui;
        safe(ui.state, 'speaking');
        try { if (synth.paused) { synth.resume(); } } catch (e) {}
        var chunks = split(job.text), i = 0, started = false;
        var watchdog = setTimeout(function () {
          if (!started && S.epoch === epoch) {
            S.epoch++;
            try { synth.cancel(); } catch (e) {}
            safe(ui.state, job.auto ? 'blocked' : 'error');
            resolve();
          }
        }, job.auto ? 2500 : 5000);
        function next() {
          if (S.epoch !== epoch) { clearTimeout(watchdog); resolve(); return; }
          if (i >= chunks.length) { clearTimeout(watchdog); safe(ui.state, 'done'); resolve(); return; }
          var u = new SpeechSynthesisUtterance(chunks[i++]);
          u.voice = voice; u.lang = voice.lang || job.locale; u.rate = 0.95; u.pitch = 1;
          S.keep = u;
          u.onstart = function () { started = true; };
          u.onend = function () { next(); };
          u.onerror = function (e) {
            clearTimeout(watchdog);
            var err = e && e.error;
            if (err === 'interrupted' || err === 'canceled') { resolve(); return; }
            safe(ui.state, 'error'); resolve();
          };
          synth.speak(u);
        }
        next();
      }
      var now = voicesNow();
      if (now.length) { withVoices(now); } else { loadVoices(withVoices); }
    });
  }

  S.play = function (job, ui) {
    ui = ui || {};
    if (!supported()) { safe(ui.state, 'unsupported'); return; }
    if (S.chat !== null && S.chat !== job.chat) { cancelAll(); S.spoken = {}; }
    S.chat = job.chat;
    if (S.lang !== null && S.lang !== job.lang) { cancelAll(); }   // language switched
    S.lang = job.lang;
    if (job.auto) {
      if (S.spoken[job.id]) { return; }                             // never auto-speak twice
      S.spoken[job.id] = true;
      if (S.turn !== job.turn) { cancelAll(); S.turn = job.turn; }  // new question: drop old speech
      if (!S.unlocked) { safe(ui.state, 'blocked'); return; }       // no user gesture yet
      S.queue = S.queue.then(function () { return start(job, ui); });
    } else {
      var busy = false;
      try { busy = synth.speaking || synth.pending; } catch (e) {}
      cancelAll();
      S.spoken[job.id] = true;
      if (busy) { setTimeout(function () { start(job, ui); }, 60); }
      else { start(job, ui); }
    }
  };
  S.stop = cancelAll;

  function unlock() {
    if (S.unlocked) { return; }
    S.unlocked = true;
    try {
      if (supported()) { var u = new SpeechSynthesisUtterance(' '); u.volume = 0; synth.speak(u); }
    } catch (e) {}
  }
  ['pointerdown', 'touchend', 'mousedown', 'keydown'].forEach(function (ev) {
    document.addEventListener(ev, unlock, { capture: true, passive: true });
  });
  // Starting a recording must not pick up the assistant's own voice.
  document.addEventListener('click', function (e) {
    var t = e.target;
    if (t && t.closest && t.closest('[data-testid="stAudioInput"]')) { cancelAll(); }
  }, true);
})();
'''

_SPEECH_BAR_HTML = r"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
html,body{margin:0;padding:0;background:transparent;font:13px/1.4 Arial,Helvetica,sans-serif;color:#cbd5e1}
.row{display:flex;flex-wrap:wrap;align-items:center;gap:6px}
button{border:1px solid #2dd4bf;border-radius:8px;background:#0f766e;color:#fff;cursor:pointer;
 min-height:40px;min-width:44px;padding:6px 12px;font-size:14px;touch-action:manipulation}
button:hover:not(:disabled){background:#115e59}
button:disabled{opacity:.45;cursor:default}
#status{flex:1 1 100%;min-width:0}
#status.warn{color:#ffe8a3}
</style></head><body>
<div class="row"><button id="play" type="button"></button><button id="stop" type="button" disabled></button>
<span id="status" role="status" aria-live="polite"></span></div>
<script>
(function () {
  var CFG = __CFG__;
  var ENGINE_SRC = __ENGINE__;
  var L = CFG.labels;
  function $(id) { return document.getElementById(id); }
  var host;
  try { void window.parent.document; host = window.parent; } catch (e) { host = window; }
  try {
    if (host !== window) {
      if (!host.__maTTS) {
        var s = host.document.createElement('script');
        s.textContent = ENGINE_SRC; host.document.head.appendChild(s);
      }
    } else if (!window.__maTTS) { (0, eval)(ENGINE_SRC); }
  } catch (e) {
    host = window;
    if (!window.__maTTS) { try { (0, eval)(ENGINE_SRC); } catch (e2) {} }
  }
  var T = host.__maTTS;
  $('play').textContent = L.listen;
  $('stop').textContent = L.stop;

  function resize() {
    try { window.frameElement.style.height = (document.documentElement.scrollHeight + 2) + 'px'; } catch (e) {}
  }
  var played = false;
  function state(name) {
    var st = $('status'), play = $('play'), stop = $('stop');
    st.className = ''; st.textContent = '';
    stop.disabled = true;
    if (name === 'speaking') { st.textContent = L.speaking; stop.disabled = false; played = true; }
    else if (name === 'done' || name === 'idle') { /* quiet */ }
    else if (L[name]) { st.textContent = L[name]; st.className = 'warn'; }
    play.textContent = played ? L.replay : L.listen;
    resize();
  }
  var ui = { state: state };
  function job(auto) {
    return { id: CFG.id, text: CFG.text, locale: CFG.locale, lang: CFG.lang,
             turn: CFG.turn, chat: CFG.chat, auto: auto };
  }
  $('play').addEventListener('click', function () { if (T) { T.play(job(false), ui); } else { state('unsupported'); } });
  $('stop').addEventListener('click', function () { if (T) { T.stop(); } state('idle'); });
  if (!T || !T.play) { state('unsupported'); return; }
  if (CFG.auto) { T.play(job(true), ui); }
  resize();
})();
</script></body></html>"""

_MIC_CHECK_HTML = r"""<!doctype html><html><body><script>
(function () {
  var L = __LABELS__;
  var host;
  try { void window.parent.document; host = window.parent; } catch (e) { host = window; }
  function notice(msg) {
    var d = host.document, old = d.getElementById('ma-voice-notice');
    if (old) { old.remove(); }
    var b = d.createElement('div');
    b.id = 'ma-voice-notice'; b.setAttribute('role', 'alert');
    b.style.cssText = 'position:fixed;left:50%;transform:translateX(-50%);bottom:84px;z-index:99999;' +
      'max-width:min(92vw,560px);background:#332b16;color:#ffe8a3;border:1px solid #8b6b27;' +
      'border-radius:12px;padding:10px 40px 10px 14px;font:14px/1.4 Arial,sans-serif;' +
      'box-shadow:0 6px 24px rgba(0,0,0,.4)';
    b.textContent = msg;
    var x = d.createElement('button');
    x.textContent = '✕'; x.setAttribute('aria-label', 'Close');
    x.style.cssText = 'position:absolute;top:4px;right:6px;background:none;border:0;color:inherit;' +
      'font-size:16px;cursor:pointer;min-width:32px;min-height:32px';
    x.onclick = function () { b.remove(); };
    b.appendChild(x); d.body.appendChild(b);
  }
  function clear() { var o = host.document.getElementById('ma-voice-notice'); if (o) { o.remove(); } }
  var nav = host.navigator;
  if (host.isSecureContext === false) { notice(L.mic_insecure); return; }
  if (!nav || !nav.mediaDevices || !nav.mediaDevices.getUserMedia) { notice(L.mic_unsupported); return; }
  try {
    nav.permissions.query({ name: 'microphone' }).then(function (p) {
      function check() { if (p.state === 'denied') { notice(L.mic_denied); } else { clear(); } }
      check(); p.onchange = check;
    }).catch(function () {});
  } catch (e) {}
})();
</script></body></html>"""


def clean_for_speech(text):
    """Remove Markdown, links and emoji so the voice reads natural sentences."""
    s = str(text)
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"[*_`#>~|]", "", s)
    s = re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]", " ", s)
    s = re.sub(r"\s*[—–]\s*", ", ", s)
    s = re.sub(r"([^.!?।:])[ \t]*\n+[ \t]*", r"\1. ", s)
    s = re.sub(r"\s*\n+\s*", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:3000]


def _json_for_script(value):
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def speech_controls(message_id, visible_text, autoplay, turn):
    """Render the per-message speaker controls (and optional one-time autoplay)."""
    language = st.session_state.get("language", "en")
    spoken_text = clean_for_speech(visible_text)
    if not spoken_text:
        return
    cfg = {
        "id": message_id,
        "text": spoken_text,
        "lang": language,
        "locale": {"en": "en-IN", "te": "te-IN", "hi": "hi-IN"}.get(language, "en-IN"),
        "turn": turn,
        "chat": st.session_state.get("chat_id", ""),
        "auto": bool(autoplay),
        "labels": BROWSER_TEXT.get(language, BROWSER_TEXT["en"]),
    }
    html = (_SPEECH_BAR_HTML
            .replace("__CFG__", _json_for_script(cfg))
            .replace("__ENGINE__", _json_for_script(_SPEECH_ENGINE_JS)))
    components.html(html, height=58)


def mic_support_check():
    """Hidden helper: warns about insecure pages, unsupported browsers or a blocked microphone."""
    labels = BROWSER_TEXT.get(st.session_state.get("language", "en"), BROWSER_TEXT["en"])
    html = _MIC_CHECK_HTML.replace("__LABELS__", _json_for_script(labels))
    with st.container(key="ma_voice_support"):
        components.html(html, height=0)


# ---------------------------------------------------------------
# Voice input: validate -> recognise -> same pipeline as typed text
# ---------------------------------------------------------------
def audio_problem(data):
    """Return 'empty' for too-short or silent recordings, otherwise None."""
    try:
        with wave.open(io.BytesIO(data), "rb") as wav:
            frames = wav.getnframes()
            rate = wav.getframerate() or 16000
            width = wav.getsampwidth()
            raw = wav.readframes(frames)
    except Exception:
        return "empty" if len(data) < 4000 else None  # not plain PCM WAV: let the recogniser decide
    if frames / float(rate) < 0.4:
        return "empty"
    if width == 2 and raw:
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
        if samples.size and float(np.sqrt(np.mean(samples ** 2))) < 12:
            return "empty"
    return None


def transcribe_audio(audio_bytes, language_code):
    recognizer = sr.Recognizer()
    recognizer.operation_timeout = 20
    with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio, language=language_code)


def process_voice_input(audio_file, status_slot):
    """Handle one recording exactly once and send the text through handle_user_message."""
    data = audio_file.getvalue()
    fingerprint = hashlib.sha256(data).hexdigest()
    processed = st.session_state.setdefault("processed_audio", set())
    if fingerprint in processed:
        return
    processed.add(fingerprint)  # marked first, so a failure can never cause a retry loop
    status_slot.info(vt("mic_processing"))
    spoken_text = ""
    try:
        if audio_problem(data):
            queue_notice("warning", vt("mic_empty"))
        else:
            spoken_text = transcribe_audio(data, st.session_state.get("speech_locale", "en-IN")).strip()
            if not spoken_text:
                queue_notice("warning", tr("Sorry, I couldn't understand. Please try speaking again."))
    except sr.UnknownValueError:
        queue_notice("warning", tr("Sorry, I couldn't understand. Please try speaking again."))
    except (sr.RequestError, TimeoutError, OSError):
        queue_notice("error", tr("Speech recognition is unavailable. Check your internet connection."))
    except Exception as exc:
        queue_notice("error", vt("mic_error", err=str(exc)[:120]))
    st.session_state.mic_nonce = st.session_state.get("mic_nonce", 0) + 1  # fresh, empty recorder
    if spoken_text:
        queue_notice("success", vt("mic_ok", text=spoken_text))
        handle_user_message(spoken_text)
    st.rerun()

@st.cache_resource(show_spinner="Loading MediAssist's saved AI model...")
def load_model():
    if core.os.path.exists(core.MODEL_FILE):
        return core.load_saved_model()
    # Only trains on the first run when no compatible saved model exists.
    return core.train_and_save()
def add_message(role, content, spoken=False):
    st.session_state.messages.append({
        "id": str(uuid.uuid4()),
        "role": role,
        "content": content,
        "turn": st.session_state.get("turn", 0),
        "spoken": spoken,
    })


def render_assistant(text):
    language = st.session_state.get("language", "en")
    # Store the English source text; the selected language is applied to display and audio.
    # Speech is played from the controls under each message (see speech_controls), never here.
    add_message("assistant", text)


def ask_next_question():
    a = st.session_state.assessment
    if a["question_count"] >= 6:
        a["stage"] = "duration"
        render_assistant("Thank you. How long have you had these symptoms? "
                         "For example: 2 days, 1 week, or since yesterday.")
        return
    results = core.get_predictions(a["model"], a["vector"], top_n=5)
    selected = core.choose_group_question(
        a["initial"],
        a["vector"],
        results,
        a["profiles"],
        a["symptom_cols"],
        a["asked_symptoms"],
        a["asked_groups"],
    )
    if selected is None:
        a["stage"] = "duration"
        render_assistant("I have asked the relevant follow-up questions available "
                         "for this assessment. How long have you had these symptoms?")
        return
    group_name, symptom, question = selected
    a["asked_symptoms"].add(symptom)
    a["asked_groups"].add(group_name)
    a["pending_symptom"] = symptom
    a["pending_group"] = group_name
    a["pending_question"] = question
    a["question_count"] += 1
    render_assistant(
        f"**Follow-up {a['question_count']} of 6**\n\n"
        f"{question}\n\n{core.TEXT['en']['answer_yes_no']}"
    )
def start_assessment(user_text):
    model_package = st.session_state.model_package
    symptom_cols = model_package["symptom_columns"]
    english_symptoms = model_language_text(user_text)
    vector, matched = core.text_to_vector(english_symptoms, symptom_cols)
    flags = core.check_red_flags(english_symptoms)
    st.session_state.assessment = {
        "model": model_package["model"],
        "profiles": model_package["profiles"],
        "symptom_cols": symptom_cols,
        "initial": english_symptoms,
        "vector": vector,
        "matched": matched,
        "initial_flags": flags,
        "asked_symptoms": set(),
        "asked_groups": set(),
        "answers": [],
        "question_count": 0,
        "stage": "followup",
        "duration": "",
        "severity": "",
    }
    results = core.get_predictions(model_package["model"], vector, top_n=5)
    response = "I understood your symptoms. Here is the initial model assessment:\n\n"
    if matched:
        response += "**Symptoms recognized:** " + ", ".join(matched[:15]) + "\n\n"
    else:
        response += "**Symptoms recognized:** No exact dataset symptom matched. "
        response += "The model may not fully understand this description.\n\n"
    response += "**Initial model classifications**\n"
    for rank, (disease, probability) in enumerate(results, start=1):
        response += f"{rank}. {disease} — {probability * 100:.1f}%\n"
    response += "\nThese are model outputs, not confirmed diagnoses or clinical certainty."
    if flags:
        response += (
            "\n\n🚨 **Urgent warning:** I detected a possible red-flag symptom: "
            + ", ".join(flags)
            + ". Please seek urgent medical attention now. Do not delay care "
              "to complete this chat."
        )
    render_assistant(response)
    if flags:
        # Continue only as an optional record, without suggesting that chat is care.
        render_assistant("If you are safe and still wish to continue this educational "
                         "assessment, answer the follow-up question below.")
    ask_next_question()
def finish_assessment():
    a = st.session_state.assessment
    results = core.get_predictions(a["model"], a["vector"], top_n=5)
    top_disease, top_probability = results[0]
    second_probability = results[1][1] if len(results) > 1 else 0.0
    margin = top_probability - second_probability
    yes_symptoms = [
        item["symptom"] for item in a["answers"] if item["answer"] == "yes"
    ]
    final_context = a["initial"] + " " + " ".join(yes_symptoms)
    flags = core.check_red_flags(final_context)
    if top_probability >= 0.60 and margin >= 0.15:
        lead = (
            f"The leading model classification is **{top_disease}** "
            f"({top_probability * 100:.1f}% model score)."
        )
    else:
        lead = (
            "The model did not produce a sufficiently separated result. "
            "Several conditions overlap, so no single result should be treated as confirmed."
        )
    response = "**Assessment summary**\n\n"
    response += lead + "\n\n**Top model classifications**\n"
    for rank, (disease, probability) in enumerate(results, start=1):
        response += f"{rank}. {disease} — {probability * 100:.1f}%\n"
    response += (
        f"\n**Duration:** {a['duration'] or 'Not provided'}"
        f"\n\n**Severity:** {a['severity']}"
        f"\n\n**Symptoms recognized:** "
        f"{', '.join(a['matched']) if a['matched'] else 'No exact match'}"
    )
    if flags:
        response += (
            "\n\n🚨 **Urgent warning:** " + ", ".join(flags)
            + ". Please seek urgent medical attention."
        )
    elif a["severity"] == "severe":
        response += "\n\nPlease seek prompt professional medical evaluation."
    elif top_probability < 0.30 or margin < 0.10:
        response += (
            "\n\nConsider discussing these symptoms with a qualified healthcare professional."
        )
    else:
        response += (
            "\n\nYou can share this summary with a healthcare professional for evaluation."
        )
    response += (
        "\n\n*This is a preliminary educational symptom assessment, not a diagnosis "
        "or a prescription. Do not start, stop, or change medication based on this result.*"
    )
    session = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "initial_symptoms": a["initial"],
        "recognized_symptoms": a["matched"],
        "duration": a["duration"],
        "severity": a["severity"],
        "follow_up_answers": a["answers"],
        "top_classification": top_disease,
        "top_probability": top_probability,
        "top_5": [
            {"disease": disease, "probability": probability}
            for disease, probability in results
        ],
        "red_flags": flags,
        "language": st.session_state.language,
        "input_mode": "chat",
    }
    core.save_session(session)
    a["stage"] = "completed"
    render_assistant(response)
def handle_user_message(user_text):
    user_text = user_text.strip()
    if not user_text:
        return
    now = time.time()
    last = st.session_state.get("_last_submit")
    if last and last[0] == user_text and now - last[1] < 1.0:
        return  # ignore accidental double submission
    st.session_state["_last_submit"] = (user_text, now)
    st.session_state.turn = st.session_state.get("turn", 0) + 1
    add_message("user", user_text)
    a = st.session_state.assessment
    if a is None or a["stage"] == "completed":
        lowered = user_text.lower()
        if lowered in {"hi", "hello", "hey", "నమస్కారం", "नमस्ते"}:
            render_assistant(
                "Hello! I’m MediAssist. Tell me what symptoms you are experiencing. "
                "You can type your message below."
            )
            return
        if any(word in lowered for word in ["help", "what can you do", "మీరు ఏమి"]):
            render_assistant(
                "I can collect symptom information, ask adaptive follow-up questions, "
                "and show preliminary model classifications. I cannot confirm a diagnosis, "
                "prescribe medicine, or replace a healthcare professional. "
                "Please describe your symptoms to begin."
            )
            return
        start_assessment(user_text)
        return
    if a["stage"] == "followup":
        answer = yes_no_value(user_text)
        if answer is None:
            render_assistant("Please answer **yes** or **no** so I can update the assessment.")
            return
        symptom = a["pending_symptom"]
        a["answers"].append({
            "group": a["pending_group"],
            "symptom": symptom,
            "question": a["pending_question"],
            "answer": "yes" if answer else "no",
        })
        index = a["symptom_cols"].index(symptom)
        a["vector"][index] = 1 if answer else 0
        ask_next_question()
        return
    if a["stage"] == "duration":
        a["duration"] = user_text
        a["stage"] = "severity"
        render_assistant(
            "How severe are your symptoms? Please reply **mild**, **moderate**, or **severe**."
        )
        return
    if a["stage"] == "severity":
        severity = severity_value(user_text)
        if severity not in {"mild", "moderate", "severe"}:
            render_assistant("Please choose **mild**, **moderate**, or **severe**.")
            return
        a["severity"] = severity
        finish_assessment()
        return
def reset_chat():
    st.session_state.messages = []
    st.session_state.assessment = None
    st.session_state.chat_id = str(uuid.uuid4())
    add_message(
        "assistant",
        "Hello! I’m **MediAssist**, your multilingual preliminary health-assessment assistant. "
        "Tell me what symptoms you are experiencing. You can type your message below.",
        spoken=True,
    )
# Sidebar controls
with st.sidebar:
    st.markdown(tr("## 🩺 MediAssist"))
    st.caption(tr("AI-powered preliminary health assistance"))
    # The widget label is language-neutral and the choice is remembered separately, so
    # translating the sidebar can never silently reset the language back to English.
    language_names = list(LANGUAGES.keys())
    remembered_name = st.session_state.get("_language_name", language_names[0])
    language_name = st.selectbox(
        vt("lang_label"),
        language_names,
        index=language_names.index(remembered_name) if remembered_name in language_names else 0,
    )
    st.session_state["_language_name"] = language_name
    language, speech_locale = LANGUAGES[language_name]
    st.session_state.language = language
    st.session_state.speech_locale = speech_locale
    core.LANGUAGE = language
    st.session_state.voice_reply = st.toggle(
        tr("Speak assistant replies"), value=st.session_state.get("_voice_reply", True)
    )
    st.session_state["_voice_reply"] = st.session_state.voice_reply
    st.caption(tr("Voice replies use your browser's available speech voice."))
    if st.button(tr("＋ New chat"), use_container_width=True):
        reset_chat()
        st.rerun()
    st.divider()
    st.markdown(tr("**About this model**"))
    st.write(tr("773 disease classes"))
    metrics = st.session_state.get("model_package", {}).get("metrics", {})
    if metrics:
        st.write(tr(f"Test accuracy: {metrics.get('accuracy', 0) * 100:.2f}%"))
    st.caption(tr("Model scores are not clinical probabilities."))
    st.divider()
    st.caption(tr("For emergencies, contact local emergency services or go to the nearest emergency department."))
st.markdown('<div class="brand">🩺 MediAssist</div>', unsafe_allow_html=True)
st.markdown(
    tr('<div class="subbrand">A conversational, multilingual health-assessment assistant</div>'),
    unsafe_allow_html=True,
)
st.markdown(
    tr('<div class="disclaimer">MediAssist provides preliminary educational information only. '
    'It is not a doctor, does not provide a confirmed diagnosis, and does not prescribe treatment. '
    'Do not delay urgent care to use this chatbot.</div>'),
    unsafe_allow_html=True,
)
st.write("")
if "messages" not in st.session_state:
    st.session_state.messages = []
if "assessment" not in st.session_state:
    st.session_state.assessment = None
if "voice_reply" not in st.session_state:
    st.session_state.voice_reply = True
if "language" not in st.session_state:
    st.session_state.language = "en"
if "speech_locale" not in st.session_state:
    st.session_state.speech_locale = "en-IN"
st.session_state.setdefault("mic_nonce", 0)
st.session_state.setdefault("turn", 0)
st.session_state.setdefault("chat_id", str(uuid.uuid4()))
if "model_package" not in st.session_state:
    try:
        st.session_state.model_package = load_model()
    except Exception as exc:
        st.error(tr(f"Could not load MediAssist model: {exc}"))
        st.info(tr("Check that your saved_model folder and dataset are in the project directory."))
        st.stop()
if not st.session_state.messages:
    reset_chat()
mic_support_check()
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        visible_content = tr(message["content"]) if message["role"] == "assistant" else message["content"]
        st.markdown(visible_content)
        if message["role"] == "assistant":
            # Auto-play each reply at most once (and only when the toggle is on); the
            # Listen / Replay / Stop buttons are always available.
            autoplay = bool(st.session_state.voice_reply) and not message.get("spoken", False)
            message["spoken"] = True
            speech_controls(message["id"], visible_content, autoplay, message.get("turn", 0))
for _kind, _text in st.session_state.pop("notices", []):
    getattr(st, _kind, st.info)(_text)
# Original message input with a microphone button beside it.
# The existing theme and all other page sections remain unchanged.
message_col, mic_col = st.columns([0.88, 0.12], vertical_alignment="bottom")
with message_col:
    with st.form("mediassist_message_form", clear_on_submit=True):
        typed_text = st.text_input(
            tr("Message MediAssist..."),
            key="mediassist_typed_message",
            label_visibility="collapsed",
            placeholder=tr("Message MediAssist..."),
        )
        send_message = st.form_submit_button(tr("Send"), use_container_width=True)
with mic_col:
    audio_file = st.audio_input(
        "🎙️",
        key=f"mediassist_mic_input_{st.session_state.mic_nonce}",
        sample_rate=16000,
        label_visibility="collapsed",
    )
voice_status_slot = st.empty()
if audio_file is None:
    voice_status_slot.caption(vt("mic_hint"))
if send_message and typed_text.strip():
    handle_user_message(typed_text.strip())
    st.rerun()
if audio_file is not None:
    process_voice_input(audio_file, voice_status_slot)
# Care navigation appears only after the symptom conversation is completed.
# It does not claim that the model has diagnosed a disease or booked an appointment.
assessment = st.session_state.get("assessment")
if assessment and assessment.get("stage") == "completed":
    st.markdown("---")
    st.markdown(tr("### 🩺 Your next step: connect with a healthcare professional"))
    st.write(tr(
        "MediAssist cannot confirm a disease. If you are concerned about your symptoms, "
        "you can use the options below to find a qualified doctor or nearby hospital."
    ))
    with st.container(border=True):
        st.markdown(tr("**Find care near you**"))
        st.markdown(tr("Use your current device location or enter an area manually. Your browser will ask for location permission."))
        live_location_html = """<!doctype html><html><body style="margin:0;background:#172235;font-family:Arial,sans-serif">
        <button id="liveLoc" style="background:#0f766e;color:#fff;border:1px solid #2dd4bf;border-radius:10px;padding:12px 16px;font-size:15px;font-weight:600;cursor:pointer;width:100%">📍 Use my live location</button>
        <div id="locStatus" style="color:#cbd5e1;font-size:13px;margin-top:8px"></div>
        <script>
        document.getElementById('liveLoc').addEventListener('click', function(){
          const status=document.getElementById('locStatus');
          if(!navigator.geolocation){status.textContent='Location is not supported by this browser.';return;}
          status.textContent='Requesting location permission…';
          navigator.geolocation.getCurrentPosition(function(pos){
            const lat=pos.coords.latitude, lon=pos.coords.longitude;
            status.textContent='Location found. Opening nearby hospitals in Google Maps…';
            window.open('https://www.google.com/maps/search/hospitals/@'+lat+','+lon+',14z','_blank');
          }, function(err){
            status.textContent=err.code===1?'Location permission was denied. Allow location access or enter your area below.':'Could not get your location. Check GPS and browser permissions, or enter your area below.';
          }, {enableHighAccuracy:true,timeout:15000,maximumAge:60000});
        });
        </script></body></html>"""
        location_labels = {
            "te": {
                "📍 Use my live location": "📍 నా ప్రస్తుత స్థానాన్ని ఉపయోగించండి",
                "Location is not supported by this browser.": "ఈ బ్రౌజర్‌లో స్థాన సేవ అందుబాటులో లేదు.",
                "Requesting location permission…": "స్థాన అనుమతి కోరుతోంది…",
                "Location found. Opening nearby hospitals in Google Maps…": "స్థానం కనుగొనబడింది. Google Maps లో సమీప ఆసుపత్రులను తెరుస్తోంది…",
                "Location permission was denied. Allow location access or enter your area below.": "స్థాన అనుమతి నిరాకరించబడింది. స్థాన అనుమతిని ఇవ్వండి లేదా మీ ప్రాంతాన్ని క్రింద నమోదు చేయండి.",
                "Could not get your location. Check GPS and browser permissions, or enter your area below.": "మీ స్థానాన్ని పొందలేకపోయాం. GPS మరియు బ్రౌజర్ అనుమతులను తనిఖీ చేయండి లేదా మీ ప్రాంతాన్ని క్రింద నమోదు చేయండి.",
            },
            "hi": {
                "📍 Use my live location": "📍 मेरी वर्तमान लोकेशन उपयोग करें",
                "Location is not supported by this browser.": "यह ब्राउज़र लोकेशन का समर्थन नहीं करता।",
                "Requesting location permission…": "लोकेशन की अनुमति माँगी जा रही है…",
                "Location found. Opening nearby hospitals in Google Maps…": "लोकेशन मिल गई। Google Maps में नज़दीकी अस्पताल खोले जा रहे हैं…",
                "Location permission was denied. Allow location access or enter your area below.": "लोकेशन की अनुमति नहीं मिली। अनुमति दें या नीचे अपना क्षेत्र दर्ज करें।",
                "Could not get your location. Check GPS and browser permissions, or enter your area below.": "लोकेशन नहीं मिल सकी। GPS और ब्राउज़र अनुमति जाँचें या नीचे अपना क्षेत्र दर्ज करें।",
            },
        }
        for source_label, translated_label in location_labels.get(st.session_state.language, {}).items():
            live_location_html = live_location_html.replace(source_label, translated_label)
        components.html(live_location_html, height=75)
        care_location = st.text_input(
            tr("Enter your city, area, or PIN code"),
            key="care_location",
            placeholder=tr("e.g. Hanamkonda, Warangal or 506001"),
            help=tr("Your location is used only to create map-search links. It is not saved by this feature."),
        )
        if care_location.strip():
            place = care_location.strip()
            hospital_query = quote_plus(f"hospitals near {place}")
            doctor_query = quote_plus(f"doctors near {place}")
            clinic_query = quote_plus(f"clinics near {place}")
            hospitals_url = f"https://www.google.com/maps/search/?api=1&query={hospital_query}"
            doctors_url = f"https://www.google.com/maps/search/?api=1&query={doctor_query}"
            clinics_url = f"https://www.google.com/maps/search/?api=1&query={clinic_query}"
            st.markdown(tr("**Explore locations on the map**"))
            map_tabs = st.tabs([tr("🏥 Hospitals"), tr("👨‍⚕️ Doctors"), tr("➕ Clinics")])
            for tab, query in zip(map_tabs, [hospital_query, doctor_query, clinic_query]):
                with tab:
                    embed_url = f"https://www.google.com/maps?q={query}&output=embed"
                    map_html = (
                        '<iframe title="Google Maps results" src="' + embed_url +
                        '" width="100%" height="430" style="border:0;border-radius:12px" '
                        'loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>'
                    )
                    components.html(map_html, height=440)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.link_button(tr("Open hospitals in Google Maps"), hospitals_url, use_container_width=True)
            with c2:
                st.link_button(tr("Open doctors in Google Maps"), doctors_url, use_container_width=True)
            with c3:
                st.link_button(tr("Open clinics in Google Maps"), clinics_url, use_container_width=True)
            st.caption(tr("Google Maps supplies the live map and listings. Confirm opening hours, services, doctor availability, and contact details directly. Results depend on the location you entered."))
        else:
            st.caption(tr("Enter your location to see nearby hospitals, doctors, and clinics on a map."))
    st.markdown(tr("**Need urgent help?**"))
    st.error(
        tr("For severe symptoms, chest pain, difficulty breathing, fainting, or heavy bleeding, "
        "seek emergency care immediately. In India, call **112** for emergency assistance. "
        "Do not wait for MediAssist or a map search.")
    )
    st.caption(tr("MediAssist does not directly contact doctors, book appointments, or transmit your health information to hospitals."))
