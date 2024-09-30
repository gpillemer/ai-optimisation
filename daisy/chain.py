from langchain_anthropic import ChatAnthropic


from prompts import create_application_prompt_template, review_application_prompt_template, fix_application_prompt_template
from langchain_core.messages import AIMessage

from bs4 import BeautifulSoup


def get_output(ai_message: AIMessage):
    soup = BeautifulSoup(ai_message.content, "html.parser")
    return soup.find("daisyappoutput").text


llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", max_tokens=8192)
# llm = ChatOpenAI(model="gpt-4o")

create_application_chain = create_application_prompt_template | llm | get_output

review_and_create_application_chain = (
    {"application_code": create_application_chain}
    | review_application_prompt_template
    | llm
    | get_output
)


def get_application_create_chain(review_application_code=False):
    if review_application_code:
        return review_and_create_application_chain
    else:
        return create_application_chain
    
fix_application_chain = fix_application_prompt_template | llm | get_output

def get_application_fix(error_message, application_code):
    return fix_application_chain.invoke({"error_message": error_message, "application_code": application_code})