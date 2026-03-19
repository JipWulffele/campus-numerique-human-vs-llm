import streamlit as st

# Set wide layout
st.set_page_config(layout="wide")

# 1. Define the pages
home_page = st.Page("views/home.py", title="Home", icon=":material/home:", default=True)
<<<<<<< Updated upstream
take_the_test = st.Page("views/take_the_test.py", title="Take the test", icon=":material/quiz:")
creativity_page = st.Page("views/creativity.py", title="Creativity", icon=":material/lightbulb:")
rare_mots_page = st.Page("views/rare_mots.py", title="Rare mots", icon=":material/auto_stories:")
culture_page = st.Page("views/culture.py", title="Culture", icon=":material/public:")

# 2. Initialize Navigation
pg = st.navigation({
    "Main": [home_page, take_the_test],
    "Results": [creativity_page, rare_mots_page, culture_page]
=======
take_the_test = st.Page("views/take_the_test.py", title="Take the test", icon=":material/bar_chart:")
creativity_page = st.Page("views/creativity.py", title="Creativity", icon=":material/bar_chart:")
rare_mots_page = st.Page("views/rare_mots.py", title="Rare mots", icon=":material/settings:")
culture_page = st.Page("views/culture.py", title="Culture", icon=":material/settings:")
model_page = st.Page("views/model.py", title="Model", icon=":material/settings:")


# 2. Initialize Navigation
pg = st.navigation({
    "Main": [home_page],
    "Tools": [take_the_test, creativity_page, rare_mots_page, culture_page, model_page]
>>>>>>> Stashed changes
})

# 3. Run the navigation
pg.run()
