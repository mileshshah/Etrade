from google import genai

class GeminiClient:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_id = 'gemini-2.0-flash'

    def analyze_portfolio(self, portfolio_data):
        """
        Analyze the portfolio data using Gemini.
        """
        if not portfolio_data:
            return "No portfolio data provided for analysis."

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

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error during Gemini analysis: {e}"
