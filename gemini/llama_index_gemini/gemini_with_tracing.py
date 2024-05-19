"""Llama index module to interact with Gemini"""
from llama_index.core.llms import ChatMessage
from llama_index.llms.gemini import Gemini
from llama_index.core.tools import BaseTool, FunctionTool
from llama_index.core.agent import FunctionCallingAgentWorker
from traceloop.sdk import Traceloop
import os 


def multiply(a: int, b: int) -> int:
    """Multiple two integers and returns the result integer"""
    return a * b

multiply_tool = FunctionTool.from_defaults(fn=multiply)

Traceloop.init(
  disable_batch=True, 
  api_key=os.environ["TRACELOOP_API_KEY"]
)

class LlamaIndexGemini:
    def __init__(self, system_instruction: str, model_name: str = "gemini-pro"):
        self.gemini = Gemini(model_name=f"models/{model_name}")
        self.messages = [
            ChatMessage(role="system", content=system_instruction)
        ]

    def send_user_message(self, text_prompt: str):
        self.messages.append(
            ChatMessage(
                role="user", content=text_prompt
            )
        )
        response = self.gemini.chat(self.messages)
        
        self.messages.append(
            ChatMessage(
                role="assistant", content=response
            )
        )

        return response
    
    def get_chat_history(self):
        return self.messages


