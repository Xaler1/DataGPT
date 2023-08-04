# Data GPT

## Goal
The goal of this project is to use the power of LLMs to bring
together as much functionality as possible. The initial idea is to
use the new functional calling capability of OpenAI models to 
integrate as many different functions as possible. Using functions 
as data sources as well as for completion of tasks.
To that end I attempted to make it as easy as possible to create new 
functions and add them to the model. Using a simple decorator to
convert standard python functions and their docstrings into a format
that can be processed by OpenAI chat models.

One of the big limitations currently is the number of tokens that can be 
processed at once. With the largest (reasonably priced) model
being the gpt-3.5-turbo-16k with 16k tokens.
This was the motivation to add data processing features as well. 
Allowing the model to write arbitrary python code to analyze and transform
dataframes.

The interface is built using streamlit.

