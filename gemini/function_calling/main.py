import os
import logging
import google.generativeai as genai
from google.generativeai.types import generation_types
from google.ai.generativelanguage import Candidate
from order_db import OrderDatabase
from external import ExternalSystems


GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
MODEL_NAME = "gemini-1.0-pro"

genai.configure(api_key=GOOGLE_API_KEY)

# Set up logging
logging.basicConfig(
    filename="chatbot.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def main():
    try:
        db = OrderDatabase()
        db.load_fake_data()

    except Exception as e:
        print("Error connecting to database", e)

    ext = ExternalSystems()

    system_instruction = """You are a customer service agent.
    You can retrieve information about  orders or create support tickets
    If a customer wants information about the order, you will ask for the order ID if they haven't already proactively provided it, and you will then use the available tool to retrive the information.
    If a customer express any kind of issue they're experiencing, whether or not it is related to an order, or if they want to connect with a human, you will first ask them if they want you to create a support ticket.
    - If they say yes, ask for more details about their issue if they haven't already proactively provided details. Then, use the available tools to first retrieve their email addresses, and then create a support ticket. Do NOT ask for their email address directly.
    - If they say no, politely ask if there's anything else you can help them with
    - You must not try to solve the problem yourself or ask them anything else beyond a description of their issue
    If a customer ends the conversation or indicates that it doesn't need anything else from you, thank them and wish them a great day"""

    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        tools=[
            db.get_order_status,
            ext.get_user_email,
            ext.create_support_ticket,
        ],
    )

    # Automatic function calling will call the function directly
    # and handle the injection of the response back to the model
    # making our lives easier.
    chat = model.start_chat(enable_automatic_function_calling=True)
    turn_start_idx = 0
    chat_ongoing = True

    while True:
        try:
            user_input = input("User: ")

            # Log user interaction
            logging.info(f"User: {user_input}")

            prompt_text = f"##System instructions\n{system_instruction}\n{user_input}"
            # Call it with `stream=True` to receive response chunks as they are generated:
            response = chat.send_message(prompt_text)

            while turn_start_idx < len(chat.history):
                logging.debug(chat.history[turn_start_idx].parts[0])
                turn_start_idx += 1

            logging.info(f"Bot: {response.text}")

            # Here you would want to send the bot response to the frontend
            print(f"Bot: {response.text}")

        except generation_types.BlockedPromptException as bpe:
            print("Bot: I am sorry, but I am unable to assist with that request.")
            logging.warning("BlockedPromptException: ", bpe)
        except generation_types.StopCandidateException as sce:
            if response and response.candidates:
                reason = response.candidates[0].finish_reason
            else:
                reason = "Unknown"
            print("Bot: Sorry, something went wrong. Reason:", reason)
            logging.error("StopCandidateException: ", sce)
        except generation_types.BrokenResponseError as bke:
            print("Bot: Sorry, something went wrong")
            logging.error("BrokenResponseError: ", bke)
        except generation_types.IncompleteIterationError as iie:
            print("Bot: Sorry, something went wrong")
            logging.error("IncompleteIterationError: ", iie)
        except Exception as e:
            print("Bot: Sorry, something went wrong.")
            logging.error("An unexpected error occurred:", e)
            chat_ongoing = False
        finally:
            if not chat_ongoing:
                # Close DB connection and dump chat history
                db.close()


if __name__ == "__main__":
    main()
