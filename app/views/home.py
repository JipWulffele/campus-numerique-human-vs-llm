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

st.subheader("Orginality : frequency of rare words")
# ADD EXPLICATION LAETITIA


st.header("Cultural bias")
# ADD EXPLICATION DILETTA

