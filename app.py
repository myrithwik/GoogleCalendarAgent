#from swarm import Swarm
from utils_and_tools.logger import logger
#from agents import Runner
from my_agents.google_calendar_agent import extract_request_type, general_agent, calendar_agent
from my_agents.date_scheduler_agent import coordinating_date_agent
import streamlit as st
import asyncio
from api_keys.openai_api import client
from openai.types.chat import ChatCompletionMessage


model = "gpt-5-nano"

def handle_message(messages, prompt):
    logger.info("Routing user request")
    request_type = extract_request_type(messages, prompt)
    logger.info(
        f"Request routed as: {request_type.request_type} with confidence: {request_type.confidence_score}"
    )
    if request_type.request_type == "general":
        logger.info("Passing request to the general agent.")
        response = general_agent(messages, prompt)
        logger.debug(
            f"General agent response: {response}"
        )
    elif request_type.request_type == "calendar":
        logger.info("Passing request to the calendar agent.")
        response = calendar_agent(messages, prompt)
        logger.debug(
            f"Calendar agent response: {response}"
        )
    elif request_type.request_type == "date":
        logger.info("Passing request to the date scheduling agent.")
        response = coordinating_date_agent(messages, prompt)

    return response

def main():
    #swarm_client = Swarm()
    #agent = main_agent

    st.title('Create A Google Calendar AI Agent')

    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        if isinstance(message, ChatCompletionMessage):
            # new_msg = {
            #     "role": message.role,
            #     "content": (
            #         message.content if isinstance(message.content, str) else str(message.content)
            #     )
            # }
            # message = new_msg
            continue
        if message["role"] == "tool":
            continue
        with st.chat_message(message['role']):
            st.markdown(message['content'])
    
    if prompt := st.chat_input('Enter your prompt here'):
        st.session_state.messages.append({'role': 'user', 'content': prompt})

        with st.chat_message('user'):
            st.markdown(prompt)
        
        with st.chat_message('ai'):
            try:  
                #history = st.session_state.messages.copy()
                response = handle_message(st.session_state.messages, prompt)         
                # response = asyncio.run(Runner.run(
                #     starting_agent=agent,
                #     input= st.session_state.messages
                # ))
            except Exception as e:
                print(f"Error with calling the agent: {e}")
                return
            st.markdown(response['content'])
            #st.markdown(response.final_output)
            #print(response.raw_responses)
            #st.markdown(response.messages[-1]['content'])
        st.session_state.messages.append(response)

if __name__ == "__main__":
    main()