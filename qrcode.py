import streamlit as st
import pandas as pd
from datetime import datetime
import os

CSV_FILENAME = "pointage_femme_menage.csv"

st.set_page_config(page_title="Suivi femme de ménage", page_icon="📊", layout="wide")
st.title("📊 Suivi des horaires - Femme de ménage")

if not os.path.exists(CSV_FILENAME):
    st.warning("Aucun pointage encore enregistré.")
    st.stop()

df = pd.read_csv(CSV_FILENAME)

st.markdown("### Derniers passages")
st.dataframe(df.tail(14), use_container_width=True)

st.markdown("---")
st.header("Synthèse et export")

# Sélection période
periode = st.selectbox("Période :", ["Cette semaine", "Ce mois", "Tout"], key="periode_suivi_unique_1")
now = datetime.now()

if periode == "Cette semaine":
    semaine = now.isocalendar().week
    recap = df[df["Date"].apply(lambda d: datetime.strptime(d, "%Y-%m-%d").isocalendar().week) == semaine]
elif periode == "Ce mois":
    mois = now.month
    recap = df[df["Date"].apply(lambda d: datetime.strptime(d, "%Y-%m-%d").month) == mois]
else:
    recap = df

# Calcul heures
def calc_heures(row):
    try:
        h1 = datetime.strptime(str(row["Heure arrivée"]), "%H:%M:%S")
        h2 = datetime.strptime(str(row["Heure sortie"]), "%H:%M:%S") if pd.notna(row["Heure sortie"]) else None
        return (h2 - h1).total_seconds() / 3600 if h2 else None
    except:
        return None

recap["Heures travaillées"] = recap.apply(calc_heures, axis=1)
st.write(recap)

st.markdown(f"**Total heures travaillées :** {round(recap['Heures travaillées'].sum(skipna=True) or 0, 2)}h")

# Export
st.download_button(
    label="📥 Télécharger le CSV",
    data=recap.to_csv(index=False).encode("utf-8"),
    file_name="pointage_femme_menage_export.csv",
    mime="text/csv"
)
