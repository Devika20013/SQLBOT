
# import os
# import re
# from datetime import datetime, timedelta
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_community.utilities import SQLDatabase
# from langchain_together import ChatTogether
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables import RunnablePassthrough
# from langchain_community.agent_toolkits import SQLDatabaseToolkit
# from langchain_core.messages import SystemMessage, HumanMessage
# from langgraph.prebuilt import create_react_agent

# # Set the API key
# os.environ["TOGETHER_API_KEY"] = "38642b269f2f83848c5e50838ddbe856da4dddfa604014763b9a0d950c44456a"

# # Connect to the database
# db_uri1 = "mysql+mysqlconnector://root:123456789@127.0.0.1:3306/chinook"
# db1 = SQLDatabase.from_uri(db_uri1)

# # Create the LLM
# llm = ChatTogether(
#     api_key=os.environ["TOGETHER_API_KEY"],
#     temperature=0.0,
#     model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
# )

# # Create a prompt template for SQL query generation
# prompt = ChatPromptTemplate.from_template("""
# Based on the table schema below, write an SQL query that would answer the user's question:
# {schema}

# User question: {question}

# Respond with ONLY the SQL query, nothing else. Do not include any markdown formatting or backticks.

# SQL Query:
# """)

# # Function to get the schema
# def get_schema(_):
#     return db1.get_table_info()

# # Function to clean the SQL query
# def clean_sql_query(query):
#     # Remove markdown SQL formatting
#     query = re.sub(r'```sql\s*|\s*```', '', query)
#     # Remove any remaining backticks
#     query = query.replace('`', '')
#     return query.strip()

# # Create the SQL query chain
# sql_chain = (
#     RunnablePassthrough.assign(schema=get_schema)
#     | prompt
#     | llm.bind(stop=["\n", "SQL Result:"])
#     | StrOutputParser()
#     | clean_sql_query
# )

# # Function to execute the query
# def execute_query(query):
#     return db1.run(query)

# # Answer prompt
# answer_prompt = ChatPromptTemplate.from_template(
#     """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

# Question: {question}
# SQL Query: {query}
# SQL Result: {result}
# Answer: """
# )

# # Function to process a question
# last_query_time = None
# query_limit = 6  # queries per minute
# def process_question(question):
#     global last_query_time

#     if last_query_time is None or datetime.now() - last_query_time >= timedelta(minutes=1):
#         last_query_time = datetime.now()

#         query = sql_chain.invoke({"question": question})
#         result = execute_query(query)
#         answer = sql_chain.invoke({"question": question})

#         print(f"Question: {question}")
#         print(f"SQL Query: {query}")
#         print(f"SQL Result: {result}")
#         print(f"Answer: {answer}")
#         print("-" * 50)
#     else:
#         print(f"You have reached the rate limit of {query_limit} queries per minute. Please try again later.")

# # Example usage
# user_question = input("Please enter your question: ")
# process_question(user_question)

# # Create SQLDatabaseToolkit for more complex queries
# toolkit = SQLDatabaseToolkit(db=db1, llm=llm)
# tools = toolkit.get_tools()

# # Define system message for the agent
# SQL_PREFIX = """You are an agent designed to interact with a SQL database.
# Given an input question, create a syntactically correct SQL query to run, then look at the results of the query and return the answer.
# Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
# You can order the results by a relevant column to return the most interesting examples in the database.
# Never query for all the columns from a specific table, only ask for the relevant columns given the question.
# You have access to tools for interacting with the database.
# Only use the below tools. Only use the information returned by the below tools to construct your final answer.
# You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

# DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

# To start you should ALWAYS look at the tables in the database to see what you can query.
# Do NOT skip this step.
# Then you should query the schema of the most relevant tables."""

# system_message = SystemMessage(content=SQL_PREFIX)

# # Create the agent executor for more complex queries
# agent_executor = create_react_agent(llm, tools, state_modifier=system_message)

# # Example of a more complex query using the agent
# complex_question = input("Please enter a more complex question: ")
# complex_result = agent_executor.invoke({"input": complex_question})
# print(f"Complex Question: {complex_question}")
# print(f"Complex Result: {complex_result}")












import os
import re
from datetime import datetime, timedelta
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_together import ChatTogether
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import SystemMessage, HumanMessage

# Set the API key
os.environ["TOGETHER_API_KEY"] = "38642b269f2f83848c5e50838ddbe856da4dddfa604014763b9a0d950c44456a"

# Connect to the database
db_uri1 = "mysql+mysqlconnector://root:123456789@127.0.0.1:3306/chinook"
db1 = SQLDatabase.from_uri(db_uri1)

# Create the LLM
llm = ChatTogether(
    api_key=os.environ["TOGETHER_API_KEY"],
    temperature=0.0,
    model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
)

# Create a prompt template for SQL query generation
prompt = ChatPromptTemplate.from_template("""
Based on the table schema below, write an SQL query that would answer the user's question:
{schema}

User question: {question}

Respond with ONLY the SQL query, nothing else. Do not include any markdown formatting or backticks.

SQL Query:
""")

# Function to get the schema
def get_schema(_):
    return db1.get_table_info()

# Function to clean the SQL query
def clean_sql_query(query):
    # Remove markdown SQL formatting
    query = re.sub(r'```sql\s*|\s*```', '', query)
    # Remove any remaining backticks
    query = query.replace('`', '')
    return query.strip()

# Create the SQL query chain
sql_chain = (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt
    | llm.bind(stop=["\n", "SQL Result:"])
    | StrOutputParser()
    | clean_sql_query
)

# Function to execute the query
def execute_query(query):
    return db1.run(query)

# Answer prompt
answer_prompt = ChatPromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
)

# Function to process a question
last_query_time = None
query_limit = 6  # queries per minute
def process_question(question):
    global last_query_time

    if last_query_time is None or datetime.now() - last_query_time >= timedelta(minutes=1):
        last_query_time = datetime.now()

        query = sql_chain.invoke({"question": question})
        result = execute_query(query)
        answer = answer_prompt.invoke({"question": question, "query": query, "result": result})

        print(f"Question: {question}")
        print(f"SQL Query: {query}")
        print(f"SQL Result: {result}")
        print(f"Answer: {answer}")
        print("-" * 50)
    else:
        print(f"You have reached the rate limit of {query_limit} queries per minute. Please try again later.")

# Example usage
user_question = input("Please enter your question: ")
process_question(user_question)