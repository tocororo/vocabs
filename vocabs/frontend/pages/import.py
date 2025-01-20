from langchain_huggingface import HuggingFaceEmbeddings
import streamlit as st
from vocabs.backend.neo4voc.neo4_vector_index import access_neo_index, create_neo_index, get_indexes
from vocabs.frontend.locales.language import Language
from vocabs.backend.neo4voc.connection import Connection
from vocabs.backend.neo4voc.neosemantics import NeoSemantics

from vocabs.frontend.pages.menu import Menu

class Import:

    def __init__(self):
        # ********************************
        # The `_page` variable is saved for each page, 
        # this is so that the translation selection works between multiple pages.
        # ********************************
        st.session_state._page = 'import'
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
        _ = l.language()
        # pre configuration
        # 
        neo = NeoSemantics()
        config, constraint =neo.create_constraint_and_default_config()
        try:
            st.title(_('Sceiba Vocabularies Service'))
            st.subheader('System for vocabularies')

            uploaded_file = st.file_uploader("Choose a file", type=['ttl', 'xml'])
            if uploaded_file is not None:
                st.write(uploaded_file.name)
                st.write(uploaded_file.type)
                st.write(uploaded_file._file_urls.upload_url)
                connection = Connection()
                
                records = neo.import_data(
                    path= uploaded_file.getvalue(),#'file:///home/edel/Projects/PhD/unesco-thesaurus.ttl', 
                    format= uploaded_file.type,#'ttl',
                    tags= {
                        'identifier': 'uri',
                        'id_value': 'unesco.org',
                        'labels': 'Unesco'
                    }
                    )
                connection.close()
            
        except Exception as e:
            st.toast(e, icon=':material/warning:')

i = Import()
st.Page(i, title="Sceiba/Import")