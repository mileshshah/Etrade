from google import genai

class GeminiClient:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_id = 'gemini-2.0-flash'

    def analyze_portfolio(self, portfolio_data):
        """
        Perform a general analysis of the portfolio data.
        """
        prompt = f"""
        Analyze the following E*TRADE portfolio data:
        {portfolio_data}

        For each company in the portfolio, provide:
        1. A brief overview of what is currently happening with the company.
        2. General recent news.
        3. A summary of market sentiment and what people are saying on social media (e.g., Twitter/X).
        4. Any new technological advancements or products related to the company.

        Format the output clearly for a human reader.
        """
        return self._generate(prompt)

    def chat(self, portfolio_data, user_question):
        """
        Answer a specific user question about the portfolio data.
        """
        prompt = f"""
        You are a financial assistant. Below is the user's E*TRADE portfolio data:
        {portfolio_data}

        The user has the following question:
        "{user_question}"

        Please provide a helpful, data-driven answer based on the portfolio information and your general knowledge of the market and companies involved.
        """
        return self._generate(prompt)

    def _generate(self, prompt):
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error during Gemini interaction: {e}"
