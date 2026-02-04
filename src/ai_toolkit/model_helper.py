from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel


def get_model(model_name: str,
              temperature: float = 0.5,
              timeout: int = 600) -> BaseChatModel:
    """Utility to get the LLM model instance based on the model name."""

    llm: BaseChatModel = init_chat_model(
        model_name,
        temperature=temperature,
        timeout=timeout
    )  # type: ignore

    return llm