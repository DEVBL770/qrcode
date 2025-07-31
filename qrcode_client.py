import streamlit as st
from datetime import datetime
import requests

GOOGLE_APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxZLi0wYP3DEVTPbGDxw4czSVaeaAGbYT07iEzIH3iC6txqp1lqv6Ab7Jy-oIv2v1TTNg/exec"

TELEGRAM_BOT_TOKEN = "8485390899:AAF1Qd6ISc7MIHIWUs4FZrseFCboIdkWof0"
TELEGRAM_CHAT_ID = "402634505"
NOM_PERSONNE = "Femme de ménage"

st.set_page_config(page_title="Scan", page_icon="🧹")
hide_menu = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        st.warning(f"Erreur Telegram : {e}")

def charger_df():
    try:
        resp = requests.get(GOOGLE_APPS_SCRIPT_URL, timeout=10)
        data = resp.json()
        if not data or len(data) < 2:
            return []
        columns = data[0]
        rows = data[1:]
        return columns, rows
    except Exception as e:
        st.error(f"Erreur de connexion à la feuille Google Sheets : {e}")
        return [], []

def ajouter_pointage(date, heure_arrivee=None, heure_sortie=None):
    payload = {"Date": date, "Heure arrivée": heure_arrivee, "Heure sortie": heure_sortie}
    try:
        r = requests.post(GOOGLE_APPS_SCRIPT_URL, json=payload, timeout=10)
        return r.text
    except Exception as e:
        st.error(f"Erreur d'envoi : {e}")
        return None

now = datetime.now()
date_str = now.strftime("%Y-%m-%d")
heure_str = now.strftime("%H:%M:%S")

columns, rows = charger_df()
df_rows = [dict(zip(columns, row)) for row in rows] if columns else []
df_today = [r for r in df_rows if r["Date"] == date_str]

# Détecte si arrivée ou sortie
if not df_today or not df_today[-1]["Heure arrivée"] or df_today[-1]["Heure sortie"]:
    # Nouvelle arrivée
    reponse = ajouter_pointage(date_str, heure_arrivee=heure_str)
    msg = f"🧹 {NOM_PERSONNE} a commencé le travail à {heure_str} le {date_str}."
    send_telegram(msg)
    st.success("🟢 Début du travail enregistré !")
elif df_today[-1]["Heure arrivée"] and not df_today[-1]["Heure sortie"]:
    # On complète la sortie
    reponse = ajouter_pointage(date_str, heure_sortie=heure_str)
    msg = f"🧹 {NOM_PERSONNE} a terminé le travail à {heure_str} le {date_str}."
    send_telegram(msg)
    st.success("✅ Fin du travail enregistrée !")
else:
    st.warning("Action inattendue, réessayez.")

st.stop()
