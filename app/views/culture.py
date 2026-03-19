import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np



# --------------------------------------------------
# Project description banner
# --------------------------------------------------

st.title("🎭 IA & Patrimoine Culturel — Évaluation de modèles de langage")

st.markdown("""
<div style="
    background-color: #f0f4f9;
    border-left: 5px solid #1F3864;
    border-radius: 6px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.5rem;
">

<h4 style="color:#1F3864; margin-top:0;">À propos de ce projet</h4>

<p>
Ce tableau de bord présente les résultats du défi 
<a href="https://defis.data.gouv.fr/defis/ia-culturelles" target="_blank"><strong>IA Culturelles</strong></a> 
porté par data.gouv.fr. L'objectif est d'évaluer dans quelle mesure les grands modèles de langage (LLM) 
répondent correctement à des questions sur le <strong>patrimoine culturel français et européen</strong>, 
et de mesurer leurs biais — notamment le biais <em>anglocentrique</em>.
</p>

<p>
Le jeu de données de questions-réponses a été construit à partir de plusieurs sources ouvertes :
<strong>Joconde</strong> (catalogue national des musées),
<strong>CNC</strong> (données d'entrées cinéma),
<strong>base des lieux et équipements culturels</strong> du Ministère de la Culture.
Les questions couvrent 7 catégories : biais culturel, disambiguation d'entités, distracteurs réalistes,
données open data, raisonnement multi-hop, méta-test biais IA, et questions temporelles.
</p>

<p>
Trois modèles ont été évalués :
<strong>DeepSeek-V3.2</strong>, <strong>Mistral-Small-2506</strong> et <strong>Gemma-3n-e4b-it</strong>.
L'évaluation combine trois approches complémentaires :
</p>

<ul>
  <li>📐 <strong>Métrique automatique</strong> — BERTScore</li>
  <li>🤖 <strong>LLM-as-Judge</strong> — notation par Claude Sonnet 4.6 sur 3 dimensions (exactitude, biais, complétude)</li>
  <li>👤 <strong>Jugement humain</strong> — annotation binaire (correct / incorrect) par un expert</li>
</ul>

<p style="margin-bottom:0;">
L'énergie consommée par chaque modèle (en mWh / 1 000 tokens) est également intégrée pour 
permettre une <strong>comparaison performance / empreinte environnementale</strong>.
</p>

</div>
""", unsafe_allow_html=True)

# Metrics summary row
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Questions évaluées", "31")
col_m2.metric("Réponses annotées", "93")
col_m3.metric("Modèles comparés", "3")
col_m4.metric("Accord juge-humain", "86%")

st.divider()

# --------------------------------------------------
# Data loading
# --------------------------------------------------

df_scores = pd.read_csv("data/scores_automatiques.csv")
llm_human_score = pd.read_excel('data/llm_judge_scores.xlsx', sheet_name="Judge_Scores")
conso = pd.read_csv("data/model-energy-2_11_2026.csv")

df_scores = df_scores.merge(conso, left_on="modele", right_on="id_model_culture", how="left")
llm_human_score = llm_human_score.merge(conso, left_on="Model", right_on="id_model_culture", how="left")
df_scores["consumption_mWh_1000tokens"] = df_scores["consumption_mWh_1000tokens"].astype(float)
llm_human_score["consumption_mWh_1000tokens"] = llm_human_score["consumption_mWh_1000tokens"].astype(float)

# --------------------------------------------------
# 🟦 1. BAR PLOTS (3 on same row)
# --------------------------------------------------

st.subheader("Scores moyens par modèle")
st.caption("Les modèles sont triés par consommation énergétique croissante. Le label indique : nom du modèle / consommation (mWh/1 000 tokens) / taille.")

avg_scores_1 = (
    df_scores
    .groupby(["modele","consumption_mWh_1000tokens", "size"])[["bert_score_f1"]]
    .mean()
    .round(4)
    .reset_index()
)
avg_scores_1['label'] = avg_scores_1.apply(
    lambda row: f"{row['modele']}<br>{row['consumption_mWh_1000tokens']:.2f}<br>{row['size']}",
    axis=1
)

