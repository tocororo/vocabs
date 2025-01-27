from langchain_huggingface import HuggingFaceEmbeddings
import pandas as pd
import numpy as np
import streamlit as st
from streamlit.url_util import is_url
from vocabs.backend.neo4voc.neo4_vector_index import Vector
from vocabs.frontend.locales.language import Language
from vocabs.frontend.pages.menu import Menu

class Vector_Index:

    model_name = None
    show_index = True

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
            st.title(self._('Vector Index'))
            
        except Exception as e:
            st.toast(e, icon=':material/warning:')
            st.exception(e)

        with st.container(border=True):
            st.write(self._('**Create Index**'))
            vector_name = st.text_input(label=self._('Vector Name'), placeholder=self._('index ...'), help=self._('Used to identify the index of the vector. Make sure the name is unique.'))
            node_labels = st.text_input(label=self._('Node Labels'), placeholder=self._('Unesco or Unesco:Vocabulary ...'), help=self._('It is used to classify each vocabulary element with this tag, the format must be the tag without spaces followed by two points if more than one is added, example: `Unesco` or `Unesco:Vocabulary`'))
            index_lang = st.selectbox(self._('Chosse a Language'), options=['es','en'])
            model_name = st.selectbox(self._('Chosse a Model'), options=[
                'sentence-transformers/all-MiniLM-L12-v2',
                'sentence-transformers/all-MiniLM-L6-v2',
                'sentence-transformers/all-mpnet-bembeddingsase-v2']
            )
            map_options = {
                'sentence-transformers/all-MiniLM-L12-v2': {'d':'384', 'n': 'all_MiniLM_L12_v2'},
                'sentence-transformers/all-MiniLM-L6-v2': {'d':'384', 'n': 'all_MiniLM_L6_v2'},
                'sentence-transformers/all-mpnet-bembeddingsase-v2': {'d':'768', 'n': 'all_mpnet_bembeddingsase_v2'}
            }
            selected_model_name = map_options[model_name]
            dimension = st.text_input(self._('vector Dimension'), value=selected_model_name['d'], disabled=True)
            node_properties= ['title','prefLabel', "altLabel",'description','scopeNote']
            # text_node_properties = st.multiselect(label=self._('Properties to include in the vector'), options=node_properties, help=self._('It is used to identify that each vocabulary item contains the URL, just provide the domain, example: `unesco.org`'))
            text_node_properties = st.selectbox(label=self._('Property to include in the vector'), options=node_properties)
            # Every form must have a submit button
            submitted = st.button(self._('Submit'))

        if submitted:
            # 1. embeddings provider
            embeddings_provider = HuggingFaceEmbeddings(model_name= model_name)
            property_to_save_embedding= vector_name+"_"+ index_lang+"_"+selected_model_name['n']
            # 2. create the index
            vector = Vector()
            vector.create_neo_index(
                vector_name= vector_name,
                node_labels=node_labels,
                property_to_save_embedding= property_to_save_embedding,
                vector_dimension= dimension
            )
            self.update_show_index()

            # 3. update the graph to manage the language individually 
            # text_node_properties= ['prefLabel', "altLabel",'description','title','literalForm','scopeNote']
            text_node_properties_update = []
            for property in text_node_properties:
                vector.set_node_properties(label=node_labels, property_name=property, lang=index_lang)
                text_node_properties_update.append('_'+property+'_'+index_lang)
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
            vector.create_neo_index_from_graph(
                vector_name = vector_name,
                node_label = node_labels,
                text_node_properties= text_node_properties_update,
                embedding_property_saved = property_to_save_embedding,
                embeddings = embeddings_provider
            )

            # si se elimina el indice tambien hay que eliminar el valor de la propiedad donde se guarda el embedding
        # 2.1 show all indexes (OPTIONAL)
        if self.show_index:
            self.update_show_index()
            self.show_index = False

    def update_show_index(self):
        with st.expander(self._('Show al indexes')):
            vector = Vector()
            records, summary, keys = vector.get_indexes()
            chart_data = pd.DataFrame(records,
            columns=keys)
            st.table(chart_data)
        


h = Vector_Index()
# ********************************
# The `_page` variable is saved for each page, 
# this is so that the translation selection works between multiple pages.
# ********************************
st.session_state._page = 'vector_index'
st.Page(h, title="Sceiba/Vector Index")