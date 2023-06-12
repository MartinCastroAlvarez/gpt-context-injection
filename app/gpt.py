import json
from typing import List
import requests
from .post import Post


class Gpt:
    """
    GPT APIutility.
    """

    API_KEY: str = ""
    TEMPERATURE: float = 0.5
    URL: str = "https://api.openai.com/v1/completions"
    MAX_CONTEXT_DOCUMENTS_SIZE: int = 3
    MAX_CONTEXT_SUMMARY_SIZE: int = 50

    def post(self, prompt: str, limit: int = 50):
        """
        Sends a post request to the GPT API.
        """
        headers: dict = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.API_KEY}"
        }
        payload: dict = {
            "model": "text-davinci-003",
            "prompt": prompt,
            "temperature": self.TEMPERATURE,
            "max_tokens": limit,
            "n": 1,
            # "stop": ["\n", ".", "!", "?"]
        }
        print(json.dumps(payload, indent=4, sort_keys=True))
        response: requests.Response = requests.post(self.URL, headers=headers, json=payload)
        print(response.status_code, response.reason)
        assert response.status_code == 200, response.text
        data: Union[dict, list] = response.json()
        print(json.dumps(data, indent=4, sort_keys=True))
        text: str = data['choices'][0]['text'].strip()
        print(text)
        return text

    def ask(self, question: str, context: List[Post], limit: int = 50) -> str:
        """
        Asks a question to the GPT API with Context Injection.
        """
        prompt: str = "\n".join([
            "Digest the following summarized blog posts in a way that you can answer questions based on them, and so that you can suggest reading them:",
            "\n".join([
                "m ".join([
                    f"The blog post titled: '{post.title}'",
                    f"is summarized as: '{post.summary[:self.MAX_CONTEXT_SUMMARY_SIZE]}'",
                    f"and you can read it in the following link: '{post.url}'",
                ])
                for post in context[:self.MAX_CONTEXT_DOCUMENTS_SIZE]
            ]),
            f"Now, answer the following question in a separate paragraph (but always referring to topics summarized above) and, in another paragraph give me a reference (the title and the link) to only one of those blog posts explaining why I should read it: '{question}'",
        ])
        answer: str = self.post(
            prompt=prompt,
            limit=limit,
        )
        print('Answer:', answer)
        return answer

    def summarize(self, text: str, limit: int = 50) -> str:
        """
        Summarizes a text using the GPT API.
        """
        summary: str = self.post(
            prompt=f'Summarize the following text: {text}',
            limit=limit,
        )
        print('Summary:', summary)
        return summary

    def get_goal(self, text: str, limit: int = 50) -> str:
        """
        Extracts the main idea of the text.
        """
        goal: str = self.post(
            prompt=f'What is the goal of what is described in the following text and how other people could benefit from it: {text}',
            limit=limit,
        )
        print('Main idea:', goal)
        return goal

    def get_keywords(self, text: str, limit: int = 20) -> List[str]:
        """
        Summarizes a text using the GPT API.
        """
        keywords: str = self.post(
            prompt=f'Give me a list of the most important 50 words, entities, and their synonims in the following text, separated by comma without any other text than the words: {text}',
            limit=limit,
        )
        print('Keywords:', keywords)
        return [
            word.strip()
            for word in keywords.split(',')
        ]
