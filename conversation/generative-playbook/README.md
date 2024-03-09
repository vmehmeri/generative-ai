# Sample Generative Playbook Tool
[Demo video](https://youtub.be/jbB1s43f__o) 

In this directory you will find the following source files:

* `openapi_schema.yaml`: this is the OpenAPI schema for the API to be used as a tool within a generative playbook
* `search_wiki_function.py`: this is the implementation of the API to be deployed in Cloud Functions
* `requirements.txt`: this is the requirements file listing the dependencies for the code.

## Pre-requisites
You will need a Google Cloud project with billing enabled. You will also need to have permissions to create Cloud Functions at a minimum.

## Deploy
As a first step, you will need to create a Cloud Function. You can do so by navigating to Cloud Functions in the Google Cloud console. You don't need to customize any of the default settings, simply press **Next** and then copy and paste the code from `search_wiki_function.py` into the inline code editor. Just make sure you replace the **Entrypoint** field with `search_wiki` (the name of the method in the function that is triggered by the HTTP request).

**note**: if you choose to only allow authenticated requests to your Cloud Function, you will need to assign the [Dialogflow service agent](https://cloud.google.com/iam/docs/service-agents#dialogflow-service-agent) the following IAM roles:

* Cloud Run Invoker
* Cloud Functions Invoker


Once you have your Cloud Function deployed, then navigate to **Vertex AI Search and Conversation**, click on **New App**, and choose the option **Generative playbook**.

## Configure
See [this video](https://youtub.be/jbB1s43f__o) where I walk through the process of configuring a generative playbook with a tool that calls the search wiki function.