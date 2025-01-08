import streamlit as st
import gettext

class Language:
    current_page = ''
    values = ['es', 'en']
    def __init__(self):
        pass

    def show_languages(self):
        self.language_in_session()
        
        default_ix = self.values.index(st.session_state.language)

        # if self.current_page != st.session_state._page:
        self.current_page = st.session_state._page
        st.session_state.language = st.sidebar.selectbox(
            label='Language', 
            label_visibility='collapsed', 
            options=self.values,
            index=default_ix, 
            placeholder = "Choose an option")
        # else:
        #     st.session_state.language = st.sidebar.selectbox(
        #         label='Language', 
        #         label_visibility='collapsed', 
        #         options=self.values,
        #         placeholder = "Choose an option")

    def language(self):
        self.language_in_session()

        gettext.bindtextdomain("messages", "vocabs/frontend/locales")
        gettext.textdomain("messages")

        translations = gettext.translation("messages", localedir="vocabs/frontend/locales", languages=[st.session_state.language])

        translations.install()

        return translations.gettext
        
    def language_in_session(self):
        if "language" not in st.session_state:
            st.session_state.language = 'es'
        st.session_state._language = st.session_state.language

        if "_page" not in st.session_state:
            st.session_state._page = 'default'