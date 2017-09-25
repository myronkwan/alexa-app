import requests



def lambda_handler(event,context):
    if(event['session']['application']['applicationId']!='amzn1.ask.skill.e2cb70c7-7b43-4637-949a-bcdd7b16c2ed'):
        raise ValueError('Invalid Application ID')
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, event['session'])
    if event['request']['type']=='LaunchRequest':
        return on_launch(event['request'],event['session'])
    elif event['request']['type']=='IntentRequest':
        return on_intent(event['request'],event['session'])
    elif event['request']['type']=='SessionEndedRequest':
        return on_session_ended(event['request'],event['session'])
    else:
        speech_output='Try asking that again.'
        should_end_session=False
        return build_response({},build_speechlet_response('startover',speech_output,None,should_end_session))
        
def on_session_started(session_started_request,session):
    speech_output='Starting New Session.'
    session_attributes={}
    card_title='onsessionstarted'
    return build_response(session_attributes,build_speechlet_response(card_title,speech_output,None,False))
 
def on_launch(launch_request,session):
    speech_output='I can help you find a game rating.'
    should_end_session=False
    return build_response({},build_speechlet_response('onlaunch',speech_output,None,False))
    

def on_session_ended(session_ended_request,session):
    speech_output='Ending Session.'
    should_end_session=True
    return build_response({},build_speechlet_response('sessionended',speech_output,None,should_end_session))
    
def on_intent(intent_request,session):
    intent=intent_request['intent']
    intent_name=intent_request['intent']['name']
    if intent_name=='AMAZON.CancelIntent' or intent_name=='AMAZON.StopIntent':
        card_title= "Thanks"
        speech_output="Thanks for using the Game Rating App."
        should_end_session=True
        return build_response({},build_speechlet_response(card_title,speech_output,None,should_end_session))
    elif intent_name=='AMAZON.HelpIntent':
        speech_output='For example, you can ask, What is the game rating for Call of Duty.'
        should_end_session=False
        session_attributes={}
        card_title='helpintent'
        return build_response(session_attributes,build_speechlet_response(card_title,speech_output,None,should_end_session))
    elif intent_name=='AMAZON.StartOverIntent':
        speech_output='Ask me again.'
        should_end_session=False
        return build_response({},build_speechlet_response('startover',speech_output,None,should_end_session))
    elif intent_name=='askgamerating':
        return gamerating(intent)
    else:
        speech_output='Ask me again.'
        should_end_session=False
        return build_response({},build_speechlet_response('startover',speech_output,None,should_end_session))

    
def gamerating(intent):
    if intent['slots']['game'].get('value'):
        name=intent['slots']['game']['value']
    else:
        speech_output='Game not found'
        should_end_session=True
        session_attributes={}
        card_title='ratingresponse'
        return build_response(session_attributes,build_speechlet_response(card_title,speech_output,None,should_end_session))
    if name.endswith("'s"):
        name=name[:-2]
    search='?search='+ name
    url='https://api-2445582011268.apicast.io/games/'
    url1=url+search
    headers={'user-key':'2905236328de3e2b47d3753dc9d31d13','Accept':'application/json'}
    try:
        r=requests.get(url1,headers=headers)
        if(r.text=='[]'):
            speech_output='Game not found'
            should_end_session=True
            return build_response({},build_speechlet_response('gamenotfound',speech_output,None,should_end_session))
        else:
            response=r.json()
            gameid=str(response[0]['id'])
            r=requests.get(url+gameid,headers=headers)
            response=r.json()
            try:
                rating=str(round(response[0]['total_rating'],1))
            except KeyError as e:
                rating='Not Available'
            title=str(response[0]['name'])
            speech_output = title + ' rating is: ' + rating +'.'
            should_end_session=True
            session_attributes={}
            card_title='ratingresponse'
            return build_response(session_attributes,build_speechlet_response(card_title,speech_output,None,should_end_session))
    except (requests.exceptions.RequestException,ValueError ) as e:  
        print(e)
        speech_output='Error occured.'
        should_end_session=True
        return build_response({},build_speechlet_response('startover',speech_output,None,should_end_session))

        
def build_speechlet_response(title,output,reprompt_text,should_end_session):
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
    