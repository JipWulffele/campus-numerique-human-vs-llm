import pandas as pd
from unidecode import unidecode
import streamlit as st

from views.rare_mots import prepare_lexicons, compute_scores_all, compute_word_scores, clean_words, words_to_df

#-------------------------------------------------------
# load dictionnary
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
# preparation des données:
#-------------------------------------------------------

limits = [100, 500, 1000, 2000, 5000, 7500, 10000]

# calculer les scores pour toutes les limites
dfs = []
for lim in limits:
    df_tmp = compute_word_scores(df_ten_words, limit=lim)
    df_tmp["limit"] = lim
    dfs.append(df_tmp)
df_ten_words_res = pd.concat(dfs, ignore_index=True)

# sépare le dataset entre humain et ia
human_mask = df_ten_words_res["model"].str.contains("human", case=False)

df_humans = df_ten_words_res[human_mask]
df_ai = df_ten_words_res[~human_mask]

#-------------------------------------------------------
# Choix utilsateur
#-------------------------------------------------------
# choix difficulté
difficulty_map = {
    "Facile (100 mots)": 100,
    "Moyen (500 mots)": 500,
    "Intermédiaire (1000 mots)": 1000,
    "Avancé (2000 mots)": 2000,
    "Difficile (5000 mots)": 5000,
    "Expert (7500 mots)": 7500,
    "Impossible (10000 mots)": 10000
}

selected_difficulty = st.selectbox(
    "Choisissez la difficulté (taille du dictionnaire) :",
    list(difficulty_map.keys()),
    index=3  # par défaut "Avancé"
)

# récupérer la limite associée
selected_limit = difficulty_map[selected_difficulty]

#Choix langue
is_english = st.checkbox("Anglais 🇬🇧")

#Choix 10 mots
user_input = st.text_input(
    "Entrez 10 mots séparés par des espaces :",
    placeholder="ex: chat chien maison voiture arbre ..."
)

language = "english" if is_english else "french"

#-------------------------------------------------------
# Calcul du score
#-------------------------------------------------------

if user_input:
    words = clean_words(user_input)
    
    if len(words) != 10:
        st.error(f"Veuillez entrer exactement 10 mots. Il manque actuellement {10 - len(words)} mots")
    else:
        # détecter les doublons
        duplicates = [word for word in set(words) if words.count(word) > 1]
        if duplicates:
            st.warning(f"⚠️ Attention, mots en double détectés : {', '.join(duplicates)}")

        df_user = words_to_df(words, language=language) 
        
        # calcul du score
        df_result = compute_word_scores(df_user, limit=selected_limit)
        
        #-------------------------------------------------------
        # Comparaison avec resultat dataset
        #-------------------------------------------------------
        df_humans_lim = df_humans[df_humans["limit"] == selected_limit]
        df_ai_lim = df_ai[df_ai["limit"] == selected_limit]
        df_ai_grouped = df_ai_lim.groupby("model", as_index=False)["score"].mean()

        def percentile_rank(user_score, scores):
            return (scores < user_score).mean() * 100

        user_score = df_result["score"].iloc[0]

        # calcul %
        pct_humans = percentile_rank(user_score, df_humans_lim["score"])
        pct_ai = percentile_rank(user_score, df_ai_grouped["score"])

        st.success(f"""
        🎯 Ton score : **{user_score}/10**

        🤖 Meilleur que **{pct_ai:.1f}% des IA**  
        🧑 Meilleur que **{pct_humans:.1f}% des humains**
        """)