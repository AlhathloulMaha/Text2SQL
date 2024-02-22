import os
from pathlib import Path
import sqlite3
import streamlit as st
from langchain.chains import LLMChain
from langchain_openai import OpenAI
from langchain.prompts import load_prompt
from langchain.sql_database import SQLDatabase
from sqlite3 import OperationalError
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate


class Text2SQLAssistant:
    def __init__(self):
        self.llm = None
        self.sql_chain = None
        self.db = None

    def set_up(self):
        # API key
        os.environ['OPENAI_API_KEY'] = '--'

        # Connect to Database
        self.db = SQLDatabase.from_uri("Chinook.db")

        # Front-end for streamlit
        st.title("Text2SQL Assistant")
        self.user_input = st.text_input("Enter your query here")
        self.tab_titles = ["Answer","Result", "Query"]
        self.tabs = st.tabs(self.tab_titles)

        # Create the prompt
        prompt_template = load_prompt("tpch_prompt.yaml")

        self.llm = OpenAI(temperature=0)

        self.sql_chain = LLMChain(llm=self.llm,
                                  prompt=prompt_template,
                                  verbose=True)

    def run(self):
        result = None
        sql_query = None
        answer_prompt = None
        answer = None
        answer_chain = None

        if self.user_input:
            sql_query = self.sql_chain(self.user_input)["text"]  # Extract the text from the response dictionary
            if "I do not know".lower() in sql_query.lower():
                 result = "I'm sorry, I don't have an answer for that."
                 answer= "I'm sorry, I don't have an answer for that."
            else:
                result = self.db.run(sql_query)
                answer_prompt = PromptTemplate.from_template(
                """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
                Question: {user_input}
                SQL Query: {sql_query}
                SQL Result: {result}
                Answer: """
                )
                answer_chain = LLMChain(llm=self.llm,prompt=answer_prompt,verbose=True)
                answer = answer_chain({
                    "user_input": self.user_input,
                    "sql_query": sql_query,
                    "result": result
                })["text"]

            with self.tabs[0]:
                st.write(answer)
            with self.tabs[1]:
                st.write(result)

            with self.tabs[2]:
                if sql_query is not None:
                    st.write(sql_query)
                else:
                    sql_query = "I'm sorry, I don't have an answer for that."



if __name__ == "__main__":
    assistant = Text2SQLAssistant()
    assistant.set_up()
    assistant.run()