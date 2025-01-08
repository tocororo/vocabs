import streamlit as st
from vocabs.frontend.locales.language import Language

class Menu:
    # ********************************
    # creates the variable `_` that contains the translation documents.
    # ********************************
    _ = None
    def __init__(self):
        l = Language()
        l.show_languages()
        self._ = l.language()

    def authenticated_menu(self):
        # Show a navigation menu for authenticated users
        st.sidebar.page_link("app.py", label=self._('Sceiba Vocabularies Service'))
        st.sidebar.page_link("pages/home.py", label=self._('Home'))
        
        if st.session_state.role in ["admin", "super-admin"]:
            st.sidebar.page_link("pages/import.py", label=self._('Import'))
            # st.sidebar.page_link(
            #     "pages/super-admin.py",
            #     label="Manage admin access",
            #     disabled=st.session_state.role != "super-admin",
            # )


    def unauthenticated_menu(self):
        # Show a navigation menu for unauthenticated users
        st.sidebar.page_link("pages/home.py", label="Log in")


    def menu(self):
        st.write(self._('Sceiba Vocabularies Service'))
        st.write(self._("Hello streamlit"))
        
        
        # Determine if a user is logged in or not, then show the correct
        # navigation menu
        if "role" not in st.session_state or st.session_state.role is None:
            self.unauthenticated_menu()
            return
        self.authenticated_menu()
        


    def menu_with_redirect(self):
        # Redirect users to the main page if not logged in, otherwise continue to
        # render the navigation menu
        if "role" not in st.session_state or st.session_state.role is None:
            st.switch_page("app.py")
        self.menu()