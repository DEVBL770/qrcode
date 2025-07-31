import streamlit as st
import pandas as pd
from datetime import datetime
import requests

GOOGLE_APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxZLi0wYP3DEVTPbGDxw4czSVaeaAGbYT07iEzIH3iC6txqp1lqv6Ab7Jy-oIv2v1TTNg/exec"

st.set_page_config(page_title="Suivi femme de ménage", page_icon="📊", layout="wide")
st.title("📊 Suivi des horaires - Femme de ménage")

def charger_df():
    try:
        resp = requests.get(GOOGLE_APPS_SCRIPT_URL, timeout=10)
        data = resp.json()
        if not data or len(data) < 2:
            return pd.DataFrame(columns=["Date", "Heure arrivée", "Heure sortie"])
        columns = data[0]
        rows = data[1:]
        return pd.DataFrame(rows, columns=columns)
    except Exception as e:
        st.error(f"Erreur de connexion à la feuille Google Sheets : {e}")
        return pd.DataFrame(columns=["Date", "Heure arrivée", "Heure sortie"])

df = charger_df()
if df.empty:
    st.info("Aucun pointage enregistré.")
else:
    st.markdown("### Derniers passages")
    st.dataframe(df.tail(14), use_container_width=True)

    st.markdown("---")
    st.header("Synthèse et export")

    periode = st.selectbox("Période :", ["Cette semaine", "Ce mois", "Tout"], key="periode_suivi_unique_1")
    now = datetime.now()

    def safe_week(d):
        try:
            return datetime.strptime(d, "%Y-%m-%d").isocalendar().week
        except Exception:
            return -1

    def safe_month(d):
        try:
            return datetime.strptime(d, "%Y-%m-%d").month
        except Exception:
            return -1

    if periode == "Cette semaine":
        semaine = now.isocalendar().week
        recap = df[df["Date"].apply(safe_week) == semaine]
    elif periode == "Ce mois":
        mois = now.month
        recap = df[df["Date"].apply(safe_month) == mois]
    else:
        recap = df

    def calc_heures(row):
        try:
            h1 = datetime.strptime(str(row["Heure arrivée"]), "%H:%M:%S")
            h2 = datetime.strptime(str(row["Heure sortie"]), "%H:%M:%S") if pd.notna(row["Heure sortie"]) and row["Heure sortie"] != "" else None
            return (h2 - h1).total_seconds() / 3600 if h2 else None
        except:
            return None

    if not recap.empty:
        recap["Heures travaillées"] = recap.apply(calc_heures, axis=1)
        st.write(recap)
        st.markdown(f"**Total heures travaillées :** {round(recap['Heures travaillées'].sum(skipna=True) or 0, 2)} h")
        st.download_button(
            label="📥 Télécharger le CSV",
            data=recap.to_csv(index=False).encode("utf-8"),
            file_name="pointage_femme_menage_export.csv",
            mime="text/csv"
        )
    else:
        st.info("Aucun pointage pour cette période.")
