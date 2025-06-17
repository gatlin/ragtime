import logging
import os

import streamlit as st

from src.utils import setup_logging

# Initialize logger
setup_logging()  # Set up logging configuration
logger = logging.getLogger(__name__)

# Set page config with title, icon, and layout
st.set_page_config(page_title="Hello, Dave. :-)", page_icon="")


# Function to display logo or placeholder
def display_logo(logo_path: str) -> None:
    """Displays the logo in the sidebar or a placeholder if the logo is not found.

    Args:
        logo_path (str): The file path for the logo image.
    """
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=220)
        logger.info("Logo displayed.")
    else:
        st.sidebar.markdown("### Logo Placeholder")
        logger.warning("Logo not found, displaying placeholder.")


# Function to display main content
def display_main_content() -> None:
    """Displays the main welcome content on the page."""
    st.title("Personal Document Assistant 📄🤖")
    st.markdown(
        """
        Welcome to the AI-Powered Document Retrieval Assistant 👋

        This app allows you to interact with an AI-powered assistant and upload documents for processing and retrieval.

        **Features:**
        - **Chatbot**: Have a conversation with the AI using the latest LLM model.
        - **Document Upload**: Upload PDFs and retrieve data from them using OpenSearch as a Hybrid RAG System.

        **Choose a page from the sidebar to begin!**
        """
    )
    logger.info("Displayed main welcome content.")


# Function to display sidebar content
def display_sidebar_content() -> None:
    """Displays headers and footer content in the sidebar."""
    st.sidebar.markdown(
        "<h2 style='text-align: center;'>Librarian</h2>", unsafe_allow_html=True
    )
    st.sidebar.markdown(
        """
        <div class="footer-text">
            © 1988 &mdash; Gatlin
        </div>
        """,
        unsafe_allow_html=True,
    )
    logger.info("Displayed sidebar content.")


# Main execution
if __name__ == "__main__":
    display_sidebar_content()
    display_main_content()
