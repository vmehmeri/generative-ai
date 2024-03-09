import httpx
import functions_framework

@functions_framework.http
def search_wiki(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    query = request.get_json()['query']

    
    return wikipedia(query)

def wikipedia(q):
    info = {f"context_{n}":c for n,c in enumerate(httpx.get("https://en.wikipedia.org/w/api.php", params={"action": "query", "list": "search", "srsearch": q, "format": "json"}).json()["query"]["search"]) if n<5}
       
    return str(info)