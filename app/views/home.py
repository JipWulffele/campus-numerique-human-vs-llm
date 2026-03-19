import streamlit as st


st.title('LLMs : creativity and cultural bias')

st.header("The Divergent Association Task")
st.markdown("source : https://www.datcreativity.com/")

st.markdown("""
            ```
            **Instructions:**\n
            Please enter 10 words that are as different from each other as possible, in all meanings and uses of the words.

            **Rules:**
            1. Only single words in English.
            2. Only nouns (e.g., things, objects, concepts).
            3. No proper nouns (e.g., no specific people or places).
            4. No specialised vocabulary (e.g., no technical terms).
            5. Think of the words on your own (e.g., do not just look at objects in your surroundings).
            ```
            """)

st.header("How to measure creativity and originality ?")

st.subheader("Creativity : average pairwise cosine similairity")
st.image("./data/cosine_explication.png")

st.subheader("Originality : frequency of rare words")
st.markdown("""
The originality of your list of words is measured by checking how many of them appear in the most frequently used words in French or English.  
Each dataset contains the 10,000 most common words.  
The larger the subset of common words you consider, the harder it becomes to achieve a high originality score.
""")

st.header("Cultural bias")
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

