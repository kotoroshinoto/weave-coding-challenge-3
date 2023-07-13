import click
import os
import sys
import re
import json
import requests
import openai
from datetime import datetime
from utils import extract_values
from urlpath import URL
from pathlib import Path

opentargets_base_url = "https://api.platform.opentargets.org/api/v4/graphql"
open_targets_base = URL(opentargets_base_url)
open_targets_schema_url = open_targets_base / "schema"
schema_response = open_targets_schema_url.get()
open_targets_schema = schema_response.content.decode()

openai.api_key = os.environ.get("OPENAI_API_KEY")
models = openai.Model.list()
model_ids = []
for item in models['data']:
    model_ids.append(item['id'])
sorted(model_ids)

def generate_query_for_opentargets_using_human_language(gpt_model, prompt_templates, user_input):
    completion_prompt = "\nGiven this schema, what resources would be required to retrieve the results of this query: "
    resource_messages = [{'role':'user', 'content': "The following is the schema provided by Open Targets for their graphQL API:\n" + open_targets_schema + "\n\n" + completion_prompt + user_input}]
    resource_response = openai.ChatCompletion.create(
        model=gpt_model,
        messages=resource_messages,
        temperature=0,
        max_tokens=250,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["###"],
    )
    resource_response_message = resource_response['choices'][0]['message']
    graphql_messages = [
        {
            'role':'user',
            'content': resource_response_message['content']
        },
        {
            'role':'user',
            'content': 'Here are some example queries: \n' + prompt_templates
        },
        {
        'role':'user',
        'content': 'Please do not include extra variables not in the examples. Do not tranform or translate any drug, disease or gene names into chemblId, EFO ID, or ENSEMBL ID. Follow the examples strictly. Do not include extra variables in the query. Please use the resources listed and the example queries to generate a graphQL expression that fetches all the required data to complete the query: "' + user_input + "; query generated_query {\n  search("
        }
    ]
    graphql_response = openai.ChatCompletion.create(
        model=gpt_model,
        messages=graphql_messages,
        temperature=0,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["###"],
    )
    return "query generated_query {\n  search(" + graphql_response['choices'][0]['message']['content']

def store_custom_query(user_input, query_string):
    query_file = "query_" + datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") + ".txt"
    with open(query_file, "w") as f:
        f.write(f"# User input: {user_input}\n")
        f.write(query_string)
        #print(f"\nCustom graphQL query was written to file: {query_file}")
        
def perform_opentargets_query(query):
    # Perform POST request and check status code of response
    # This handles the cases where the Open Targets API is down or our query is invalid
    try:
        response = open_targets_base.post(json={"query": query})
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err, file=sys.stderr)
        print(response.content.decode(), file=sys.stderr)
        return None
    except:
        the_type, the_value, the_traceback = sys.exc_info()
        print("exception occurred: %s -> %s" % (str(the_type), str(the_value)), file=sys.stderr)
        return None
    
    return response.content.decode()

def handle_input(test_mode, model, template_file_path, user_input):
    with open(template_file_path, "r") as f:
        prompt_templates = f.read()
    generated_query = generate_query_for_opentargets_using_human_language(model, prompt_templates, user_input)
    if test_mode:
        store_custom_query(user_input, generated_query)
    query_result = perform_opentargets_query(generated_query)
    return query_result

@click.command()
@click.option('--test', is_flag=True, default=False, help="activate test mode. when active, the generated query and user input will be saved in a datetime-stamped text file.")
@click.option('--templates', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True), default=str(Path("./graphql_schema.txt").absolute()), help="path to some example templates to use with gpt model to inform structure of generated queries.")
@click.option('--model', type=str, default="gpt-4", help="openAI model to use. Available models: [%s] default: gpt-4" % ('\n'.join(model_ids)))
@click.argument('user_input', type=str, required=True)
def main(model, test, user_input, templates):
    query_result = handle_input(test, model, templates, user_input)
    if query_result is None:
        print("An error was detected. The user input did not generate a functional query")
    else:
        print(query_result)

if __name__ == "__main__":
    main()
