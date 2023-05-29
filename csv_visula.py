# Required imports
import streamlit as st
import pandas as pd
import json
from langchain import OpenAI
from langchain.agents import create_pandas_dataframe_agent


# Function to create agent from CSV file
def create_agent(filename: str):
    # Read API key from environment variable
    API_KEY = "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"
    
    # Create OpenAI object
    llm = OpenAI(openai_api_key=API_KEY)
    
    # Read CSV file into a Pandas DataFrame
    df = pd.read_csv(filename)
    
    # Create Pandas DataFrame agent
    return create_pandas_dataframe_agent(llm, df, verbose=False)

# Function to query the agent and return response as a dictionary
def query_agent(agent, query):
    prompt = (
        """
            For the following query, if it requires drawing a table, reply as follows:
            {"table": {"columns": ["column1", "column2", ...], "data": [[value1, value2, ...], [value1, value2, ...], ...]}}

            If the query requires creating a bar chart, reply as follows:
            {"bar": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

            If the query requires creating a line chart, reply as follows:
            {"line": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

            If it is just asking a question that requires neither, reply as follows:
            {"answer": "answer"}
            Example:
            {"answer": "The title with the highest rating is 'Gilead'"}

            Return all output as a string.

            All strings in "columns" list and data list, should be in double quotes,

            For example: {"columns": ["title", "ratings_count"], "data": [["Gilead", 361], ["Spider's Web", 5164]]}

            Lets think step by step.

            Below is the query.
            Query: 
            """
        + query
    )
    
    # Run the prompt through the agent
    response = agent.run(prompt)
    
    # Convert the response to a dictionary
    return json.loads(response.__str__())
    # return (response.__str__())

# Function to decode response from agent
def decode_response(response: str) -> dict:
    return json.loads(response)

# Function to write response to Streamlit app
def write_response(response_dict: dict):
    if "answer" in response_dict:
        st.write(response_dict["answer"])
    
    if "table" in response_dict:
        data = response_dict["table"]
        df = pd.DataFrame(data["data"], columns=data["columns"])
    # Display the table
    print(df)
    
    if "bar" in response_dict:
        data = response_dict["bar"]
        df = pd.DataFrame(data)
        df.set_index("columns", inplace=True)
        st.bar_chart(df)
    
    if "line" in response_dict:
        data = response_dict["line"]
        df = pd.DataFrame(data)
        df.set_index("columns", inplace=True)
        st.line_chart(df)

# Streamlit app interface
def main():
    st.title("👨‍💻 Chat with your CSV")
    st.write("Please upload your CSV file below.")
    
    data = st.file_uploader("Upload a CSV")
    query = st.text_area("Insert your query")
    
    if st.button("Submit Query", type="primary"):
        agent = create_agent(data)
        response = query_agent(agent=agent, query=query)
        decoded_response = decode_response(response)
        write_response(decoded_response)

# Run the Streamlit app
if __name__ == "__main__":
    main()
