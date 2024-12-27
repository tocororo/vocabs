import streamlit as st
from vocabs.backend.neo4voc.connection import Connection
from vocabs.backend.neo4voc.neosemantics import NeoSemantics

from vocabs.frontend.locales.languaje import *

language = st.sidebar.selectbox(' ', ['es', 'en'])

translations = gettext.translation("messages", localedir="vocabs/frontend/locales", languages=[language])

translations.install()

_ = translations.gettext

@st.dialog('ERROR')
def dialog_error(e:Exception):
    st.write(e)
@st.dialog('Info')
def dialog_info(info):
    st.write(info)

try:
    st.title(_('Sceiba Vocabularies Service'))
    st.subheader('System for vocabularies')

    st.text_area(_("Hello streamlit"))

    connection = Connection()
    neo = NeoSemantics()
    records = neo.import_data(
        path= 'file:///home/edel/Projects/PhD/unesco-thesaurus.ttl', 
        format= 'ttl'
        )
    neo.add_labels_to_nodes(property='uri', property_value='vocabularies.unesco.org', labels='Unesco')
    connection.close()
    
except Exception as e:
    dialog_error(e)