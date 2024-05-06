# Agent Builder for IT Service Desk Automation
This folder contains code and resources for using Google Cloud's Agent Builder in the context of IT Service Desk automation. These are companion resources to the Youtube video:

[![Watch the video](https://img.youtube.com/vi/iBiyOl_pH-8/default.jpg)](https://youtu.be/iBiyOl_pH-8)

## Resources in this repo
* `agents/default/config.md` contains the configurations used for the Default Agent
* `agents/info/config.md` contains the configurations used for the Info Agent
* `agents/ticket/config.md` contains the configurations used for the Ticket Agent
* `agents/info/tools` directory contains details and data for setting up the data store tool
* `agents/ticket/tools` directory contains details and code for setting up the OpenAPI tool, including:
  * `main.py` is the function to simulate the creation of an IT service desk ticket. This function is to be deployed on Cloud Functions
  * `requirements.txt` is the Python requirements file for the function
  * `api-spec.yaml` is the OpenAPI spec for the function

## Setup
See video for full instructions