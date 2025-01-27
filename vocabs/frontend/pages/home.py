from langchain_huggingface import HuggingFaceEmbeddings
import streamlit as st

from vocabs.backend.neo4voc.neo4_vector_index import Vector
from vocabs.frontend.locales.language import Language
from vocabs.frontend.pages.menu import Menu

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
        _ = l.language()

        try:
            with st.container(border=True):
                st.title(_('Sceiba Vocabularies Service'))
                vector = Vector()
                # Get index names from the database.
                results= vector.get_index_names()
                # Format the result for a better user interface
                index_names = []
                for index in results:
                    index_names.append(str(index[0]).replace('_',' ').upper())
                
                selected_index= st.selectbox(_('Chosse a Vocabulary'), options=index_names)
                text= st.text_area(_('Keywords or abstract'), max_chars=250)
                search= st.button(_('Search'))
            
            if search:
                if text != '':
                    # get access to the index selected
                    index = str(selected_index).replace(' ','_').lower()
                    result= vector.access_neo_index(index, query=text, k=5)
                    print('index loaded')
                    # embeddings_provider = HuggingFaceEmbeddings(model_name= model_name)
                    # result = vector.similar_from_index(query=text,k=5)
                    st.write(result)
                else: st.toast('Please fill the form',icon=':material/warning:')

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