import streamlit as st
import os
from datetime import datetime
import langchain
from typing import Optional, List, Dict, Any  # 必要な型をインポート
import requests
from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from pydantic import BaseModel, Field
from zoneinfo import ZoneInfo

class GoogleCalendarAddEventArgs(BaseModel):
    event_name: str = Field(examples=["会議"])
    start_at: str = Field(examples=["2022-01-01T00:00:00+09:00"])
    duration: Optional[str] = Field(description="HH:mm", examples=["01:00", "02:00"])
    
@tool("google_calender_add_event", args_schema=GoogleCalendarAddEventArgs)
def google_calender_add_event_tool(event_name: str, start_at: str, duration: Optional[str]):
    """Google Calender Add Event"""
    print("google_calender_add_event_tool run")
    webhook_url = os.environ["MAKE_WEBHOOK_URL"]
    body = {
        "eventName": event_name,
        "startAt": start_at,
        "duration": duration
    }
    print("body", body)
    result = requests.post(webhook_url, json=body)
    st.write(result)
    return f"Status: {result.status_code} - {result.text}"

@tool("clock")
def clock_tool():
    """Clock"""
    return datetime.now(ZoneInfo("Asia/Tokyo")).isoformat()


st.title("AIアシスタント")

input = st.text_input(label="何を依頼しますか")

if input:
    with st.spinner("考え中…"):
        llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
        agent = initialize_agent(  # Agentのがツールを使えるようにする
            tools=[google_calender_add_event_tool, clock_tool],
            llm=llm,
            agent=AgentType.OPENAI_FUNCTIONS
            )
        result = agent.run(f"{input} 時間は日本時間を使ってください")
        st.write(result)