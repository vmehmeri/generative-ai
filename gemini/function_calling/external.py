"""External APIs and Integrations"""

import json


class ExternalSystems:

    @classmethod
    def get_user_email(cls) -> str:
        """Retrieves the email address of the authenticated user"""

        return "john.doe@example.com"

    @classmethod
    def create_support_ticket(
        cls, user_email_address: str, issue_description: str
    ) -> str:
        """
        Creates a customer support ticket in the system.

        This function interacts with the customer support ticketing system to log a new issue
        reported by the user. It captures the user's email address for communication and
        records a detailed description of the problem.

        Args:
            user_email_address (str): The email address of the authenticated user reporting the issue.
            issue_description (str): A clear and concise description of the problem encountered.

        Returns:
            dict: A dictionary containing the details of the created support ticket, including:
                * ticket_id (int): A unique identifier for the ticket.
                * status (str): The initial status of the ticket (e.g., "Open", "Pending").

        Raises:
            ValueError: If the user's email address or issue description is invalid or missing.
            SupportSystemError: If there's an error communicating with the ticketing system.
        """
        if not user_email_address or not issue_description:
            raise ValueError("User email and issue description are required.")

        # Simulate interaction with a ticketing system
        ticket_id = 12345  # Assign a dummy ticket ID
        status = "Open"  # Set the initial status

        ticket_data = {
            "ticket_id": ticket_id,
            "user_email": user_email_address,
            "issue_description": issue_description,
            "status": status,
        }

        # In a real implementation, you would store ticket_data in a database or send it to a
        # ticketing API.

        return json.dumps(ticket_data)
