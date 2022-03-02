# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
import json
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import pyTigerGraph as tg

################# TigerGraph Credentials ######################""
# Connection parameters
hostName = "https://language.i.tgcloud.io/"
userName = "tigergraph"
password = "tigergraph"

conn = tg.TigerGraphConnection(host=hostName, username=userName, password=password)

print("initial connection")

conn.graphname="WordNet"
secret = conn.createSecret()
print(secret)
authToken = conn.getToken(secret)
authToken = authToken[0]
print(authToken)
conn = tg.TigerGraphConnection(host=hostName, graphname="WordNet", username=userName, password=password, apiToken=authToken)
print("Connected")

class ActionWordDef(Action):

    def name(self) -> Text:
        return "action_word_definition"   # !!!! this return value must match line 55 of domain.yml  [ Step 4.a ]

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        prediction = tracker.latest_message['entities'][0]['value']
        
        if prediction:
            query_response = conn.runInstalledQuery("get_definition",{"word_query": prediction})
            
            r=query_response[0]
            w=r["words"]
            vals=[]
            for wd in w:
                vals.append(wd["attributes"]["definition"])
            value = "\n".join(vals)
        
        counts = len(vals)
        if counts > 0:
            dispatcher.utter_message(text="Here is the list of definitions:")
            dispatcher.utter_message(text=value)
            dispatcher.utter_message(text="========================")
        else:
            dispatcher.utter_message(text="no definition found")

        return []

class ActionHypernym(Action):

    def name(self) -> Text:
        return "action_hypernym"   # !!!! this return value must match line 55 of domain.yml  [ Step 4.a ]

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        print(tracker.latest_message)
        prediction = tracker.latest_message['entities'][0]['value']

        if prediction:
            query_response = conn.runInstalledQuery("get_synonyms",{"word_query": prediction})
            r=query_response[0]
            w=r["definition"]
            vals=[]
            for wd in w:
                vals.append(wd)
            value = "\n".join(vals)
            dispatcher.utter_message(text="Here is the list of hypernyms:")
            dispatcher.utter_message(text=value)
            # dispatcher.utter_message(words[0])
            dispatcher.utter_message(text="========================")
        else:
            dispatcher.utter_message(text="No matched words")

        return []

class ActionHyponym(Action):

    def name(self) -> Text:
        return "action_hyponym"   # !!!! this return value must match line 55 of domain.yml  [ Step 4.a ]

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        print(tracker.latest_message)
        prediction = tracker.latest_message['entities'][0]['value']

        if prediction:
            query_response = conn.runInstalledQuery("get_related_words",{"word_query": prediction})
            r=query_response[0]
            w=r["definition"]
            vals=[]
            for wd in w:
                vals.append(wd)
            value = "\n".join(vals)
            dispatcher.utter_message(text="Here is the list of hyponyms:")
            dispatcher.utter_message(text=value)
            # dispatcher.utter_message(words[0])
            dispatcher.utter_message(text="========================")

        return []

class ActionAntonyms(Action):

    def name(self) -> Text:
        return "action_antonym"   # !!!! this return value must match line 55 of domain.yml  [ Step 4.a ]

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        print(tracker.latest_message)
        prediction = tracker.latest_message['entities'][0]['value']

        if prediction:
            query_response = conn.runInstalledQuery("get_antonyms",{"word_query": prediction})
            r=query_response[0]
            w=r["definition"]
            vals=[]
            for wd in w:
                vals.append(wd)
            value = "\n".join(vals)
            dispatcher.utter_message(text="Here is the list of antonyms:")
            dispatcher.utter_message(text=value)
            # dispatcher.utter_message(words[0])
            dispatcher.utter_message(text="========================")

        return []

class ActionAllConnections(Action):

    def name(self) -> Text:
        return "action_all_connections"   # !!!! this return value must match line 55 of domain.yml  [ Step 4.a ]

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        print(tracker.latest_message)
        prediction = tracker.latest_message['entities'][0]['value']

        if prediction:
            query_response = conn.runInstalledQuery("get_all_connections",{"word_query": prediction})
            r=query_response[0]
            w=r["definition"]
            vals=[]
            for wd in w:
                vals.append(wd)
            value = "\n".join(vals)
            dispatcher.utter_message(text="Here is the list of related words:")
            dispatcher.utter_message(text=value)
            # dispatcher.utter_message(words[0])
            dispatcher.utter_message(text="========================")

        return []
