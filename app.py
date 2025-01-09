import streamlit as st
import PyPDF2
import ollama
from io import StringIO

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += f"Page {page_num + 1}:\n{page.extract_text()}\n\n"
    return text

# Function to simulate citation (extract page number or topic)
def generate_citation(response_text, pdf_text):
    # Simulate finding the most relevant page
    for page_num, page_text in enumerate(pdf_text.split("Page ")):
        if response_text.lower() in page_text.lower():
            return f"Page {page_num + 1}"
    return "Page not found"

# Initialize session state for chat history and uploaded PDFs
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_pdfs" not in st.session_state:
    st.session_state.uploaded_pdfs = {}

# Streamlit UI
st.title("📄 PDF Chatbot with Ollama (llama3.2:latest)")

# Sidebar for PDF management
with st.sidebar:
    st.header("📂 PDF Management")
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    if uploaded_file:
        pdf_name = uploaded_file.name
        st.session_state.uploaded_pdfs[pdf_name] = extract_text_from_pdf(uploaded_file)
        st.success(f"Uploaded {pdf_name}!")

    if st.session_state.uploaded_pdfs:
        selected_pdf = st.selectbox("Select a PDF to chat with", list(st.session_state.uploaded_pdfs.keys()))
        st.write(f"Selected PDF: **{selected_pdf}**")
    else:
        st.write("No PDFs uploaded yet.")

    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.success("Chat history cleared!")

# Main chat interface
if st.session_state.uploaded_pdfs:
    st.header("💬 Chat with the PDF")

    # Display chat history
    for prompt, response, citation in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(f"**You:** {prompt}")
        with st.chat_message("assistant"):
            st.write(f"**Bot:** {response}")
            st.caption(f"Citation: {citation}")

    # Input for user question
    user_question = st.chat_input("Ask a question about the PDF content...")
    if user_question:
        # Add user question to chat history
        st.session_state.chat_history.append((user_question, "", ""))

        # Get the selected PDF text
        pdf_text = st.session_state.uploaded_pdfs[selected_pdf]

        # Combine the PDF text and user question
        input_text = f"PDF Content:\n{pdf_text}\n\nQuestion: {user_question}"

        # Send the input to Ollama for processing
        with st.spinner("Generating response..."):
            try:
                response = ollama.generate(
                    model="llama3.2:latest",
                    prompt=input_text
                )
                response_text = response["response"]

                # Generate citation
                citation = generate_citation(response_text, pdf_text)

                # Update chat history with response and citation
                st.session_state.chat_history[-1] = (user_question, response_text, citation)

                # Rerun to update the chat interface
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {e}")

    # Download chat history
    if st.session_state.chat_history:
        chat_history_text = "\n\n".join(
            [f"You: {prompt}\nBot: {response}\nCitation: {citation}" for prompt, response, citation in st.session_state.chat_history]
        )
        st.download_button(
            label="Download Chat History",
            data=chat_history_text,
            file_name="chat_history.txt",
            mime="text/plain",
        )

    # Feedback button
    if st.session_state.chat_history:
        feedback = st.radio("Rate the last response:", ("👍 Good", "👎 Bad"))
        if feedback:
            st.write(f"Thank you for your feedback: {feedback}")

else:
    st.write("Please upload a PDF file to get started.")

# App status in the sidebar
st.sidebar.markdown("### App Status")
st.sidebar.write("App is running and waiting for input.")