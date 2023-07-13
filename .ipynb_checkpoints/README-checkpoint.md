## Coding Challenge-3: Natural Language Queries Against a Structural Database

This repo is forked from Onuralp Soylemez's (@cx0) repo: https://github.com/cx0/chatGPT-for-genetics

The goal of this coding challenge is to build a function that takes a natural language instruction or a question, and returns an appropriate response using using Open Targets API endpoints [Open Targets Platform GraphQL](https://platform-docs.opentargets.org/data-access/graphql-api).  

You may use Onuralp's scripts as starting point, or you can write it from scratch. 


### Tasks:
**1. Handle single step queries**
e.g. "What are the targets of vorinostat?", "Find drugs that are used for treating ulcerative colitis." etc.

**2. 2-step queries**
e.g. "Which diseases are associated with the genes targetted by fasudil?", "Show all the diseases that have at least 5 pathways associated with Alzheimer"

### Expectations:
- You can build the solution on Jupyter notebook, but we prefer to see as a CLI functionality
- The response should list the queried entities, no extra paragraphs or text. 
- We will test the solution on a set of held out instructions and questions (10 cases for each task). 
- You may need an OpenAI account for OpenAI api or a similar LLM API access. 