avg_scores_2 = (
    llm_human_score
    .groupby(["Model","consumption_mWh_1000tokens", "size"])[["Judge_Total"]]
    .mean()
    .round(4)
    .reset_index()
)
avg_scores_2['label'] = avg_scores_2.apply(
    lambda row: f"{row['Model']}<br>{row['consumption_mWh_1000tokens']:.2f}<br>{row['size']}",
    axis=1
)

avg_scores_3 = (
    llm_human_score
    .groupby(["Model","consumption_mWh_1000tokens", "size"])[["Human_Correct"]]
    .mean()
    .round(4)
    .reset_index()
)
avg_scores_3['label'] = avg_scores_3.apply(
    lambda row: f"{row['Model']}<br>{row['consumption_mWh_1000tokens']:.2f}<br>{row['size']}",
    axis=1
)

fig1 = px.bar(
    avg_scores_1.sort_values(by="consumption_mWh_1000tokens", ascending=True),
    x='label', y='bert_score_f1',
    title="BERTScore F1 moyen"
)
fig1.update_layout(xaxis_title="Modèle", yaxis_title="BERTScore F1", height=500, showlegend=False)
fig1.update_coloraxes(showscale=False)
fig1.add_annotation(
    text="<b>Cons. (mWh/1000t) =</b><br><b>Size =</b>",
    xref="paper", yref="paper",
    x=0.1, y=-0.18, showarrow=False,
    font=dict(size=10), align="right", xanchor="right"
)

fig2 = px.bar(
    avg_scores_2.sort_values(by="consumption_mWh_1000tokens", ascending=True),
    x='label', y='Judge_Total',
    title="LLM-as-Judge — Score moyen /7"
)
fig2.update_layout(xaxis_title="Modèle", yaxis_title="Score moyen /7", height=500, showlegend=False)
fig2.update_coloraxes(showscale=False)

fig3 = px.bar(
    avg_scores_3.sort_values(by="consumption_mWh_1000tokens", ascending=True),
    x='label', y='Human_Correct',
    title="Jugement humain — Taux de réponses correctes"
)
fig3.update_layout(xaxis_title="Modèle", yaxis_title="Taux correct", height=500, showlegend=False)
fig3.update_coloraxes(showscale=False)

col1, col2, col3 = st.columns(3)
with col1:
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    st.plotly_chart(fig2, use_container_width=True)
with col3:
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# --------------------------------------------------
# 🔥 2. HEATMAPS (2 on same row)
# --------------------------------------------------

st.subheader("Scores par catégorie de question")
st.caption("Chaque cellule représente le score moyen du modèle sur la catégorie. Les cases vides indiquent qu'aucune réponse n'est disponible pour cette combinaison.")

pivot_1 = llm_human_score.pivot_table(
    values='Judge_Total',
    index='Model',
    columns='Subject',
    aggfunc='mean'
)

fig_heatmap_1 = px.imshow(
    pivot_1,
    text_auto='.2f',
    aspect="auto",
    title='LLM-as-Judge — Score /7 par catégorie',
    labels=dict(x="Catégorie", y="Modèle", color="Score"),
    color_continuous_scale='Blues'
)

pivot_2 = llm_human_score.pivot_table(
    values='Human_Correct',
    index='Model',
    columns='Subject',
    aggfunc='mean'
)

fig_heatmap_2 = px.imshow(
    pivot_2,
    text_auto=True,
    aspect="auto",
    title='Jugement humain — Taux correct par catégorie',
    labels=dict(x="Catégorie", y="Modèle", color="Taux"),
    color_continuous_scale='Greens'
)

col4, col5 = st.columns(2)
with col4:
    st.plotly_chart(fig_heatmap_1, use_container_width=True)
with col5:
    st.plotly_chart(fig_heatmap_2, use_container_width=True)

