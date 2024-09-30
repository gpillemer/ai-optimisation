from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI


from prompts import create_application_prompt_template, review_application_prompt_template, fix_application_prompt_template, create_application_prompt_template_o1
from langchain_core.messages import AIMessage

from bs4 import BeautifulSoup


def get_output(ai_message: AIMessage):
    soup = BeautifulSoup(ai_message.content, "html.parser")
    return soup.find("daisyappoutput").text


llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", max_tokens=8192, temperature=0.05)
llm_o1 = ChatOpenAI(model="o1-preview-2024-09-12", temperature=1)

create_application_chain = create_application_prompt_template | llm | get_output
create_application_chain_o1 = create_application_prompt_template_o1 | llm_o1 | get_output

review_and_create_application_chain = (
    {"application_code": create_application_chain}
    | review_application_prompt_template
    | llm
    | get_output
)


def get_application_create_chain(review_application_code=False, use_o1=False):
    if use_o1:
        return create_application_chain_o1
    if review_application_code:
        return review_and_create_application_chain
    else:
        return create_application_chain
    
fix_application_chain = fix_application_prompt_template | llm | get_output

def get_application_fix(error_message, application_code):
    return fix_application_chain.invoke({"error_message": error_message, "application_code": application_code})