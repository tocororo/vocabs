import streamlit as st
from vocabs.frontend.locales.language import Language
from vocabs.backend.neo4voc.connection import Connection
from vocabs.backend.neo4voc.neosemantics import NeoSemantics

from vocabs.frontend.menu import Menu

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

        try:
            st.title(_('Sceiba Vocabularies Service'))
            st.subheader('System for vocabularies')

            uploaded_file = st.file_uploader("Choose a file", type=['ttl', 'xml'])
            if uploaded_file is not None:
                st.write(uploaded_file.name)
                st.write(uploaded_file.type)
                st.write(uploaded_file._file_urls.upload_url)
                connection = Connection()
                neo = NeoSemantics()
                records = neo.import_data(
                    path= uploaded_file.getvalue(),#'file:///home/edel/Projects/PhD/unesco-thesaurus.ttl', 
                    format= uploaded_file.type,#'ttl',
                    tags= {
                        'identifier': 'uri',
                        'id_value': 'vocabularies.unesco.org',
                        'labels': 'Unesco'
                    }
                    )
                # neo.add_labels_to_nodes(property='uri', property_value='vocabularies.unesco.org', labels='Unesco')
                connection.close()
            # endif
            
        except Exception as e:
            st.toast(e, icon=':material/warning:')
            # dialog_error(e)

i = Import()
st.Page(i, title="Sceiba/Import")