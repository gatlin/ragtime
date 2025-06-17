import logging
import os

import streamlit as st

from src.chat import (  # type: ignore
    ensure_model_pulled,
    generate_response_streaming,
    get_embedding_model,
)
from src.ingestion import create_index, get_opensearch_client
from src.constants import OLLAMA_MODEL_NAME, OPENSEARCH_INDEX
from src.utils import setup_logging

# Initialize logger
setup_logging()  # Configures logging for the application
logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(page_title="Discuss", page_icon="")


# Main chatbot page rendering function
def render_chatbot_page() -> None:
    # Set up a placeholder at the very top of the main content area
    st.title("Discuss")
    model_loading_placeholder = st.empty()

    # Initialize session state variables for chatbot settings
    if "think" not in st.session_state:
        st.session_state["think"] = True
    if "use_hybrid_search" not in st.session_state:
        st.session_state["use_hybrid_search"] = True
    if "num_results" not in st.session_state:
        st.session_state["num_results"] = 10
    if "temperature" not in st.session_state:
        st.session_state["temperature"] = 0.7

    # Initialize OpenSearch client
    with st.spinner("Connecting to OpenSearch..."):
        client = get_opensearch_client()
    index_name = OPENSEARCH_INDEX

    # Ensure the index exists
    create_index(client)

    # Sidebar settings for hybrid search toggle, result count, and temperature
    st.session_state["think"] = st.sidebar.checkbox(
        "Thought", value=st.session_state["think"]
    )
    st.session_state["use_hybrid_search"] = st.sidebar.checkbox(
        "RAG", value=st.session_state["use_hybrid_search"]
    )
    st.session_state["num_results"] = st.sidebar.number_input(
        "Number of Results in Context Window",
        min_value=1,
        max_value=10,
        value=st.session_state["num_results"],
        step=1,
    )
    st.session_state["temperature"] = st.sidebar.slider(
        "Response Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state["temperature"],
        step=0.1,
    )

    # Sidebar headers and footer

    # Footer text
    st.sidebar.markdown(
        """
        <div class="footer-text">
            © 1988 &mdash; Gatlin
        </div>
        """,
        unsafe_allow_html=True,
    )
    logger.info("Sidebar configured with headers and footer.")

    # Display loading spinner at the top of the main content area
    with model_loading_placeholder.container():
        st.spinner("Loading models for chat...")

    # Load models if not already loaded
    if "embedding_models_loaded" not in st.session_state:
        with model_loading_placeholder:
            with st.spinner(
                "Loading Embedding and Ollama models {OLLAMA_MODEL_NAME} for Hybrid Search...".format(
                    OLLAMA_MODEL_NAME=OLLAMA_MODEL_NAME
                )
            ):
                get_embedding_model()
                ensure_model_pulled(OLLAMA_MODEL_NAME)
                st.session_state["embedding_models_loaded"] = True
        logger.info("Embedding model loaded.")
        model_loading_placeholder.empty()

    # Initialize chat history in session state if not already present
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Display chat history
    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Process user input and generate response
    if prompt := st.chat_input("Type your message here..."):
        logger.warning("proving a point")
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        logger.info("User input received.")

        # Generate response from assistant
        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                response_placeholder = st.empty()
                response_text = ""

                response_stream = generate_response_streaming(
                    prompt,
                    think=st.session_state["think"],
                    use_hybrid_search=st.session_state["use_hybrid_search"],
                    num_results=st.session_state["num_results"],
                    temperature=st.session_state["temperature"],
                    chat_history=st.session_state["chat_history"],
                )

            # Stream response content if response_stream is valid
            if response_stream is not None:
                for chunk in response_stream:
                    if "message" in chunk and "content" in chunk["message"]:
                        response_text += chunk["message"]["content"]
                        response_placeholder.markdown(response_text + "▌")
                    else:
                        logger.error("Unexpected chunk format in response stream.")

            response_placeholder.markdown(response_text)
            st.session_state["chat_history"].append(
                {"role": "assistant", "content": response_text}
            )
            logger.warning(
                "Generated: {response_text}".format(response_text=response_text)
            )
            logger.info("Response generated and displayed.")


# Main execution
if __name__ == "__main__":
    render_chatbot_page()
