import functions_framework
import json
from datetime import datetime
from google.cloud import firestore
import vertexai
from vertexai.language_models import TextGenerationModel

@functions_framework.http
def submit_issue(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
    Returns:
        issue_id (str): issue identifier
    """
    
    alias = request.get_json()['corporate_alias']
    issue = request.get_json()['issue']
    if not alias or not issue:
        raise "Input malformed"

    now = datetime.now()
    dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
    
    # log request with date and time
    print(f"[{dt_string}] Request for ticket creation from {alias}@")

    try:
         issue_id = submit_ticket(alias, issue, categorize_ticket(issue))
    except Exception as e:
        print("Failed to write to Firestore", e)

    response_dict = {
        'issue_id': issue_id
    }
    return json.dumps(response_dict)




def submit_ticket(
    alias: str,
    issue: str,
    issue_cat: str,
):
    db = firestore.Client(project='PROJECT_ID')
    
    data = {"from_alias": alias, "issue": issue, "category": issue_cat}

    update_time, issue_ref = db.collection("issues").add(data)
    print(f"Added Firestore document with id {issue_ref.id}")

    return issue_ref.id


def categorize_ticket(
    issue: str,
):
    vertexai.init(project="PROJECT_ID", location="us-central1")
    parameters = {
        "candidate_count": 1,
        "max_output_tokens": 256,
        "temperature": 0.2,
        "top_p": 0.8,
        "top_k": 40
    }
    model = TextGenerationModel.from_pretrained("text-bison")
    response = model.predict(
        """Multi-choice problem: Define the category of the ticket
    Categories:
    - Password
    - Printer
    - Network

    Ticket: I forgot my password
    Category: Password

    Ticket: I can\'t seem to be able to print a document, I need help
    Category: Printer

    Ticket: I\'ve tried connecting to the office WiFi but it\'s not working
    Category: Network

    Ticket: The Wifi seems really slow
    Category: Network

    Ticket: I\'m unable to connect to the printer
    Category: Printer

    Ticket: I need to reset my password
    Category: Password

    Ticket: Placeholder
    Category:
    """,
        **parameters
    )
    print(f"Response from Model: {response.text}")

    return response.text