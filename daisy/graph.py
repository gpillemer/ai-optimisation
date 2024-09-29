from langchain_anthropic import ChatAnthropic


from daisy.prompts import create_application_prompt_template, review_application_prompt
from langchain_core.messages import AIMessage

from bs4 import BeautifulSoup


def get_output(ai_message: AIMessage):
    soup = BeautifulSoup(ai_message.content, "html.parser")
    return soup.find("daisyappoutput").text


llm = ChatAnthropic(model="claude-3-5-sonnet-20240620",max_tokens=8192)
# llm = ChatOpenAI(model="gpt-4o")

create_application_chain = create_application_prompt_template | llm | get_output

create_and_review_application_code = create_application_chain

# create_and_review_application_code = (
#     {"application_code": create_application_chain}
#     | review_application_prompt
#     | llm
#     | get_output
# )
