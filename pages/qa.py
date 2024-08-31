import streamlit as st
import tempfile
from pathlib import Path
from langchain_openai import ChatOpenAI
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.readers.file import PDFReader
import logging

logging.basicConfig(level=logging.DEBUG)
st.title('PDFへのQA')

index = st.session_state.get('index')
def on_change_file():
    if "index" in st.session_state:
        del st.session_state.index

uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'], on_change=on_change_file)


        
        
if uploaded_file and index is None:
    with st.spinner('Processing...'):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            
            documents = PDFReader().load_data(file=Path(temp_file.name))
            
            llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
            
            index = VectorStoreIndex.from_documents(
                documents=documents
            )
            st.write(temp_file.name)
            st.write('Processing done')
            
            
if index is not None:
    question = st.text_input(label="質問")
    
    if question:
        with st.spinner('Processing...'):
            query_engine = index.as_query_engine()
            answer = query_engine.query(f"{question}. 回答は日本語でお願いします")
            st.write(answer.response)
            st.info(answer.source_nodes)
            