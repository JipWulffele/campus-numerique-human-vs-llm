import pandas as pd
from unidecode import unidecode
import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

#-------------------------------------------------------
#load dictionnary
#-------------------------------------------------------
df_french = pd.read_csv("data/french_top_10000.csv",header=1,skipinitialspace=True)
df_french = df_french[["lemme"]]
df_french['lemme'] = df_french['lemme'].apply(lambda x: unidecode(x) if isinstance(x, str) else '')
df_english = pd.read_csv("data/english_top_10000.txt", header= None, names=["words"])
df_ten_words = pd.read_csv("data/words10_cleaned.csv", )
df_ten_words.columns = df_ten_words.columns.str.strip()
for col in df_ten_words.select_dtypes(include='object'):
    df_ten_words[col] = (
        df_ten_words[col]
        .astype(str)
        .str.strip()
        .apply(lambda x: unidecode(x) if isinstance(x, str) else '')
        .str.lower()
    )

#-------------------------------------------------------
# utility fonctions:
#-------------------------------------------------------
def prepare_lexicons(limit):
    """
    Prépare les sets de mots les plus fréquents à partir des datasets.
    
    Arguments:
        X_english: nombre de mots à prendre pour English
        X_usa: nombre de mots à prendre pour USA
        X_french: nombre de mots à prendre pour French
    
    Retour:
        dict de sets { "english": set(...), "usa": set(...), "french": set(...) }
    """
    lex_dict = {
        "english": set(df_english["words"].head(limit)),
        "french": set(df_french["lemme"].head(limit))
    }
    return lex_dict

def compute_scores_all(row, lex_dict):
    words = row[[str(i) for i in range(1, 11)]].tolist()
    lang = str(row["language"]).lower()
    
    if lang == "english":
        score_english = sum(1 for w in words if w in lex_dict["english"])
        return score_english

    elif lang == "french":
        score_french = sum(1 for w in words if w in lex_dict["french"])
        return score_french
    
    else:
        # autre langue
        print("error lang")
        return None

def compute_word_scores(df, limit=10000):
    """
    Pour chaque ligne du DataFrame `df` contenant 10 mots et une colonne 'language',
    calcule les scores par lexique (français / anglais / US) selon la langue,
    et retourne le DataFrame enrichi avec une colonne 'score' (ou plusieurs scores si nécessaire).
    """
    df = df.copy()
    # Préparer les lexiques
    lex_dict = prepare_lexicons(limit=limit)

    # calculer les scores pour toutes les lignes
    df_scores = df.apply(lambda row: compute_scores_all(row, lex_dict), axis=1)

    # ajouter les colonnes au DataFrame original
    df['score'] = 10 - df_scores

    return df

def clean_words(text):
    words = text.split()
    
    words = [
        unidecode(word.strip().lower())
        for word in words
        if word.strip() != ""
    ]
    
    return words

def words_to_df(words, language="french"):
    if len(words) != 10:
        return None
    
    data = {str(i+1): words[i] for i in range(10)}
    data["language"] = language
    
    return pd.DataFrame([data])

#-------------------------------------------------------
# Choix utilisateur
#-------------------------------------------------------

# Choix langue pour visualisation
language_options = ["english", "french", "both"]
selected_language = st.selectbox("Filtrer par langue :", language_options, index=2)  # 'both' par défaut


# Gestion choix limit
animate = st.checkbox("Activer animation de la variation de la limite")

if animate:
    # limites pour animation : 100 à 10000 par pas de 100
    animation_limits = list(range(100, 10001, 100))

else:
    # Slider pour choisir la limite de mots
    selected_limit = st.slider(
        "Choisissez la limite de mots pour le lexique :",  # titre
        min_value=100,
        max_value=10000,
        value=2000,          # valeur par défaut
        step=100             # incréments
    )

