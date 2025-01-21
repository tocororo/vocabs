from langchain_huggingface import HuggingFaceEmbeddings
import streamlit as st

from vocabs.backend.neo4voc.neo4_vector_index import access_neo_index, create_neo_index, get_indexes, set_node_properties
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
        self._ = l.language()

        try:
            st.title(self._('Sceiba Vocabularies Service'))
            st.subheader('System for vocabularies')
            
        except Exception as e:
            st.toast(e, icon=':material/warning:')
            st.exception(e)

        
        # 1. embeddings provider
        embeddings_provider = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")
        # 2. create the index
        create_neo_index(
            vector_name="unesco_all_MiniLM_L12_v2",
            property_to_save_embedding="unesco_all_MiniLM_L12_v2",
            vector_dimension= 384
        )
        # 2.1 show all indexes (OPTIONAL)
        st.write(get_indexes())
        # 3. update the graph to manage the language individually 
        text_node_properties= ['prefLabel', "altLabel",'description','title','literalForm','scopeNote']
        for property in text_node_properties:
            set_node_properties(label="Unesco", property_name=property, lang="es")
        # 3. Get the access to the index created
        # Note: Because we are using vocabularies that follow the skos model, 
        # the properties that contain multiple languages ​​are the following. 
        #   ("skos","prefLabel"), 
        #   ("skos","altLabel"), 
        #   ('dct','description'), 
        #   ('dct','title'), 
        #   ('skosxl','literalForm'), 
        #   ('skos','scopeNote'),
        # The algorithm for creating vectors assumes that the data type is a string
        #  and is being saved in a database as an array in the format ['string@code_language',...]
        # access_neo_index(
        #     vector_name = 'unesco_all_MiniLM_L12_v2',
        #     node_label = "Unesco",
        #     text_node_properties= ['prefLabel', "altLabel",'description','title','literalForm','scopeNote'],
        #     text_node_properties_language='es',
        #     embedding_property_saved = 'unesco_all_MiniLM_L12_v2',
        #     embeddings = embeddings_provider
        # )

        # si se elimina el indice tambien hay que eliminar el valor de la propiedad donde se guarda el embedding

h = Home()
# ********************************
# The `_page` variable is saved for each page, 
# this is so that the translation selection works between multiple pages.
# ********************************
st.session_state._page = 'home'
st.Page(h, title="Sceiba/Home")