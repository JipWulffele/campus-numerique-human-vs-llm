import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

st.title('(not so) Creative LLMs')


################################################
### Wordclouds
################################################

image = Image.open("./data/wordclouds.png")
st.image(image, caption="LLM vs Human Word Clouds")

################################################
### Boxplots
################################################

# Load data-------------------------------------------------------------------------
df_cosine = pd.read_csv('./data/cosine_similairity_neigbor.csv', index_col=0)

# Column layout for box plots-------------------------------------------------------------
col1, col2, col3 = st.columns([2, 2, 1])

# Sidebar / selector (col3) ---------------------------------------------------------
with col3:
    embedding_models = df_cosine["embedding_model"].unique()

    selected_embedding = st.selectbox(
        "Embedding model",
        embedding_models,
        index=0  # default = first
    )

# Filter data -----------------------------------------------------------------------
df_filtered = df_cosine[df_cosine["embedding_model"] == selected_embedding].copy()

# Split by language -----------------------------------------------------------------
df_filtered["language"] = df_filtered["language"].str.strip().str.lower()
df_en = df_filtered[df_filtered["language"] == "english"]
df_fr = df_filtered[df_filtered["language"] == "french"]

# Sort models by avg cosine (ascending) ---------------------------------------------
model_order_en = (
    df_en 
    .groupby("model")["avg_cosine"]
    .mean()
    .sort_values(ascending=True)
    .index
)

model_order_fr = (
    df_fr 
    .groupby("model")["avg_cosine"]
    .mean()
    .sort_values(ascending=True)
    .index
)

# Set up colors----------------------------------------------
df_fr = df_fr.fillna("N/A")
color_map = {
    "N/A": "#54478C",        # grey (humans)
    "US": "#EFEA5A",         # blue
    "France": "#f29e4c",      # red
    "China": "#F1C453",       # purple
}

y_min = df_filtered["avg_cosine"].min()
y_max = df_filtered["avg_cosine"].max()

# Plot English ----------------------------------------------------------------------
with col1:
    st.subheader("English")

    fig_en = px.box(
        df_en,
        x="model",
        y="avg_cosine",
        color="country",
        category_orders={"model": list(model_order_en)},
        color_discrete_map=color_map
    )
    fig_en.update_traces(width=0.6)
    fig_en.update_yaxes(range=[y_min, y_max])
    fig_en.update_layout(xaxis_title=None)
    fig_en.update_yaxes(title="Average cosine similarity")

    st.plotly_chart(fig_en, use_container_width=True)

# Plot French -----------------------------------------------------------------------
with col2:
    st.subheader("French")

    fig_fr = px.box(
        df_fr,
        x="model",
        y="avg_cosine",
        color="country",
        category_orders={"model": list(model_order_fr)},
        color_discrete_map=color_map
    )
    fig_fr.update_traces(width=0.6)
    fig_fr.update_yaxes(range=[y_min, y_max])
    fig_fr.update_layout(xaxis_title=None)
    fig_fr.update_yaxes(title="Average cosine similarity")

    st.plotly_chart(fig_fr, use_container_width=True)

################################################
### Neighborhood bias
################################################

# Column layout for box plots-------------------------------------------------------------
col1, col2 = st.columns([4, 1])

df_fr["cosine_difference"] = df_fr["avg_cosine"] -  df_fr["avg_neighbor_cosine"]

# Plot English ----------------------------------------------------------------------
with col1:
    st.subheader("Neighborhood bias")

    fig_en = px.box(
        df_fr,
        x="model",
        y="cosine_difference",
        color="country",
        category_orders={"model": list(model_order_fr)},
        color_discrete_map=color_map
    )
    fig_en.update_traces(width=0.6)
    fig_en.update_layout(xaxis_title=None)
    fig_en.update_yaxes(title="Difference in cosine similarity")

    st.plotly_chart(fig_en, use_container_width=True)
