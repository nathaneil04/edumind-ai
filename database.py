import json 
import os
import re
from google import genai

class EduMindAssistant:
    def __init__(self, dataset_path: str = "academic_answers.json", api_key: str = None):
        self.dataset = []
        self.is_loaded = False
        self.load_dataset(dataset_path)
        
        # Gemini API Key mula sa iyong Google AI Studio account
        HARDCODED_KEY = os.getenv("GEMINI_API_KEY")        
        self.api_key = api_key or HARDCODED_KEY
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.conversation_history = []

    def load_dataset(self, path: str):
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.dataset = json.load(f)
                self.is_loaded = True
        except (FileNotFoundError, json.JSONDecodeError):
            self.dataset = []
            self.is_loaded = False

    @staticmethod
    def extract_course_code(course_name: str) -> str:
        match = re.search(r'\((.*?)\)', course_name)
        return match.group(1) if match else course_name

    def clear_history(self):
        self.conversation_history = []

    def _generate_llm_response(self, user_prompt: str, course_name: str) -> str:
        if not self.client:
            return None
        
        try:
            system_instruction = (
                f"You are EduMind AI, a specialized study assistant for students enrolled in {course_name}. "
                "Maintain active awareness of previous conversation turns to answer follow-up questions accurately."
            )
            
            full_prompt = f"System: {system_instruction}\n\n"
            for msg in self.conversation_history:
                full_prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
            full_prompt += f"User: {user_prompt}"

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt
            )
            
            reply = response.text
            self.conversation_history.append({"role": "user", "content": user_prompt})
            self.conversation_history.append({"role": "model", "content": reply})
            
            return reply
        except Exception:
            return None

    def get_response(self, user_prompt: str, course_name: str) -> str:
        query = user_prompt.lower().strip()
        code = self.extract_course_code(course_name)

        if self.is_loaded and self.dataset:
            for item in self.dataset:
                course_match = item.get("course_code") == code or item.get("course") == course_name
                if course_match and item.get("user_prompt", "").lower() == query:
                    reply = item.get("response", "")
                    self.conversation_history.append({"role": "user", "content": user_prompt})
                    self.conversation_history.append({"role": "model", "content": reply})
                    return reply

        llm_response = self._generate_llm_response(user_prompt, course_name)
        if llm_response:
            return llm_response

        fallback = f"I am ready to assist with your {course_name} studies. Ask any question to get started!"
        self.conversation_history.append({"role": "user", "content": user_prompt})
        self.conversation_history.append({"role": "model", "content": fallback})
        return fallback

# Pag-run ng Assistant
if __name__ == "__main__":
    assistant = EduMindAssistant()
    response = assistant.get_response(
        "Magbigay ng 3 study tips", 
        "Bachelor of Science in Information Technology (BSIT)"
    )
    print(response)