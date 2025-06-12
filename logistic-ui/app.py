import streamlit as st
import pandas as pd
import altair as alt
import os

FLOWS_CSV = os.getenv("FLOWS_CSV", "flows.csv")
CELLS_CSV = os.getenv("CELLS_CSV", "cells.csv")

st.set_page_config(page_title="Analyse Logistique", layout="wide")

st.title("🔍 Analyse des Résultats Logistiques")

flows_df = pd.read_csv(FLOWS_CSV)
cells_df = pd.read_csv(CELLS_CSV)

st.header("1️⃣ Analyse des Flux Logistiques")
st.metric("Nombre de flux utilisés", len(flows_df))
st.metric("Volume total transporté", f"{flows_df['value'].sum():,.0f} unités")

st.subheader("Top 10 des plus gros flux")
top_flows = flows_df.sort_values(by="value", ascending=False).head(10)
st.dataframe(top_flows)
chart1 = alt.Chart(top_flows).mark_bar().encode(
    x=alt.X("edgeId:N", sort="-y", title="ID Flux"),
    y=alt.Y("value:Q", title="Quantité transportée"),
    tooltip=["edgeId", "value"]
).properties(height=300)
st.altair_chart(chart1, use_container_width=True)

st.header("2️⃣ Analyse des Cellules de Stockage")
nb_cells = cells_df["cellId"].nunique()
st.metric("Cellules utilisées", nb_cells)

st.subheader("Répartition des produits par cellule")
products_per_cell = cells_df.groupby("cellId")["productId"].nunique().reset_index()
products_per_cell.columns = ["cellId", "nbProduits"]
st.dataframe(products_per_cell.sort_values(by="nbProduits", ascending=False))

chart2 = alt.Chart(products_per_cell).mark_bar().encode(
    x=alt.X("cellId:N", sort="-y", title="Cellule"),
    y=alt.Y("nbProduits:Q", title="Produits stockés"),
    tooltip=["cellId", "nbProduits"]
).properties(height=300)
st.altair_chart(chart2, use_container_width=True)

st.subheader("Occupation des cellules par période")
occu = cells_df.groupby("timePeriodId")["cellId"].nunique().reset_index()
occu.columns = ["Période", "NbCellules"]
chart3 = alt.Chart(occu).mark_bar().encode(
    x="Période",
    y="NbCellules",
    tooltip=["Période", "NbCellules"]
).properties(height=300)
st.altair_chart(chart3, use_container_width=True)
