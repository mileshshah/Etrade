from google import genai
from google.genai import types

class GeminiClient:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_id = 'gemini-2.0-flash'

    def chat(self, portfolio_data, user_question, account_context=None, tools=None):
        """
        Answer a specific user question about the portfolio data with support for tools (functions).
        """
        prompt = f"""
        You are an advanced financial assistant with trading capabilities.
        Below is the user's filtered E*TRADE portfolio data (restricted for privacy):
        {portfolio_data}

        Account Context:
        {account_context if account_context else 'No account selected or context provided.'}

        The user has the following question or instruction:
        "{user_question}"

        You can use tools to perform actions like previewing or placing trades if requested.
        Always inform the user when you are using a tool and provide the results clearly.
        """

        # Configuration for tools with automatic function calling enabled
        config = types.GenerateContentConfig(
            tools=tools if tools else [],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False
            )
        )

        try:
            # Create a chat session with automatic function calling
            chat_session = self.client.chats.create(model=self.model_id, config=config)
            response = chat_session.send_message(prompt)

            return response.text
        except Exception as e:
            return f"Error during Gemini interaction: {e}"

    def _generate(self, prompt):
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error during Gemini interaction: {e}"
