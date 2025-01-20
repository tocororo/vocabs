import streamlit as st
from vocabs.backend.neo4voc.connection import Connection
from vocabs.backend.neo4voc.neosemantics import NeoSemantics

from vocabs.frontend.locales.language import Language
from vocabs.frontend.pages.menu import Menu

class App:

    def __init__(self):
        
        # Contains the general structure of the application
        # - menu block or side menu where functions will appear according to the user and the roles, for now only admin and users who do not need authentication
        # - page block, contains the main functionality of the application. Also authentication, data import, data management and other future functions

        # blocks

        # Initialize st.session_state.role to None
        if "role" not in st.session_state:
            st.session_state.role = 'admin'

        # Retrieve the role from Session State to initialize the widget
        st.session_state._role = st.session_state.role
        
        # ********************************
        # Shows the application navigation, 
        # also contains the logic according to the user role
        # ********************************
        m = Menu()
        m.menu()

        # ********************************
        # creates the variable `_` that contains the translation documents.
        # ********************************
        l = Language()
        self._ = l.language()

    @st.dialog('ERROR')
    def dialog_error(e:Exception):
        st.write(e)
    @st.dialog('Info')
    def dialog_info(info):
        st.write(info)

# ********************************
# The `_page` variable is saved for each page, 
# this is so that the translation selection works between multiple pages.
# ********************************
app = App()
st.Page(app, title='Sceiba')
st.session_state._page = 'app'