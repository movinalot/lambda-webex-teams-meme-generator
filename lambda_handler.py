"""
Name:
    lambda_handler.py
Purpose:
    lambda hander for the DevNet Day Meme Generator Skill
Author:
    John McDonough (jomcdono@cisco.com)
    Cisco Systems, Inc.
"""
# pylint: disable=unused-argument, import-error, inconsistent-return-statements

from __future__ import print_function
import json
import random
from botocore.vendored import requests

MEME_IMAGES = {
    "Batman" : "438680",
    "Spongebob":"102156234",
    "Butterfly":"100777631",
    "Alien":"101470",
    "Futurama":"61520",
    "Leo":"5496396",
    "Skeptical":"101288",
    "Kermit":"84341851",
    "Doge":"8072285",
    "Yoda":"14371066",
    "Patrick":"61581"
}

MEME_TEXTS = [
    {
        "text0": "Hand sanitizer helps you",
        "text1": "Discover the cuts you didn't know you had"
    },
    {
        "text0": "Everything is funnier",
        "text1": "When you're not allowed to laugh"
    },
    {
        "text0": "Saying, I get it!",
        "text1": "So the teacher walks away"
    },
    {
        "text0": "Parents call it talking back",
        "text1": "We call it explaining"
    },
    {
        "text0": "Mom: Why is everything on the floor?",
        "text1": "Gravity Mom!"
    },
    {
        "text0": "That song is soooo old!",
        "text1": "So are your parents, you still listen to them"
    },
    {
        "text0": "Where have you been all my life?",
        "text1": "Please go back there."
    },
    {
        "text0": "This is me",
        "text1": "When someone ignores me"
    },
    {
        "text0": "When you're about to say something interesting",
        "text1": "And the topic changes."
    },
    {
        "text0": "Message send failed, retry?",
        "text1": "Uh, duh, yes!"
    },
    {
        "text0": "Teacher - Don't pack up yet...",
        "text1": "Students - *quietly pack up*"
    },
    {
        "text0": "We all have that one friend",
        "text1": "That needs to learn how to whisper"
    },
    {
        "text0": "Cleaning my room",
        "text1": "2% cleaning, 35% complaining, 63% playing with stuff"
    },
    {
        "text0": "Parents: We need to talk, Me: Oh no!",
        "text1": "Parents: Stop leaving the lights on"
    },
    {
        "text0": "Oh, you're upset you got a 97 on the test",
        "text1": "Here use my 56 to dry your tears"
    },
    {
        "text0": "Family sized cookie packages, good!",
        "text1": "Sharing with family, bad!"
    }
]

IMGFLIP_URL = "http://api.imgflip.com/caption_image"
WEBEX_T_URL = "https://api.ciscospark.com/v1"
WEBEX_T_MSG_RESOURCE = '/messages'

# Put your values here for imgFlip
IMGFLIP_U = 'imgflip-username-goes-here'
IMGFLIP_P = 'imgflip-password-goes-here'

# Put your values here for Webex Teams
WEBEX_T_TOKEN = 'webex-teams-bot-token-goes-here'
WEBEX_T_EMAIL = 'webex-teams-recipient-email-goes-here'

# Meme Creation functions
def make_any_meme():
    """ Make a random meme and send to requester """

    imgflip_headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Accept': "application/json",
    }

    meme_image = random.choice(MEME_IMAGES.keys())
    meme_text = random.randint(0, len(MEME_TEXTS)-1)


    encoded_url = (
        IMGFLIP_URL +
        "?username="+IMGFLIP_U +
        "&password="+IMGFLIP_P +
        "&template_id="+MEME_IMAGES[meme_image] +
        "&text0="+MEME_TEXTS[meme_text]['text0'] +
        "&text1="+MEME_TEXTS[meme_text]['text1']
    )

    print(encoded_url)
    response = requests.request(
        "GET",
        encoded_url,
        headers=imgflip_headers
    )

    print(response.text)

    json_response = json.loads(response.text)
    imgflip_page_url = json_response['data']['page_url'].replace('\\', '')
    imgflip_file_url = json_response['data']['url'].replace('\\', '')

    webex_t_headers = {
        'Authorization': 'Bearer ' + WEBEX_T_TOKEN,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    webex_t_msg_json = {
        "toPersonEmail": WEBEX_T_EMAIL,
        "markdown": "**Here's your meme!** " + imgflip_page_url,
        "files": [
            imgflip_file_url
        ]
    }

    response = requests.request(
        "POST",
        WEBEX_T_URL + WEBEX_T_MSG_RESOURCE,
        json=webex_t_msg_json,
        headers=webex_t_headers
    )

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    """ Build Speechlet Response """

    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    """ Build Response """

    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ Get Welcome Response """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = (
        "Welcome to the DevNet Day Skill for Meme Creation. " +
        "You can say things like, make me a meme. " +
        "Or you can say create a kermit meme."
    )

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.

    reprompt_text = "Did you want to create a meme?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    """ Called when the session is ended """

    card_title = "Session Ended"
    speech_output = (
        "Thank you for using the DevNet Day Alexa Skill " +
        "for meme generation."
    )

    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# Make a meme
def make_meme(intent, session):
    """ Make a meme and congratulate """

    session_attributes = {}
    reprompt_text = None

    make_any_meme()
    speech_output = "Yay, you did it!"
    should_end_session = True

    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "MakeMeme":          # Entry point for the MakeMeme intent
        return make_meme(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif (intent_name == "AMAZON.CancelIntent" or
          intent_name == "AMAZON.StopIntent"):
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Main handler ------------------

def lambda_handler(event, context):
    """
    Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameterself.
    """

    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
