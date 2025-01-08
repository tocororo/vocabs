import streamlit as st

from vocabs.frontend.locales.language import Language
from vocabs.frontend.menu import Menu

class Home:

    def __init__(self):
        
        # ********************************
        # Shows the application navigation, 
        # also contains the logic according to the user role
        # ********************************
        m = Menu()
        m.menu_with_redirect()
        # ********************************
        # creates the variable `_` that contains the translation documents.
        # ********************************
        l = Language()
        self._ = l.language()

        try:
            st.title(self._('Sceiba Vocabularies Service'))
            st.subheader('System for vocabularies')

            st.text_area(self._("Hello streamlit"))
            
        except Exception as e:
            st.toast(e, icon=':material/warning:')
            st.exception(e)

h = Home()
# ********************************
# The `_page` variable is saved for each page, 
# this is so that the translation selection works between multiple pages.
# ********************************
st.session_state._page = 'home'
st.Page(h, title="Sceiba/Home")