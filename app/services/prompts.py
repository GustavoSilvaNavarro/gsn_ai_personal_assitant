from langchain_core.messages import SystemMessage, HumanMessage

# System prompts
notion_assistant_prompt = SystemMessage(
    content="You are an expert writing assistant, that loves to fix and correct writings to make them look impactful, super clean and easy to follow." \
    "You also are very structured to put ideas into text."
)

def notion_user_prompt(user_input: str):
    return HumanMessage(
        content="The text you are receiving is a coding idea or any other type of idea." \
        "So based on this idea, I want you to create a new text based on this idea, I want you to structure a text explaining the idea and give minimal steps how to implement it." \
        "The output of this would be 3 things a title, text (split it into different paragraphs as needed it) and a random fun icon to use."
        f"\n\nHere is the idea: {user_input}"
    )
