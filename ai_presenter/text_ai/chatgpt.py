import json
import os
import openai
import logging
from ai_presenter.text_ai.base import TextAi
from ai_presenter.database import Database, Scene
from ai_presenter.tools.json_trim import json_trim
# import ai_presenter.config.env_vars

class ScriptChatGPT:
    def __init__(self):
        self.messages = [
            {
                "role": "system",
                "content": "You create plots with characters and output in YAML",
            },
            {
                "role": "user",
                "content": "a plot with 4 scenes about a space war in Europa",
            },
            {
                "role": "system",
                "content": '''
config:
  ai_config:
    text_ai_filename: europa.txt
    voice_ai_filename: europa.wav
    chatgpt_config:
      style: you are a suspenseful storyteller

actors:
  - name: Captain Ryan Thompson
    description: fearless leader of a space fleet
    voice_type: unused
    age: middle_aged
    height: 6 feet
    gender: male
    accent: american
  - name: Lieutenant Ava Ramirez
    description: brilliant pilot and strategist
    voice_type: unused
    age: young
    height: 5 feet 5 inches
    gender: female
    accent: american
  - name: Sergeant Marcus Chen
    description: skilled technician and weapons expert
    voice_type: unused
    age: old
    height: 5 feet 10 inches
    gender: male
    accent: english
  - name: Dr. Sophia Collins
    description: brilliant scientist specializing in alien life forms
    voice_type: unused
    age: middle_aged
    height: 5 feet 8 inches
    gender: female
    accent: british

locations:
  - name: Spaceship Bridge
    type: interior
    lighting: Dimly lit

scenes:
  - location: Spaceship Bridge
    characters:
      - Captain Ryan Thompson
      - Lieutenant Ava Ramirez
      - Sergeant Marcus Chen
      - Dr. Sophia Collins
    plot: The team receives a distress signal from a research outpost on Europa, prompting them to set a course for the moon.
  - location: Europa's Orbit
    characters:
      - Captain Ryan Thompson
      - Lieutenant Ava Ramirez
      - Dr. Sophia Collins
    plot: As they approach Europa, their ship is attacked by unknown alien vessels, initiating a space battle.
  - location: Europa's Surface
    characters:
      - Captain Ryan Thompson
      - Sergeant Marcus Chen
      - Dr. Sophia Collins
    plot: The team lands on Europa's icy surface and makes their way towards the research outpost, encountering hostile alien creatures along the way.
  - location: Europa Research Outpost
    characters:
      - Captain Ryan Thompson
      - Lieutenant Ava Ramirez
      - Sergeant Marcus Chen
      - Dr. Sophia Collins
    plot: They reach the research outpost and discover that it has been overrun by the alien creatures. Theyrealize that they must find a way to neutralize the alien creatures and secure the outpost. 
'''
            },
        ]

        openai.api_key = os.getenv("CHATGPT_APIKEY")

    def generate(self, plot: str) -> str:
        self.messages.append(
            {"role": "user", "content": plot},
        )
        messages = self.messages
        full_resp = ""

        count = 5
        while count > 0:
            count -= 1
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
            )

            resp = completion.choices[0].message.content
            finish_reason = completion.choices[0].finish_reason
            full_resp += resp

            logging.info(">> Recieved: " + resp)
            logging.info(">> Have: " + full_resp)
            logging.info(">> finish_reason: " + completion.choices[0].finish_reason)
            if finish_reason == 'stop':
                logging.info('chatgpt: got all info')
                self.messages.append(
                    {"role": "assistant", "content": full_resp}
                )
                return full_resp
            elif finish_reason == 'length':
                logging.info(f'chatgpt: need more info, retrying, usage:{completion.choices[0].usage} count:{count}')
                messages += [
                    {"role": "assistant", "content": resp},
                ]
            else:
                raise Exception("finish reason is " + finish_reason)
        raise Exception('Tried too many times to talk to ChatGPT')



# in the __init__ for this class,
# add openai.api_key = config.get_ai_config().get_chatgpt_api_key()
class TextChatGPT(TextAi):
    def __init__(self, db: Database):
        self.db = db
        self.messages = [
            {
                "role": "system",
                "content": "You will be provided with a set of characters, " +
                "their description, and a scene in JSON format. " +
                "Create dialogue using the plot and characters " +
                "provided and return it in JSON format. Add a narrator with key 'narrator' describing the characters, scene, and emotions"
            },
            {
                "role": "user",
                "content": '{"characters":[{"name":"Max Doe",' +
                '"description":"A charismatic detective",' +
                '"voice_type":"Baritone","age":35,"height":' +
                '"6 feet","gender":"male"},{"name":"Joana Smith",' +
                '"description":"A brilliant scientist","voice_type":' +
                '"Soprano","age":28,"height":"5 feet 8 inches","gender"' +
                ':"female"}],"scene":{"location":"Lobby","characters"' +
                ':["Max Doe","Joana Smith"],"plot":"Max Doe thinks ' +
                'he is right."}}'
            },
            {
                "role": "assistant",
                "content": '{"dialogue":[{"speaker":"narrator","message":"Max stood close to Joana."},{"speaker":"Max Doe","message":"Joana, I must say, your taste in bagels is utterly appalling!"},{"speaker":"Joana Smith","message":"Max, you are right."},{"speaker":"narrator","message":"Finally Max was happy."}]}'
            }

        ]

        self.user_message = {}
        self.user_message['actors'] = self.db.get_data()['actors']

        openai.api_key = os.getenv("CHATGPT_APIKEY")

    def generate(self, s: Scene) -> str:
        self.user_message['scene'] = s.to_map()
        self.messages.append(
            {"role": "user", "content": json.dumps(self.user_message)}
        )

        self.user_message = {}
        messages = self.messages
        full_resp = ""

        count = 5
        while count > 0:
            count -= 1
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
            )

            resp = completion.choices[0].message.content
            finish_reason = completion.choices[0].finish_reason
            full_resp += resp

            logging.info(">> Recieved: " + resp)
            logging.info(">> Have: " + full_resp)
            logging.info(">> finish_reason: " + completion.choices[0].finish_reason)
            if finish_reason == 'stop':
                logging.info('chatgpt: got all info')
                self.messages.append(
                    {"role": "assistant", "content": full_resp}
                )
                try:
                    resp = json_trim(resp)
                    return json.dumps(json.loads(resp))
                except Exception:
                    return "{}"
            elif finish_reason == 'length':
                logging.info(f'chatgpt: need more info, retrying, usage:{completion.choices[0].usage} count:{count}')
                messages += [
                    {"role": "assistant", "content": ""},
                ]
            else:
                raise Exception("finish reason is " + finish_reason)

            ## DEBUG
            try:
                json.dumps(resp)
            except Exception:
                logging.critical("******* >> resp is not json but finish_reason: " + completion.choices[0].finish_reason)


        raise Exception('Tried too many times to talk to ChatGPT')
