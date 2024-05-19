import os
import google.generativeai as genai
from order_db import OrderDatabase
from external import ExternalSystems

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
MODEL_NAME = "gemini-1.0-pro"  # "gemini-1.5-pro-latest"

genai.configure(api_key=GOOGLE_API_KEY)


def main():
    try:
        db = OrderDatabase()
        db.load_fake_data()

        ext = ExternalSystems()

        system_instruction = """You are a customer service agent.
                            You can retrieve information about  orders or create support tickets
                            If a customer wants information about the order, you will ask for the order ID if they haven't already proactively provided it, and you will then use the available tool to retrive the information.
                            If a customer express any kind of issue they're experiencing, whether or not it is related to an order, or if they want to connect with a human, you will first ask them if they want you to create a support ticket.
                            - If they say yes, ask for more details about their issue if they haven't already proactively provided details. Then, use the available tools to first retrieve their email addresses, and then create a support ticket.
                            - If they say no, politely ask if there's anything else you can help them with
                            - You must not try to solve the problem yourself or ask them anything else beyond a description of their issue
                            If a customer ends the conversation or indicates that it doesn't need anything else from you, thank them and wish them a great day"""

        if "1.5" in MODEL_NAME:
            model = genai.GenerativeModel(
                model_name=MODEL_NAME,
                tools=[
                    db.get_order_status,
                    ext.get_user_email,
                    ext.create_support_ticket,
                ],
                system_instruction=system_instruction,
            )
        else:  # 1.0 does not support system instructions
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

        while True:
            user_input = input("User: ")

            if "1.5" in MODEL_NAME:
                response = chat.send_message(user_input)
            else:
                prompt_text = (
                    f"##System instructions\n{system_instruction}\n{user_input}"
                )
                response = chat.send_message(prompt_text)

            print(f"Bot: {response.text}")

    except Exception as e:
        print("Error", e)

    finally:
        # Close DB connection and dump chat history
        db.close()
        print(chat.history)


if __name__ == "__main__":
    main()
