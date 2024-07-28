import functions_framework
import json
import os
from google.cloud import discoveryengine_v1
from google.protobuf.json_format import MessageToDict
from typing import Optional, List, Dict

PROJECT_ID = os.getenv("PROJECT_ID")
DATASTORE_ID = os.getenv("DATASTORE_ID")
DATASTORE_LOCATION = os.getenv("DATASTORE_ID", "global")


@functions_framework.http
def retrieve(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
        page_size (int): optional number of page size to retrieve
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)

    if request_json and "search_query" in request_json:
        search_results = get_search_results(request_json["search_query"])
        return format_search_results(search_results)
    return ""


def format_search_results(
    response_pager: discoveryengine_v1.SearchResponse,
) -> List[Dict]:
    response_pager_dict = MessageToDict(response_pager._pb)
    return (
        "{response:"
        + json.dumps(
            [
                result["document"]["structData"]
                for result in response_pager_dict["results"]
            ]
        )
        + "}"
    )


def get_search_results(
    search_query: str, page_size: Optional[int] = 3
) -> discoveryengine_v1.SearchResponse:
    """Performs a search query in Discovery Engine and returns the results.

    Args:
        search_query: The search query text.
        page_size: (Optional) The max number of search results to return per page. Defaults to 3.

    Returns:
        A SearchResponse object containing the search results.
    """

    # Create the Discovery Engine client
    client = discoveryengine_v1.SearchServiceClient(client_options=None)

    # Construct the full resource name of the serving config
    serving_config = client.serving_config_path(
        project=PROJECT_ID,
        location=DATASTORE_LOCATION,
        data_store=DATASTORE_ID,
        serving_config="default_config",
    )

    # Build the search request
    request = discoveryengine_v1.SearchRequest(
        serving_config=serving_config, query=search_query, page_size=page_size
    )

    # Perform the search and return the response
    return client.search(request)
