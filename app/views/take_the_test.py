import pandas as pd
from unidecode import unidecode
import streamlit as st
from gensim.models import KeyedVectors
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from utils import clean_words, compute_word_scores, words_to_df

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

# Choix langue
is_english = st.checkbox("Anglais 🇬🇧")

# Choix 10 mots
user_input = st.text_input(
    "Entrez 10 mots séparés par des espaces :",
    placeholder="ex: chat chien maison voiture arbre ..."
)

language = "english" if is_english else "french"

#-------------------------------------------------------
# Functions for cosine similairity
#-------------------------------------------------------

def get_embedding(word, lang):
    if not isinstance(word, str) or word.strip() == "":
        return np.zeros(300)

    model = model_fr if lang.strip() == "french" else model_en

    try:
        return model[word]
    except KeyError:
        return np.zeros(300)
    
def calculate_avg_cosine(vector_list):
    similarities = cosine_similarity(vector_list)
    upper_triangle = similarities[np.triu_indices_from(similarities, k=1)]
    return np.mean(upper_triangle)

def scale_score(score, n_words=10):
    max_score = 1 # all words the same
    min_score = -1/(n_words-1) # -0.111 for 10 words

    score_scaled = 0 + (score-max_score)*((0-10)/(max_score -min_score))
    score_scaled = np.clip(score_scaled, 0, 10) # cheat a bit... this should not be needed
    return int(np.round(score_scaled))

def get_ranking(cosine_score):
    df_cosine = pd.read_csv('./data/cosine_similairity_neigbor.csv', index_col=0)

    df_llm = df_cosine[df_cosine['model'] != 'Human']
    df_human = df_cosine[df_cosine['model'] == 'Human']

    ranking_llm = (df_llm['avg_cosine'] > cosine_score).mean() * 100
    ranking_human = (df_human['avg_cosine'] > cosine_score).mean() * 100

    return ranking_llm, ranking_human
            
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
        df_humans_lim = df_humans[
            (df_humans["limit"] == selected_limit) & 
            (df_humans["language"] == language)
            ]
        df_ai_lim = df_ai[
            (df_ai["limit"] == selected_limit) &
            (df_ai["language"] == language)
            ]
        df_ai_grouped = df_ai_lim.groupby("model", as_index=False)["score"].mean()

        def percentile_rank(user_score, scores):
            return (scores < user_score).mean() * 100

        user_score = df_result["score"].iloc[0]

        # calcul %
        pct_humans = percentile_rank(user_score, df_humans_lim["score"])
        pct_ai = percentile_rank(user_score, df_ai_grouped["score"])

        # Calculate cosine similairity
        try :
            model_en = KeyedVectors.load("./models/wiki.multi.en.kv", mmap='r')
            model_fr = KeyedVectors.load("./models/wiki.multi.fr.kv", mmap='r')

            vector_list = [get_embedding(word, language) for word in words]
            cosine_score = calculate_avg_cosine(vector_list)
            cosine_scaled = scale_score(cosine_score)
            ranking_llm, ranking_human = get_ranking(cosine_score)
        except : 
            print("Embeddings model not available !!!")
            cosine_scaled = None
            ranking_llm, ranking_human = None, None

        if pct_ai > 50 : 
            if is_english: 
                st.success(f"""
                🎯 Ton score de orginalité : **{user_score}/10**

                🤖 Meilleur que **{pct_ai:.1f}% des IA**  
                """)
                st.balloons()
            else:
                st.success(f"""
                🎯 Ton score de orginalité : **{user_score}/10**

                🤖 Meilleur que **{pct_ai:.1f}% des IA**  
                🧑 Meilleur que **{pct_humans:.1f}% des humains**  
                """)
                st.balloons()
        else: 
            if is_english:
                st.error(f"""
                🎯 Ton score de orginalité : **{user_score}/10**

                🤖 Meilleur que **{pct_ai:.1f}% des IA**  
                """)
            else:
                st.error(f"""
                🎯 Ton score de orginalité : **{user_score}/10**

                🤖 Meilleur que **{pct_ai:.1f}% des IA**  
                🧑 Meilleur que **{pct_humans:.1f}% des humains** 
                """)

        if ranking_llm and ranking_llm > 50 :
            if is_english:
                st.success(f"""
                🎯 Ton score de creativité : **{cosine_scaled}/10**

                🤖 Meilleur que **{ranking_llm:.1f}% des IA**  

                """)
                st.balloons()
            else:
                st.success(f"""
                🎯 Ton score de creativité : **{cosine_scaled}/10**

                🤖 Meilleur que **{ranking_llm:.1f}% des IA**  
                🧑 Meilleur que **{ranking_human:.1f}% des humains**

                """)
                st.balloons()
        elif ranking_llm is not None: 
            if is_english:
                st.error(f"""
                🎯 Ton score de creativité : **{cosine_scaled}/10**

                🤖 Meilleur que **{ranking_llm:.1f}% des IA**  
                """)
            else:
                st.error(f"""
                🎯 Ton score de creativité : **{cosine_scaled}/10**

                🤖 Meilleur que **{ranking_llm:.1f}% des IA**  
                🧑 Meilleur que **{ranking_human:.1f}% des humains**
                """)

        else: 
            st.warning(f"""
            Creativity score not available.\n
            Please download embedding models as explained in the README.
            """)