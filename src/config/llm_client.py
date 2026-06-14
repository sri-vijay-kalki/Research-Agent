from src.config import config
from langchain_nvidia_ai_endpoints import ChatNVIDIA

class LLMClient:

    @staticmethod
    def get_client(model: str = config.MODEL, temperature: float = config.TEMPERATURE, max_tokens: int = config.MAX_TOKENS, top_p: float = config.TOP_P) -> ChatNVIDIA:
        """
        Returns a ChatNVIDIA client with the specified configuration.
        """
        return ChatNVIDIA(
            api_key=config.API_KEY, 
            base_url=config.BASE_URL, 
            model=model, 
            temperature=temperature, 
            max_completion_tokens=max_tokens, 
            top_p=top_p)


if __name__ == "__main__":
    client = LLMClient.get_client()
    response = client.invoke("Hello, how are you?")
    print(response.content)
