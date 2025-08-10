import os
import re
import smtplib

from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from email.mime.text import MIMEText

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
    SystemMessage,
)
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

load_dotenv()
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

document_content = ""
file_name = ""


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


@tool(description="Update the in-memory document with the provided full content.")
def update(content: str) -> str:
    """Updates the in-memory document content."""
    global document_content
    document_content = content
    return f"Document has been updated successfully! Current content:\n\n{document_content}"


@tool(
    description="Save the in-memory document content to a text file with the specified filename."
)
def save(filename: str) -> str:
    """Saves the current in-memory document to a .txt file."""
    global document_content
    global file_name
    if not filename.endswith(".txt"):
        filename += ".txt"
    file_name = filename
    try:
        with open(filename, "w") as file:
            file.write(document_content)
        return f"Document has been saved successfully to '{filename}'."
    except Exception as e:
        return f"Error saving document: {str(e)}"


@tool(description="Check if the provided email address is valid for sending.")
def add_email(email: str) -> str:
    """Validates the format of an email address."""
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email): #needs updated
        return "Invalid email format. Please provide a valid email address."
    return f"Email '{email}' is valid and ready to receive the document."


@tool(description="Send the current document via email to the given address.")
def send_email(recipient: str) -> str:
    """Sends the current document content to a recipient via email."""
    global document_content

    try:
        msg = MIMEText(document_content)
        msg["Subject"] = subject()
        msg["From"] = SMTP_USERNAME
        msg["To"] = recipient

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, recipient, msg.as_string())

        return f"Document sent to {recipient} successfully."
    except Exception as e:
        return f"Error sending email: {str(e)}"


tools = [update, save, add_email, send_email]
llm = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools) # needs updated gemini


def subject():
    global file_name
    if file_name.endswith(".txt"):
        file_name = file_name[:-3]
    for _ in range(file_name.count("_")):
        file_name = file_name.replace("_", " ")

    return f"{file_name} [drafted]"


def our_agent(state: AgentState) -> AgentState: #system propmt
    system_prompt = SystemMessage(
        content=f"""
You are Drafter, a helpful writing assistant. You help the user update and modify a document in memory.
- Use 'update' to update the document with new content.
- Use 'save' when the user wants to save the document.
- After saving, confirm and stop tool usage.
- Show current content after updates.

Current document:
----------------------------
{document_content if document_content else "(empty)"}
----------------------------
"""
    )

    if not state["messages"]:
        user_message = HumanMessage(
            content="I'm ready to help you update or save a document. What would you like to do?"
        )
    else:
        user_input = input("\nWhat would you like to do with the document? ")
        print(f"User: {user_input}")
        user_message = HumanMessage(content=user_input)

    full_context = [system_prompt] + list(state["messages"]) + [user_message]
    response = llm.invoke(full_context)

    print(f"\nAI: {response.content}")
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"USING TOOLS: {[tc['name'] for tc in response.tool_calls]}")

    return {"messages": list(state["messages"]) + [user_message, response]}


def should_continue(state: AgentState) -> str:
    for message in reversed(state["messages"]):
        if isinstance(message, ToolMessage):
            content = message.content.lower()
            if "saved" in content and "document" in content:
                print("\nThe document has been saved to disk.")

                email = input(
                    "Enter an email address to send the document (or leave blank to skip): "
                ).strip()
                if email:
                    print(add_email.invoke({"email": email}))
                    print(send_email.invoke({"recipient": email}))

                return "end"
    return "continue"


def print_messages(messages: Sequence[BaseMessage]) -> None:
    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print(f"\nTOOL RESULT: {message.content}")


graph = StateGraph(AgentState)

graph.add_node("agent", our_agent)
graph.add_node("tools", ToolNode(tools))

graph.set_entry_point("agent")
graph.add_edge("agent", "tools")
graph.add_conditional_edges("tools", should_continue, {"continue": "agent", "end": END})
app = graph.compile()


def run_agent():
    print("\n+=+=+=+ DRAFTER WITH EMAIL SUPPORT +=+=+=+")
    state: AgentState = {"messages": []}

    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])

    print("\n+=+=+=+ DRAFTER SESSION ENDED +=+=+=+")


if __name__ == "__main__":
    run_agent()
