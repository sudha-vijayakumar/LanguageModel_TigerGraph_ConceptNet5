# Towards Conversational AI with TigerGraph + RASA + ConceptNet5

This is a complete solution package for representing ConceptNet5, WordNet as TigerGraphs' and building a Dictionary application using the RASA platform. 

> Technical Blog

A detailed overview of the project is presented in the below technical article:
- https://medium.com/@sudha.vijayakumar_74093/a-common-sense-word-network-with-tigergraph-573745e4504d


> Hands-On Video Tutorial

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/Y1s2IwjFzKM/0.jpg)](https://www.youtube.com/watch?v=Y1s2IwjFzKM)

# Steps to run this solution:

> Prerequisites:
  - Python3 runtime
  - Jupyter notebook
  - RASA 

> Step-0: Clone the repository

  - git clone https://github.com/sudha-vijayakumar/LanguageModel.git
  
> Step-1/2: Data Gathering & Preprocessing - ConceptNet5, WordNet 

  - Run 1_WordNet.ipynb
  - Run 2_MergeWordNet-ConceptNet.ipynb
  - Run 3_Preprocess.ipynb
  
>  Step-3: Load ConceptNet5 As TigerGraph


  >> Unique Edge: ConceptNet5
  - Run 6_LanguageModel_CN_UniqueEdge.ipynb
  ** pic
  
>  Step-4: Building Dictionary Bot with RASA + TigerGraph ConceptNet5

  - cd WIKI_Chatbot
  
  >> Terminal-1:
  - $ rasa train
  - $ rasa run -m models --enable-api --cors "*" --debug

  >> Terminal-2:
  - $ rasa run actions

> **NOTE:**
This help page will not go into the depth of RASA, TigerGraph functionalities. This help page will touch base and demo how ConceptNet5 can be loaded into TigerGraph and integrated with RASA to implement a dictionary bot.


## Putting things to work

### Step-1/2: **(Language Graphs)** Step-1/2: Data Gathering & Preprocessing - ConceptNet5, WordNet 

#### Step-1/2a: WordNet


#### Step-1/2b: ConceptNet5

  
### Step-3: **(TigerGraph)** Load ConceptNet5, WordNet As TigerGraph 

There are 3 different variations of the language graphs. Run the corresponding jupyter notebook to generatee the desired language graphs.

#### Step-3a: WordNet, ConceptNet5 with Single edge
  - Run 4_LanguageModel_SingleEdge.ipynb
  -   
#### Step-3b: WordNet with Unique edges
 - Run 5_LanguageModel_WN_UniqueEdge.ipynb
 
#### Step-3c: ConceptNet5 with Unique edges
  - Run 6_LanguageModel_CN_UniqueEdge.ipynb


### Step-4: **(RASA)** Building Dictionary Bot with RASA + TigerGraph ConceptNet5
#### Step-4a: Install RASA

Open a new terminal and setup RASA using the below commands:

- $ python3 -m virtualenv -p python3 .
- $ source bin/activate
- $ pip install rasa

#### Step-4b: Create new RASA project
- $ rasa init

After the execution of the above command, you will be prompted to enter project directory and name as desired. In this case, project named 'WIKI_Chatbot' will be created in the current directory as shown below,
<p align="center">
<img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%201.38.06%20AM.png" width="700" height="450">
</p>

Below is a kick-off conversation with the newly created chatbot,
<p align="center">
<img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%201.40.48%20AM.png" width="700" height="450">
</p>

Ya, that's quite simple to create a chatbot now with RASA!

#### Step-4c: Define intents, stories, action triggers
Now, navigate to the project folder WIKI_Chatbot/data and modify the default nlu.yml and rules.yml files by adding intents, rules for our dictionary usecase as show below,

<p align="center">
<img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%201.43.43%20AM.png">
</p>

<p align="center">
<img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%201.43.59%20AM.png" width="700" height="450">
</p>

#### Step-4d: Install the TigerGraph python library using pip with the below command,
- pip install pyTigerGraph

#### Step-1e: Define action endpoints
Now, navigate to the project folder WIKI_Chatbot/actions and modify the actions.py file to include TigerGraph connection parameters and action definitions with the respective GSQL querying endpoints as show below,


<p align="center">
<img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%201.47.29%20AM.png" width="700" height="450">
</p>

<p align="center">
<img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%201.50.07%20AM.png" width="700" height="450">
</p>

Add the defined action method to the domain.yml as shown below,

<p align="center">
<img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%201.46.21%20AM.png" width="700" height="450">
</p>

Here, 'get_word_definition' is the name of the insstalled GSQL query in the tgcloud database. We will go through each query used in the actions in the next section.

With this step, we are done with the installation and configuration of the RASA chatbot.

### Step-5: **(gSql Queries)** Create & Install gsql queries

 

### Step-6: **(Web UI)** Setting up a web ui for the RASA chatbot

- In this work, we are using an open-source javascript-based chatbot UI to interact with the RASA solution we implemented in Step-1.
- The RASA server endpoint is configured in the widget/static/Chat.js as shown below,
 
  <p align="center">
  <img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%202.17.45%20AM.png" width="700" height="450">
  </p>

All right, we are one step close to seeing the working of the TigerGraph and RASA integration.

### Step-7: **(RASA+TigerGraph)** Start RASA and run Actions

Run the below commands in separate terminals,

Terminal-1:
- $ rasa train
- $ rasa run -m models --enable-api --cors "*" --debug

Terminal-2:
- $ rasa run actions

### Step-8: **(ChatBot UI)** Open Chatbot User interface

- Unzip ChatBot_Widget folder.
- Hit open ChatBot_Widget/index.html to start interacting with the TigerBot movie recommendation engine!

Yes, we are DONE! 

I hope this source is informative and helpful.


# References:
https://medium.com/analytics-vidhya/integrating-rasa-chatbot-with-django-web-framework-f6cb71c58467
https://github.com/JiteshGaikwad/Chatbot-Widget/

