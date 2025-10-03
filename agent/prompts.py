from langchain_core.prompts import PromptTemplate

def get_agent_prompt() -> PromptTemplate:
    """
    Return the prompt template for the agent.
    """
    template = """
    You are a knowledge mining agent. Your task is to {task_description}.

    Use the available tools to gather and process information.

    Question: {input}
    """
    return PromptTemplate.from_template(template)