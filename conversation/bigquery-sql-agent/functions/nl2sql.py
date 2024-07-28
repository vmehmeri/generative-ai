import functions_framework
from google.cloud import bigquery
from vertexai.generative_models import GenerativeModel
import pandas as pd
from typing import Tuple
import re
import logging
import functools
import os
import warnings

warnings.filterwarnings("ignore", message="BigQuery Storage module not found") 

PROJECT_ID = os.getenv("PROJECT_ID")

TABLE_NAMES = (
    f"{PROJECT_ID}.thelook_ecommerce.users",
    f"{PROJECT_ID}.thelook_ecommerce.orders",
    f"{PROJECT_ID}.thelook_ecommerce.products",
    f"{PROJECT_ID}.thelook_ecommerce.order_items",
    f"{PROJECT_ID}.thelook_ecommerce.inventory_items",
    f"{PROJECT_ID}.thelook_ecommerce.distribution_centers",
    f"{PROJECT_ID}.thelook_ecommerce.events",
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

_current_dir = os.path.dirname(__file__)

@functions_framework.http
def generate_sql_and_retrieve(request):
    """HTTP Request handler for use with Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)

    if request_json and "question" in request_json:
        question = request_json["question"]
    else:
        return "{'response': ''}"

    try:
        result_md = generate_sql_and_retrieve_as_markdown(question, use_reflection=True)
    except Exception as e:
        logger.error("An error occurred trying to retrieve the data", exc_info=True)
        return "{'response': 'An error occurred trying to retrieve the data'}"

    return "{'response': '" + result_md + "'}"


def generate_sql_and_retrieve_as_markdown(question: str, use_reflection=True) -> str:
    """Generates SQL query using an LLM, runs the query against BigQuery, and returns the result as a Markdown-formatted string"""
    logger.info(f"Generating query...")
    query, schemas_and_rows = generate_sql(question)
    if use_reflection:
        logger.info(f"Analyzing with reflection...")
        query = reflect_on_generated_sql(
            question, schemas_and_rows, query, "gemini-1.5-pro"
        )

    logger.info(f"Generated query: {query}")
    result_df = _query_bigquery(query)
    results_md = result_df.to_markdown()
    logger.debug(f"Converting dataframe to markdown. Got {results_md}")
    return results_md


def _render_prompt(prompt_name: str, **kwargs) -> str:
    with open(f"{_current_dir}/{prompt_name}.template", "r", encoding="utf-8") as file:
        prompt_template = file.read().strip()
    try:
        return prompt_template.format(**kwargs)
    except KeyError as e:
        raise KeyError(f"Missing required variable: {e}")


@functools.lru_cache(maxsize=8)
def _query_bigquery(query: str) -> pd.DataFrame:
    # Initialize the BigQuery client
    client = bigquery.Client(project=PROJECT_ID)

    # Run the query
    logger.info("Querying BigQuery...")
    query_job = client.query(query)

    # Fetch the results
    try:
        results = query_job.result()
    except Exception as e:
        logger.debug(f"Query failed: {e}")
    logger.debug(f"Query result: {results}")

    # Convert to DataFrame
    logger.debug("Converting results to dataframe...")
    df = results.to_dataframe()

    return df


def _extract_sql_from_markdown(markdown_str: str) -> str:
    """Extract the SQL code delimited by triple backticks"""
    pattern = r"```(?:\w+)?\s*(.*?)```"
    clean_markdown_str = markdown_str.replace("```googlesql", "```").replace(
        "```sql", "```"
    )
    match = re.search(pattern, clean_markdown_str, re.DOTALL)

    if match:
        extracted = match.group(1).strip()
        return extracted

    logger.warn("Could not extract SQL from markdown. Falling back to original string.")
    return markdown_str  # fallback to returning the original string


def _get_top_n_rows_as_string(table: str, n: int) -> str:
    """Gets a string listing the top n rows from the given table"""

    client = bigquery.Client(project=PROJECT_ID)
    logger.debug(f"Fetching {n} rows from {table}")
    intro_str = f"Sample rows for table: `{table}`:\n\n"
    query_str = f"SELECT * FROM `{table}` ORDER BY RAND() LIMIT {n};"
    result_df = client.query(query_str).result().to_dataframe()
    return intro_str + str(result_df) + "\n\n"


@functools.lru_cache(maxsize=128)
def _get_schemas_and_sample_rows(table_names: Tuple[str], num_rows: int) -> str:
    """Get schemas and sample rows for all tables as a single string"""
    client = bigquery.Client(project=PROJECT_ID)
    logger.info("Getting schemas and sample rows")
    schemas_and_rows_str = ""
    for table in table_names:
        logger.debug(f"Getting schema for table {table}...")
        table_split = table.split(".")
        querystring = f"""
        SELECT
        column_name,data_type
        FROM
        `{".".join(table_split[:-1])}`.INFORMATION_SCHEMA.COLUMNS
        WHERE
        table_name = "{table_split[-1]}";
        """
        schemas_and_rows_str += f"Schema for table: `{table}`:\n\n"
        tmp = client.query(querystring).result().to_dataframe()

        schemas_and_rows_str += str(tmp) + "\n\n"
        schemas_and_rows_str += _get_top_n_rows_as_string(table, num_rows)

    return schemas_and_rows_str


@functools.lru_cache(maxsize=16)
def generate_sql(question: str, model_name: str = "gemini-1.5-flash") -> str:
    """Generates SQL query using an LLM"""
    schemas_and_rows = _get_schemas_and_sample_rows(TABLE_NAMES, 3)
    prompt = _render_prompt(
        "generation_prompt", schemas_and_rows=schemas_and_rows, question=question
    )
    gen_llm = GenerativeModel(model_name)
    try:
        logger.info(f"Prompting {model_name}")
        result = gen_llm.generate_content(prompt).candidates[0].content.parts[0].text
        return _extract_sql_from_markdown(result), schemas_and_rows
    except Exception:
        logger.error(f"Failed to generate or extract query", exc_info=True)
        raise


def reflect_on_generated_sql(
    question: str,
    schemas_and_rows: str,
    generated_sql: str,
    model_name: str = "gemini-1.5-flash",
) -> str:
    """Reflects on the generated SQL"""
    prompt = _render_prompt(
        "reflection_prompt",
        schemas_and_rows=schemas_and_rows,
        question=question,
        answer=generated_sql,
    )

    refl_llm = GenerativeModel(model_name)
    try:
        logger.info(f"Prompting {model_name}")
        result = refl_llm.generate_content(prompt).candidates[0].content.parts[0].text
        sql = _extract_sql_from_markdown(result)
        if sql == result:
            return generated_sql  # Extraction failed, fallback

        return sql
    except Exception:
        logger.error(f"Failed to generate or extract query", exc_info=True)
        return generated_sql  # Fallback
