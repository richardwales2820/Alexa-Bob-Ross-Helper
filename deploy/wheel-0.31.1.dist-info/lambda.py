from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, ListAttribute
import random
import json

class PaintingModel(Model):
    class Meta:
        table_name = "painting"
    
    episode = UnicodeAttribute(hash_key=True)
    title = UnicodeAttribute()
    colors = ListAttribute()

def lambda_handler(event, context):
    #TODO(rwales): Change this
    if (event["session"]["application"]["applicationId"] != "amzn1.ask.skill.51ab8847-6dd1-425e-a4b4-82cbcd200789"):
        raise ValueError("Invalid Application ID")
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print("Starting new session.")

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    # if intent_name == "PaintingIntent":
    #     return get_painting_by_color()
    if intent_name == 'RandomPaint':
        return get_random_painting()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print("Ending session.")
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "Happy Little Helper"
    speech_output = "Happy painting, and God bless"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "Happy Little Helper"
    speech_output = "Ask me for a painting and I will give you a random Bob Ross masterpiece to copy"
    reprompt_text = "Ask me, what should you paint?"
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_random_painting():
    session_attributes = {}
    card_title = 'Happy Little Helper'
    reprompt_text = None
    should_end_session = True

    paintings = json.loads(PaintingModel.dumps())
    table_len = len(paintings)
    random_index = random.randint(0, table_len-1)
    painting = paintings[random_index]

    episode = painting[0]
    title = painting[1]['attributes']['title']['S']
    colors = [x['S'] for x in painting[1]['attributes']['colors']['L']]

    # Join all except last element and concat that separate so string doesn't look like
    # Blue, Red, Orange, 
    # Instead would be Blue, Red, Orange
    speech_output = '{} from {} uses the following colors: '.format(title, episode) + ', '.join(colors[:-1]) + colors[-1]

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# Should pass the color slot from intent
def get_painting_by_color():    

    # Should this be the session's list of paintings?
    session_attributes = {}
    card_title = 'Happy Little Helper'
    
    reprompt_text = None
    should_end_session = True

    # Get the paintings from DDB containing the given colors by user
    speech_output = 'There are [X] paintings that use those colors.'
    
    # If there are more than 10 paintings, paginate it with a reprompt

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
    

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }