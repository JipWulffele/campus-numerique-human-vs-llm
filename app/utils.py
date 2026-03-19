import pandas as pd
from unidecode import unidecode

df_french = pd.read_csv("data/french_top_10000.csv",header=1,skipinitialspace=True)
df_french = df_french[["lemme"]]
df_french['lemme'] = df_french['lemme'].apply(lambda x: unidecode(x) if isinstance(x, str) else '')
df_english = pd.read_csv("data/english_top_10000.txt", header= None, names=["words"])

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