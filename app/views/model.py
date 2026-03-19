import streamlit as st
import pandas as pd
import plotly.express as px

#st.set_page_config(layout="wide")

st.title("📊 Score Bradley-Terry vs Consommation")

st.markdown("""
Compare Large Language Models based on:

- 🧠 **Performance** (Bradley-Terry score)
- ⚡ **Energy consumption**
- ⚖️ **Model size**

👉 Goal: identify the **most efficient models (high score, low energy)**.
""")
st.markdown("""Informations extract from:
* 🧠 https://comparia.beta.gouv.fr/ranking
* ⚡ https://ecologits.ai/latest/""")


# --- Chargement données ---
df_model = pd.read_csv('./data/model-energy-2_11_2026.csv')#, index_col=0)

df_model.columns = df_model.columns.str.strip()

# --- Mapping colonnes (à adapter si besoin) ---
MODEL = "id"
BT = "Bradley-Terry_Score"
ENERGY = "Consumption_mWh_1000_tokens"
SIZE = "Size"              # taille du modèle
PARAM= "Parameters_B"
ARCH = "Architecture"           # ex: transformer, moe...
ORGA = "Organisation"

#st.write(df_model.columns.tolist())

# --- Nettoyage ---
df_model[MODEL] = df_model[MODEL].astype(str).str.strip()
df_model_ENERGY = df_model.dropna(subset=[BT, ENERGY])
df_model["Efficiency"] = df_model_ENERGY[BT] / df_model[ENERGY]

# --- SIDEBAR FILTRES ---
st.sidebar.header("🔎 Filtres")

# Filtre modèles
models = st.sidebar.multiselect(
    "Modèles",
    df_model[MODEL].unique(),
    default=df_model[MODEL].unique()
)

# Filtre architecture
architectures = st.sidebar.multiselect(
    "Architecture",
    df_model[ARCH].dropna().unique(),
    default=df_model[ARCH].dropna().unique()
)

# Filtre taille modèle
min_size, max_size = float(df_model[PARAM].min()), float(df_model[PARAM].max())
size_range = st.sidebar.slider(
    "Taille du modèle",
    min_size, max_size, (min_size, max_size)
)

# Filtre énergie
min_energy, max_energy = float(df_model_ENERGY[ENERGY].min()), float(df_model_ENERGY[ENERGY].max())
energy_range = st.sidebar.slider(
    "Consommation énergétique",
    min_energy, max_energy, (min_energy, max_energy)
)

# --- APPLICATION FILTRES ---
filtered_df_model_ENERGY = df_model[
    (df_model[MODEL].isin(models)) &
    (df_model[ARCH].isin(architectures)) &
    (df_model[PARAM].between(size_range[0], size_range[1])) &
    (df_model[ENERGY].between(energy_range[0], energy_range[1]) )
]

filtered_df_model = df_model[
    (df_model[MODEL].isin(models)) &
    (df_model[ARCH].isin(architectures))
]

# WINNER
best_model = df_model.sort_values("Efficiency", ascending=False).iloc[0]

st.html("<hr>")
st.metric(
    "🏆 Most efficient model",
    best_model[MODEL],
    delta=f"Score/Energy = {best_model['Efficiency']:.2f}"
)
st.html("<hr>")

# --- GRAPHIQUE ---

fig = px.scatter(
    filtered_df_model_ENERGY,
    x=ENERGY,
    y=BT,
    size=PARAM,
    color=ARCH,
    hover_name=MODEL,
    size_max=60,
    title="BT Score vs Consommation (1000 tokens)"
)

fig.update_layout(
    xaxis_title="Consommation énergétique",
    yaxis_title="Score Bradley-Terry",
    legend_title="Architecture"
)
# Échelle logarithmique (souvent utilisée)
fig.update_xaxes(type="log")
fig.update_yaxes(type="log")
# Afficher labels sur points importants
fig.update_traces(textposition="top center")

st.plotly_chart(fig, use_container_width=True)


# 2nd graph
with st.expander("🏆 Top Efficiency Models"):
    fig2 = px.bar(
    #    filtered_df_model_ENERGY.sort_values("Efficiency", ascending=False).head(15),
        df_model.sort_values("Efficiency", ascending=False).head(15),
        x="Efficiency",
        y=MODEL,
        orientation="h",
        title="🏆 Top Efficient Models"
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- TABLEAU ---
with st.expander("📄 Voir les données filtrées"):
    st.dataframe(filtered_df_model_ENERGY)

# --- TABLEAU ---
with st.expander("📄 Voir les données non filtrées"):
    st.dataframe(df_model)

with st.expander("📄 Aditional informations on Large Language Models model types"):
    st.markdown("## additional informations")
    st.markdown("### model type")
    st.markdown("#### Dense")
    st.markdown(" Think of a “standard”, Dense LLM model like a single, highly knowledgeable expert (or team) that tackles every single part of your request with its full brainpower. ")
    st.markdown("#### MoE - Mixture of Experts")
    st.markdown(" An LLM models that use router to select the most appropriate LLM taking in acount the training data of the LLM and the size of the model and the request")
    st.markdown("#### MatFormer")
    st.markdown(" extract of MoE models that has been resized without dooing a specific training")
    st.markdown("#### Ref")
    st.markdown("- https://maximilian-schwarzmueller.com/articles/understanding-mixture-of-experts-moe-llms/")
    st.markdown("- MatFormer - A nested Transformer Architecture for Elastic Inference - \n"
    "https://vinithavn.medium.com/matformer-a-nested-transformer-architecture-for-elastic-inference-682beb5f3528")