from google import genai


class AIModel:

    def __init__(
        self,
        model="gemini-3.8-flash"
    ):

        self.model = model

        self.client = genai.Client()

    def generate(self, message):

        interaction = self.client.interactions.create(
            model=self.model,
            input=message
        )

        return interaction.output_text