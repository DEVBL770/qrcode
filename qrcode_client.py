import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import os

# PARAMÈTRES
TELEGRAM_BOT_TOKEN = "8485390899:AAF1Qd6ISc7MIHIWUs4FZrseFCboIdkWof0"
TELEGRAM_CHAT_ID = "402634505"
CSV_FILENAME = "pointage_femme_menage.csv"
NOM_PERSONNE = "Femme de ménage"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except:
        pass

def charger_df():
    if os.path.exists(CSV_FILENAME):
        return pd.read_csv(CSV_FILENAME)
    else:
        return pd.DataFrame(columns=["Date", "Heure arrivée", "Heure sortie"])

def sauvegarder_df(df):
    df.to_csv(CSV_FILENAME, index=False)

st.set_page_config(page_title="Pointage travail", page_icon="🧹", layout="centered")
hide_menu = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

now = datetime.now()
date_str = now.strftime("%Y-%m-%d")
heure_str = now.strftime("%H:%M:%S")

df = charger_df()

mask_today = df["Date"] == date_str

if mask_today.any() and pd.isna(df.loc[mask_today, "Heure sortie"].iloc[-1]):
    # Si arrivée sans sortie : c'est la sortie
    idx = df[mask_today & df["Heure sortie"].isna()].index[-1]
    df.at[idx, "Heure sortie"] = heure_str
    sauvegarder_df(df)
    msg = f"🧹 {NOM_PERSONNE} a terminé son travail à {heure_str} le {date_str}."
    send_telegram(msg)
    st.success("✅ Fin du travail enregistrée !\n\nMerci et bonne journée.")
else:
    # Sinon, c'est une arrivée
    new_row = {"Date": date_str, "Heure arrivée": heure_str, "Heure sortie": None}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    sauvegarder_df(df)
    msg = f"🧹 {NOM_PERSONNE} a commencé le travail à {heure_str} le {date_str}."
    send_telegram(msg)
    st.success("🟢 Début du travail enregistré !\n\nBonne journée !")

# On masque tout le reste, elle ne voit que le popup (success)
st.stop()
