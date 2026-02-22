"""
Example: LangChain agent using MoltraffleToolkit.
Install: pip install moltraffle[langchain] langchain langchain-openai
"""
from moltraffle import MoltraffleToolkit
from moltraffle.client import MoltraffleClient

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# Build toolkit
client = MoltraffleClient()
toolkit = MoltraffleToolkit(client=client)
tools = toolkit.get_tools()

# Set up LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an on-chain raffle agent operating on Base mainnet via moltraffle.fun. "
        "You can discover active raffles, retrieve their details, and generate transaction calldata "
        "to create or join them. Always present calldata clearly so the user can review before signing."
    )),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    response = agent_executor.invoke({
        "input": "Find the active raffle with the highest prize pool and show me how to join it."
    })
    print("\n=== Agent Response ===")
    print(response["output"])
