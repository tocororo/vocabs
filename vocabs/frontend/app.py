import streamlit as st
import gettext
from vocabs.backend.neo4voc.connection import Connection

gettext.bindtextdomain("messages", "vocabs/frontend/locales")
gettext.textdomain("messages")

language = st.sidebar.selectbox(' ', ['es', 'en'])

translations = gettext.translation("messages", localedir="vocabs/frontend/locales", languages=[language])

translations.install()

_ = translations.gettext

@st.dialog('ERROR')
def dialog_error(e):
    st.write(e)
@st.dialog('Info')
def dialog_info(info):
    st.write(info)

try:
    st.title(_('Sceiba Vocabularies Service'))
    st.subheader('System for vocabularies')

    st.text_area(_("Hello streamlit"))

    connection = Connection()
    records = connection.database_all_info()
    st.write(records)
    connection.close()
    
except Exception as e:
    dialog_error(e)