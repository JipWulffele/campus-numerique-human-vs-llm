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
# ADD EXPLICATION DILETTA

