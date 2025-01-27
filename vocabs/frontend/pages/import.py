from langchain_huggingface import HuggingFaceEmbeddings
import streamlit as st
from streamlit import config
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
        try:
            st.title(_('Sceiba Vocabularies Service'))
            # st.subheader('System for vocabularies')
            with st.form('my_form'):
                st.write(_('**Import Thesaurus**'))
                id_value = st.text_input(label=_('Vocabulary URL'), placeholder=_('example.com'), help=_('It is used to identify that each vocabulary item contains the URL, just provide the domain, example: `unesco.org`'))
                labels = st.text_input(label=_('Labels'), placeholder=_('Unesco or Unesco:Vocabulary ...'), help=_('It is used to classify each vocabulary element with this tag, the format must be the tag without spaces followed by two points if more than one is added, example: `Unesco` or `Unesco:Vocabulary`'))
                
                uploaded_file = st.file_uploader(_("Choose a file"), type=['ttl', 'xml', 'rdf'], accept_multiple_files=False, help=_('Upload an RDF file. `Turtle` or `XML` formats are accepted.'))              
                
                # Every form must have a submit button
                submitted = st.form_submit_button(_('Submit'))
            
            if submitted and id_value is not None and labels is not None and uploaded_file is not None:
                connection = Connection()
                # pre configuration
                neo = NeoSemantics()
                constraint =neo.create_constraint_and_default_config()
                if constraint is not None:
                    st.toast(_('Added restriction to make `uri` unique'))
                
                st.toast(_('Adding information to the database. Please wait!'), icon=':material/info:')
                result = neo.import_data(
                    path= uploaded_file.getvalue(),#'file:///home/edel/Projects/PhD/unesco-thesaurus.ttl', 
                    format= uploaded_file.type,#'ttl',
                    tags= {
                        'identifier': 'uri',
                        'id_value': id_value,
                        'labels': labels
                    }
                    )
                if result:
                    st.toast(_('Added information'), icon=':material/info:')
                connection.close()
            else: st.toast(_('You must fill out the form correctly'), icon=':material/warning:')

        except Exception as e:
            st.toast(e, icon=':material/warning:')

    # def persolalice_ulpad_file_component(self):
    #     hide_label = (
    #         """
    #         <style>
    #             div[data-testid="stFileUploader"]>section[data-testid="stFileUploadDropzone"]>button[data-testid="baseButton-secondary"] {
    #             color:white;
    #             }
    #             div[data-testid="stFileUploader"]>section[data-testid="stFileUploadDropzone"]>button[data-testid="baseButton-secondary"]::after {
    #                 content: "BUTTON_TEXT";
    #                 color:black;
    #                 display: block;
    #                 position: absolute;
    #             }
    #             div[data-testid="stFileDropzoneInstructions"]>div>span {
    #             visibility:hidden;
    #             }
    #             div[data-testid="stFileDropzoneInstructions"]>div>span::after {
    #             content:"INSTRUCTIONS_TEXT";
    #             visibility:visible;
    #             display:block;
    #             }
    #             div[data-testid="stFileDropzoneInstructions"]>div>small {
    #             visibility:hidden;
    #             }
    #             div[data-testid="stFileDropzoneInstructions"]>div>small::before {
    #             content:"FILE_LIMITS";
    #             visibility:visible;
    #             display:block;
    #             }
    #         </style>
    #     """.replace(
    #             "BUTTON_TEXT", self._("Browse file")
    #         )
    #         .replace("INSTRUCTIONS_TEXT", self._("Drag and drop file here"))
    #         .replace("FILE_LIMITS",  self._("Limit") + " " + str(config.get_option("server.maxUploadSize")) + " " + self._("per file") )
    #     )
    #     st.markdown(hide_label,True)

i = Import()
st.Page(i, title="Sceiba/Import")