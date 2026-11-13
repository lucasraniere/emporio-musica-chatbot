from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_openrouter import ChatOpenRouter
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from emporio.agent.prompts import SYSTEM_PROMPT
from emporio.config import settings
from emporio.tools import ALL_TOOLS

WEEKDAYS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
            "sexta-feira", "sábado", "domingo"]


def _now_text() -> str:
    now = settings.now()
    return f"{WEEKDAYS[now.weekday()]}, {now:%d/%m/%Y %H:%M}"


def _default_llm() -> BaseChatModel:
    if settings.llm_provider == "google":
        # Imported here so the app still starts when only OpenRouter is installed.
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.google_api_key,
            temperature=settings.llm_temperature,
            max_retries=2,
        )
    if settings.llm_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        # No temperature here: current Claude models reject non-default sampling
        # parameters with a 400. max_tokens leaves room for the model's thinking.
        return ChatAnthropic(
            model=settings.llm_model,
            api_key=settings.anthropic_api_key,
            max_tokens=16000,
            max_retries=2,
        )
    return ChatOpenRouter(
        model=settings.llm_model,
        api_key=settings.openrouter_api_key,
        temperature=settings.llm_temperature,
        max_retries=2,
    )


def build_graph(checkpointer: BaseCheckpointSaver | None = None, llm: BaseChatModel | None = None):
    llm_with_tools = (llm or _default_llm()).bind_tools(ALL_TOOLS)

    def agent(state: MessagesState) -> dict:
        # Built on every call and never stored, so the date is always current.
        system = SystemMessage(SYSTEM_PROMPT.format(now=_now_text()))
        return {"messages": [llm_with_tools.invoke([system, *state["messages"]])]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent)
    builder.add_node("tools", ToolNode(ALL_TOOLS))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)  # -> "tools" or END
    builder.add_edge("tools", "agent")
    return builder.compile(checkpointer=checkpointer)