#-------------------------------------------------------
# cas animation
#-------------------------------------------------------
if animate:
    # calculer les scores pour toutes les limites
    dfs = []
    for lim in animation_limits:
        df_tmp = compute_word_scores(df_ten_words, limit=lim)
        df_tmp["limit"] = lim
        dfs.append(df_tmp)
    df_anim = pd.concat(dfs, ignore_index=True)
    
    # Filtrer selon la langue
    if selected_language != "both":
        df_anim = df_anim[df_anim['language'] == selected_language]
    
    # Décalage pour both
    if selected_language == "both":
        df_anim['model_num'] = df_anim['model'].astype('category').cat.codes
        offset_map = {'english': -0.15, 'french': 0.15}
        df_anim['x_offset'] = df_anim['model_num'] + df_anim['language'].map(offset_map)
        x_col = 'x_offset'
        tickvals = df_anim['model_num'].unique()
        ticktext = df_anim['model'].unique()
    else:
        x_col = 'model'
        tickvals = None
        ticktext = None
    
    fig = px.scatter(
        df_anim,
        x=x_col,
        y='score',
        color='language',
        size='score',
        hover_data=df_anim.columns,
        animation_frame='limit',
        size_max=20,
        color_discrete_map={'english':'blue', 'french':'green'},
        title="Évolution des scores selon la limite"
    )
    
    # Ajuster axes
    fig.update_layout(
        yaxis=dict(range=[0,11]),
        xaxis=dict(title='Modèle', tickmode='array', tickvals=tickvals, ticktext=ticktext),
        legend_title='Langue'
    )
    
    st.plotly_chart(fig, use_container_width=True)

else:

    df_scores_all = compute_word_scores(df_ten_words, selected_limit)
    #-------------------------------------------------------
    # nuage de points
    #-------------------------------------------------------

    # Filtrer le DataFrame selon la langue choisie
    if selected_language == "both":
        df_filtered = df_scores_all.copy()
        
        # Transformer model en codes numériques pour décaler les points
        df_filtered['model_num'] = df_filtered['model'].astype('category').cat.codes
        
        # Décalage gauche/droite selon la langue
        offset_map = {'english': -0.15, 'french': 0.15}
        df_filtered['x_offset'] = df_filtered['model_num'] + df_filtered['language'].map(offset_map)
        
        # Scatter interactif
        fig_scatter = px.scatter(
            df_filtered,
            x='x_offset',
            y='score',
            color='language',
            size='score',
            hover_data=df_filtered.columns,
            title=f'Scores des mots pour limite = {selected_limit}',
            size_max=20,
            color_discrete_map={'english':'blue', 'french':'green'}
        )

        # Ajuster l'axe X pour afficher les noms de modèles
        fig_scatter.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=df_filtered['model_num'].unique(),
                ticktext=df_filtered['model'].unique(),
                title='Modèle'
            ),
            yaxis=dict(range=[0, 11]),
            legend_title='Langue'
        )

    else:
        df_filtered = df_scores_all[df_scores_all['language'] == selected_language]

        fig_scatter = px.scatter(
            df_filtered,
            x='model',              # axe X : type de modèle
            y='score',            # axe Y : score
            color='language',       # couleur selon la langue
            size='score',          # taille selon quantité
            hover_data=df_filtered.columns,  # toutes les infos au survol
            title=f'Scores des mots pour limite = {selected_limit}',
            size_max=20,             # taille max des points
            color_discrete_map={'english':'blue', 'french':'green'}
        )

        # Ajustements des axes et layout
        fig_scatter.update_layout(
            xaxis_title='Modèle',
            yaxis=dict(range=[0, 11]),
            legend_title='Langue',
        )

    # Affichage interactif dans Streamlit
    st.plotly_chart(fig_scatter, use_container_width=True)

    #-------------------------------------------------------
    # affichage boite à moustache répartition des scores
    #-------------------------------------------------------
    fig = px.box(
        df_filtered,
        x="score",
        y="model",
        color="language",
        color_discrete_map={'english':'blue', 'french':'green'},
        points="all",          # affiche les points individuels (comme stripplot)
        hover_data=df_filtered.columns,  # on peut voir toutes les infos au survol
        title="Distribution des scores par modèle et langue"
    )

    # Options pour améliorer l'affichage
    fig.update_traces(boxpoints="all", jitter=0.5, pointpos=0)
    fig.update_layout(
        yaxis=dict(range=[0, 11]),
        xaxis=dict(title="Score d'originalité"),
        boxmode="group"  # pour grouper par model/langue
    )

    # Affichage dans Streamlit
    st.plotly_chart(fig, use_container_width=True)