from langchain_core.messages import SystemMessage, HumanMessage

# System prompts
# ? Notion related prompt
notion_assistant_prompt = SystemMessage(
    content="You are an expert writing assistant, that loves to fix and correct writings to make them look impactful, super clean and easy to follow." \
    "You also are very structured to put ideas into text."
)

def notion_user_prompt(user_input: str):
    return HumanMessage(
        content=f"""The text you are receiving is a coding idea or any other type of idea.

        So based on this idea, I want you to create a new text based on this idea, I want you to structure a text explaining the idea and give minimal steps how to implement it.
        The output of this would be 3 things a title, text (split it into different paragraphs as needed it) and a random fun icon to use.
        \n\nHere is the idea: {user_input}
        \n\nNow, please follow this directions. Your result should have the response formatted following:

        The JSON output must be a valid JSON object with the following keys:
        - "title": A concise title for the content.
        - "text": list of all paragraphs.
        - "icon": A random emoji or icon related to the topic.

        Here's an example of the desired JSON format:

        ```json
        {{
        "title": "AI-Powered Coding Research & Content Generator",
        "text": ["This idea proposes the development of an intelligent AI agent designed to automate the laborious process of gathering and synthesizing information on various coding-related topics..."],
        "icon": "🤖"
        }}
        ```

        Ensure your response is ONLY the JSON object, with no extra properties or whatever.
    """
    )


# ? MMM prompts
mmm_system_prompt = SystemMessage(
    content="You are an expert finding amazing quotes and phrases from different authors books. You are great at finding quotes related to a topic."
)

def mmm_user_prompt_topic(topic: str):
    return HumanMessage(
    content=f"""Can you please provider a quote or phrase, related to this specific topic: {topic}.

    Here are the requirements:
    - Please provide a quote and phrase related to the specific topic, do not give me a phrase or quote related to other topic or something random.
    - The idea is to search for positive quotes or phrases, no negativity.
    - Please always give me back quotes or phrases that have an author, if not say the author is Unknown Author.
    - Give me back short quotes or phrases, please.
    """
)
