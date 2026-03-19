import pandas as pd
from unidecode import unidecode
import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

from utils import compute_word_scores

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
# Choix utilisateur
#-------------------------------------------------------

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
    
    df_anim_plot = (
        df_anim
        .groupby(['model', 'score', 'language', 'limit'], as_index=False)
        .size()
        .rename(columns={'size': 'count'})
    )
 
    df_anim_plot['id'] = df_anim_plot['model'] + '_' + df_anim_plot['score'].astype(str) + '_' + df_anim_plot['language']
    
    # pour corriger post aggregation l'ordre
    df_anim_plot['limit'] = df_anim_plot['limit'].astype(int)
    df_anim_plot = df_anim_plot.sort_values('limit').reset_index(drop=True)
        
    df_anim_plot['model_num'] = df_anim_plot['model'].astype('category').cat.codes
    offset_map = {'english': -0.15, 'french': 0.15}
    df_anim_plot['x_offset'] = df_anim_plot['model_num'] + df_anim_plot['language'].map(offset_map)
    x_col = 'x_offset'
    tickvals = df_anim_plot['model_num'].unique()
    ticktext = df_anim_plot['model'].unique()

    
    fig = px.scatter(
        df_anim_plot,
        x=x_col,
        y='score',
        color='language',
        size='count',
        hover_data=df_anim_plot.columns,
        animation_frame='limit',
        animation_group='id',
        size_max=30,
        color_discrete_map={'english':'#1f77b4', 'french':'#2ca02c'},
        title="Évolution des scores selon la limite"
    )
    
    # Ajuster axes
    fig.update_layout(
        yaxis=dict(range=[-1,11]),
        xaxis=dict(title='Modèle', tickmode='array', tickvals=tickvals, ticktext=ticktext),
        legend_title='Langue'
    )
    
    st.plotly_chart(fig, use_container_width=True)

#-------------------------------------------------------
# cas sans animation
#-------------------------------------------------------
else:
    color_option = st.radio("Color by:",["Country", "Size"])
    
    df_scores_all = compute_word_scores(df_ten_words, selected_limit)

    df_scores_all['country'] = df_scores_all['model'].map({
        'gpt_53_chat': 'US',
        'grok_41': 'US',
        'sonnet_46': 'US',
        'deepseek_v32': 'China',
        'gemini_3': 'US',
        'gwen_35_plus': 'China',
        'human': 'N/A',
        'mistral-medium': 'France',
        'mistral-large-2402': 'France',
        'mistral-small-2402': 'France',
        'trinity_mini': 'US',
        'glm_45_air': 'China'
    })
    df_scores_all['model_size'] = df_scores_all['model'].map({
        'gpt_53_chat': 'XL',
        'grok_41': 'XL',
        'sonnet_46': 'XL',
        'deepseek_v32': 'XL',
        'gemini_3': 'XL',
        'gwen_35_plus': 'XL',
        'human': 'N/A',
        'mistral-medium': 'M',
        'mistral-large-2402': 'L',
        'mistral-small-2402': 'S',
        'trinity_mini': 'S',
        'glm_45_air': 'L'
    })

    # Set up colors----------------------------------------------
    color_map_country = {
        "N/A": "#54478C",        
        "US": "#EFEA5A",        
        "China": "#F1C453", 
        "France": "#f29e4c",       
    }
    color_map_size = {
        "N/A": "#54478C",       
        "S": "#b9e769",         
        "M": "#efea5a",     
        "L": "#f1c453",
        "XL": "#f29e4c"     
    }

    if color_option == "Country":
        color_col = "country"
        color_map = color_map_country
    else:
        color_col = "model_size"
        color_map = color_map_size


    # Créer deux colonnes côte à côte
    col1, col2 = st.columns(2)

    #-----------------------------
    # Graphe French
    #-----------------------------
    df_french_plot = df_scores_all[df_scores_all['language'] == 'french']
    df_french_plot = (
        df_french_plot
        .groupby(['model', 'score', 'country', 'model_size'], as_index=False)
        .size()
        .rename(columns={'size': 'count'})
    )

    df_french_plot = df_french_plot.fillna("N/A")

    fig_french = px.scatter(
        df_french_plot,
        x='model',
        y='score',
        size='count',
        hover_data=df_french_plot.columns,
        title=f'French - Scores pour limite = {selected_limit}',
        size_max=20,
        color=color_col,
        color_discrete_map=color_map
    )
    fig_french.update_layout(
        yaxis=dict(range=[-1, 11]),
        xaxis_title='Modèle'
    )

    col1.plotly_chart(fig_french, use_container_width=True)

    #-----------------------------
    # Graphe English
    #-----------------------------
    df_english_plot = df_scores_all[df_scores_all['language'] == 'english']
    df_english_plot = (
        df_english_plot
        .groupby(['model', 'score', 'country', 'model_size'], as_index=False)
        .size()
        .rename(columns={'size': 'count'})
    )

    fig_english = px.scatter(
        df_english_plot,
        x='model',
        y='score',
        size='count',
        hover_data=df_english_plot.columns,
        title=f'English - Scores pour limite = {selected_limit}',
        size_max=20,
        color=color_col,
        color_discrete_map=color_map
    )
    fig_english.update_layout(
        yaxis=dict(range=[-1, 11]),
        xaxis_title='Modèle'
    )

    col2.plotly_chart(fig_english, use_container_width=True)


