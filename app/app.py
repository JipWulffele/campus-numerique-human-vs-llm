import streamlit as st

# Set wide layout
st.set_page_config(layout="wide")

# 1. Define the pages
home_page = st.Page("views/home.py", title="Home", icon=":material/home:", default=True)
creativity_page = st.Page("views/creativity.py", title="Creativity", icon=":material/bar_chart:")
rare_mots_page = st.Page("views/rare_mots.py", title="Rare mots", icon=":material/settings:")
culture_page = st.Page("views/culture.py", title="Culture", icon=":material/settings:")

# 2. Initialize Navigation
pg = st.navigation({
    "Main": [home_page],
    "Tools": [creativity_page, rare_mots_page, culture_page]
})

# 3. Run the navigation
pg.run()