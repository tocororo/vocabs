import streamlit as st
import gettext

gettext.bindtextdomain("messages", "vocabs/frontend/locales")
gettext.textdomain("messages")

language = st.sidebar.selectbox(' ', ['es', 'en'])

translations = gettext.translation("messages", localedir="vocabs/frontend/locales", languages=[language])

translations.install()


_ = translations.gettext


st.write(_('This is a translatable string.'))
st.write(_('This is a text'))

st.title(_('Sceiba Vocabularies Service'))
st.subheader('System for vocabularies')

st.text_area(_("Hello streamlit"))