# --------------------------------------------------
# 🔎 3. DETAIL EXPANDER — one row per question, all models side by side
# --------------------------------------------------
 
 
MODEL_ORDER = ["DeepSeek-V3.2", "gemma-3n-e4b-it", "mistral-small-2506"]
st.subheader("🔎 Détail par question")
st.caption(
    "Tableau comparatif : pour chaque question, les réponses des 3 modèles "
    "et leurs scores BERTScore, LLM-as-Judge et Humain côte à côte."
)
 
with st.expander("📋 Ouvrir le tableau de détail par question", expanded=False):
 
    # ── Build wide table ──────────────────────────────────────────
 
    # 1. One row per question: ID, question, reference answer, category, level
    base = (
        llm_human_score[["ID", "Question", "Réponse_correcte", "Catégorie", "Niveau"]]
        .drop_duplicates(subset="ID")
        .reset_index(drop=True)
    )
 
    # 2. For each model: answer, LLM-Judge score, Human score
    for model in MODEL_ORDER:
        sub = llm_human_score[llm_human_score["Model"] == model][
            ["ID", "Model_Answer", "Judge_Total", "Human_Correct"]
        ].rename(columns={
            "Model_Answer":  f"Réponse — {model}",
            "Judge_Total":   f"LLM-Judge /7 — {model}",
            "Human_Correct": f"Humain ✓ — {model}",
        })
        base = base.merge(sub, on="ID", how="left")
 
    # 3. BERTScore per model (from df_scores)
    if "ID" in df_scores.columns:
        for model in MODEL_ORDER:
            bert_sub = df_scores[df_scores["modele"] == model][
                ["ID", "bert_score_f1"]
            ].rename(columns={"bert_score_f1": f"BERT — {model}"})
            base = base.merge(bert_sub, on="ID", how="left")
 
    # ── Filters ───────────────────────────────────────────────────
    fc1, fc2 = st.columns(2)
    with fc1:
        cats = ["Toutes"] + sorted(base["Catégorie"].dropna().unique().tolist())
        sel_cat = st.selectbox("Filtrer par catégorie", cats, key="exp_cat")
    with fc2:
        nivs = ["Tous"] + sorted(base["Niveau"].dropna().unique().tolist())
        sel_niv = st.selectbox("Filtrer par niveau", nivs, key="exp_niv")
 
    view = base.copy()
    if sel_cat != "Toutes":
        view = view[view["Catégorie"] == sel_cat]
    if sel_niv != "Tous":
        view = view[view["Niveau"] == sel_niv]
 
    st.caption(f"{len(view)} question(s) affichée(s) sur {len(base)}")
 
    # ── Column config ─────────────────────────────────────────────
    col_cfg = {
        "ID":               st.column_config.TextColumn("ID",     width="small"),
        "Question":         st.column_config.TextColumn("Question", width="large"),
        "Réponse_correcte": st.column_config.TextColumn("Réf.",   width="medium"),
        "Catégorie":        st.column_config.TextColumn("Catégorie", width="medium"),
        "Niveau":           st.column_config.TextColumn("Niveau", width="small"),
    }
    for model in MODEL_ORDER:
        short = model.split("-")[0]   # "DeepSeek", "gemma", "mistral"
        col_cfg[f"Réponse — {model}"]    = st.column_config.TextColumn(
            f"Réponse {short}", width="large")
        col_cfg[f"LLM-Judge /7 — {model}"] = st.column_config.NumberColumn(
            f"LLM /7 {short}", format="%.0f", width="small")
        col_cfg[f"Humain ✓ — {model}"]  = st.column_config.NumberColumn(
            f"Humain {short}", format="%.0f", width="small")
        if f"BERT — {model}" in view.columns:
            col_cfg[f"BERT — {model}"]  = st.column_config.NumberColumn(
                f"BERT {short}", format="%.3f", width="small")
 
    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
        height=520,
        column_config=col_cfg,
    )
 
    # ── Download ──────────────────────────────────────────────────
    st.download_button(
        label="⬇️ Télécharger ce tableau (CSV)",
        data=view.to_csv(index=False).encode("utf-8"),
        file_name="detail_questions_scores.csv",
        mime="text/csv",
    )