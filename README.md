# LanguageModel
Solution to retrieve wordnet,conceptnet data to build language graph

> Demo run:

The below video will highlight the runtime of this setup and some sample real-time conversations using the power of RASA + TigerGraph,

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/Y1s2IwjFzKM/0.jpg)](https://www.youtube.com/watch?v=Y1s2IwjFzKM)

# Steps to run this solution:

> Step-0:

  - git clone https://github.com/sudha-vijayakumar/RASA_TigerGraph.git
  
> Step-1: (Scroll down for detailed setup instructions)

  - cd Movie_Chatbot
  
  >> Terminal-1:
  - $ rasa train
  - $ rasa run -m models --enable-api --cors "*" --debug

  >> Terminal-2:
  - $ rasa run actions
  
>  Step-2: (Scroll down for detailed setup instructions)
>  
  - Run tgcloud solution

# Project Overview: Movie recommendations using RASA + TigerGraph

Conversational recommendation systems (CRS) using knowledge graphs is a hot topic as they intend to return the best real-time recommendations to users through a multi-turn interactive conversation. CRS allows users to provide their feedback during the conversation, unlike the traditional recommendation systems. CRS can combine the knowledge of the predefined user profile with the current user requirements to output custom yet most relevant recommendations or suggestions. This work will implement a chatbot using the open-source chatbot development framework - RASA and the most powerful, super-fast, and leading cloud graph database - TigerGraph. 

> **NOTE:**
This help page will not go into the depth of RASA, TigerGraph functionalities. This help page will touch base and demo how TigerGraph can be integrated with RASA.

## Technological Stack

Here is the high-level outline of the technological stack used in this demo project,
<p align="center">
<img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/TechnicalStack.jpg" width="450" height="600">
</p>


## Putting things to work

### Step-1: **(RASA)** Implement language models, user intents and backend actions 

> **Beginner tutorial:** This is a very good spot to learn about setting up a basic chatbot using RASA and understanding the core framework constructs.
  - https://rasa.com/docs/rasa/playground/

#### Step-1a: Install RASA

Open a new terminal and setup RASA using the below commands:

- $ python3 -m virtualenv -p python3 .
- $ source bin/activate
- $ pip install rasa

#### Step-1b: Create new RASA project
- $ rasa init

After the execution of the above command, a new RASA 'Movie_Chatbot' project will be created in the current directory as shown below,
<p align="center">
<img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%201.38.06%20AM.png" width="700" height="450">
</p>

Below is a kick-off conversation with the newly created chatbot,
<p align="center">
<img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%201.40.48%20AM.png" width="700" height="450">
</p>

Ya, that's quite simple to create a chatbot now with RASA!

#### Step-1c: Define intents, stories, action triggers
Now, navigate to the project folder Movie_Chatbot/data and modify the default nlu.yml and rules.yml files by adding intents, rules for our movie recommendation business usecase as show below,

<p align="center">
<img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%201.43.43%20AM.png">
</p>

<p align="center">
<img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%201.43.59%20AM.png" width="700" height="450">
</p>

#### Step-1d: Install the TigerGraph python library using pip with the below command,
- pip install pyTigerGraph

#### Step-1e: Define action endpoints
Now, navigate to the project folder Movie_Chatbot/actions and modify the actions.py file to include TigerGraph connection parameters and action definitions with the respective movie recommendation CSQL query as show below,


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

Here, 'RecommendMovies' is the name of the GSQL query in the tgcloud database which will discuss in detail in the next section.

With this step, we are done with the installation and configuration of the RASA chatbot.

### Step-2: **(TigerGraph)** Setup TigerGraph database and querying APIs

> **Beginner tutorial:** This is a very good spot to learn about setting up a tigergraph database on the cloud and implementing CSQL queries,
  - https://www.tigergraph.com/blog/taking-your-first-steps-in-learning-tigergraph-cloud/

#### Step-2a: Setup tgcloud database
- Go to, http://tgcloud.io/ and create a new account.
- Activate the account.
- Go to, "My Solutions" and click "Create Solution"

  <p align="center">
  <img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%202.00.02%20AM.png">
  </p>
  
- Select the starter kit as shown below then click Next twice.
  <p align="center">
  <img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%202.00.29%20AM.png" width="700" height="450">
  </p>
  
- Provide a solution name, password tags, and subdomain as needed, and then click 'Next'
- Enter Submit and close your eyes for the magic!


And Yes!, the TigerGraph Movie recommendation Graph database is created. Buckle up a few more things to do!

- Go to, GraphStudio and 'Load Data' by selecting the *.csv files and hit the 'play' button as shown below. 
<p align="center">
  <img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%202.03.23%20AM.png">
  </p>
  
- Once the data is loaded, data statistics should display a green 'FINISHED' message as shown below.

  
  <p align="center">
  <img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%202.03.57%20AM.png" width="700" height="450">
  </p>
  
- Go to, 'Write Queries' and implement the CSQL queries here as shown below, 


  <p align="center">
  <img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%202.05.57%20AM.png" width="700" height="450">
  </p>
  
- Save the CSQL query and publish it using the 'up arrow' button.

  
- Lets, test the query by running with a sample input as shown below,
  
  <p align="center">
  <img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%202.06.18%20AM.png" width="700" height="450">
  </p>
  
All Set! The TigerGraph Database is up and running. Are we done? Almost! There is one more thing to do!

#### Step-2b: Configure secret token
- Let's set up the secret key access to the cloud TigerGraph API as it is very crucial to ensure a secure way of providing access to the data. 
- Go to, Admin Dashboard->Users->Management and define a secret key as shown below,

  <p align="center">
  <img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%202.10.56%20AM.png">
  </p>
  
  
  <p align="center">
  <img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%202.11.19%20AM.png">
  </p>
  
- **NOTE:** Please remember to copy the key to be used in the RASA connection configuration (Movie_ChatBot/actions/actions.py)


### Step-3: **(Web UI)** Setting up a web ui for the RASA chatbot

- In this work, we are using an open-source javascript-based chatbot UI to interact with the RASA solution we implemented in Step-1.
- The RASA server endpoint is configured in the widget/static/Chat.js as shown below,
 
  <p align="center">
  <img src="https://github.com/sudha-vijayakumar/RASA_TigerGraph/blob/master/Movie_Chatbot/snapshots/Screen%20Shot%202021-12-28%20at%202.17.45%20AM.png" width="700" height="450">
  </p>

All right, we are one step close to seeing the working of the TigerGraph and RASA integration.

### Step-4: **(RASA+TigerGraph)** Start RASA and run Actions

Run the below commands in separate terminals,

Terminal-1:
- $ rasa train
- $ rasa run -m models --enable-api --cors "*" --debug

Terminal-2:
- $ rasa run actions

### Step-5: **(ChatBot UI)** Open Chatbot User interface

Hit open widget/index.html to start interacting with the TigerBot movie recommendation engine!

Yes, we are DONE! 

I hope this source is informative and helpful.


# References:
https://medium.com/analytics-vidhya/integrating-rasa-chatbot-with-django-web-framework-f6cb71c58467
https://github.com/JiteshGaikwad/Chatbot-Widget/

