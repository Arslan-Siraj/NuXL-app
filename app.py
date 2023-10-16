import streamlit as st

from src.common import *
from src.captcha_ import *

params = page_setup(page="main")

def main():
    st.markdown(
        """# OpenNuXL"""
    )
    st.image("assets/NuXL_image.png")
    #In docker, OpenMS-app (executable) can be downloadable from github
    if Path("OpenMS-App.zip").exists():
        st.markdown("## Installation")
        with open("OpenMS-App.zip", "rb") as file:
            st.download_button(
                    label="Download for Windows",
                    data=file,
                    file_name="OpenMS-App.zip",
                    mime="archive/zip",
                )
    save_params(params) 

if "local" in sys.argv:
    params["controllo"] = True
    st.session_state["controllo"] = True
    main()

    # If not in local mode, assume it's hosted/online mode
else:
    # If captcha control is not in session state or set to False
    if 'controllo' not in st.session_state or st.session_state['controllo'] == False:
        # hide app pages as long as captcha not solved
        #delete_all_pages("app")

        # Apply captcha control to verify the user
        captcha_control()

    else:     
        # Run the main function
        main()

        # Restore all pages (assuming "app" is the main page)
        #restore_all_pages("app")
        