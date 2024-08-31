import streamlit as st
from langchain_openai import ChatOpenAI
from llama_index.core import SQLDatabase
from llama_index.core.indices.struct_store import NLSQLTableQueryEngine
from llama_index.core import Settings
from sqlalchemy import create_engine

DB_FILE = "sample.db"

st.title("text-to-sql") 


question = st.text_input(label="質問")

if question:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
    
    engine = create_engine(f"sqlite:///{DB_FILE}")
    sql_database = SQLDatabase(engine)
    settings = Settings
    query_engine = NLSQLTableQueryEngine(sql_database=sql_database, settings=settings)  
    
    try:
        response = query_engine.query(question)
        sql_query = response.metadata.get("sql_query", "")

        # SQLクエリがセミコロンで終わっているか確認し、必要に応じて追加
        if not sql_query.endswith(";"):
            sql_query += ";"

        st.info(f"修正後のSQLクエリ: {sql_query}")
        st.success(response.response)
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")