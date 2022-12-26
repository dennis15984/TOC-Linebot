import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message, send_carousel_message, send_button_message, send_image_message


load_dotenv()



machine = TocMachine(
    states=[
        'input_age',
        'input_gender',
        'input_height',
        'input_weight',
        'input_days',
        'choose',
        'muscle',
        'thin',
    ],
    transitions=[
        {'trigger': 'advance', 'source': 'user', 'dest': 'input_gender', 'conditions': 'is_going_to_input_gender'},
        {'trigger': 'advance', 'source': 'input_gender', 'dest': 'input_age', 'conditions': 'is_going_to_input_age'},
        {'trigger': 'advance', 'source': 'input_age', 'dest': 'input_height', 'conditions': 'is_going_to_input_height'},
        {'trigger': 'advance', 'source': 'input_height', 'dest': 'input_weight', 'conditions': 'is_going_to_input_weight'},
        {'trigger': 'advance', 'source': 'input_weight', 'dest': 'input_days', 'conditions': 'is_going_to_input_days'},
        {'trigger': 'advance', 'source': 'input_days', 'dest': 'choose', 'conditions': 'is_going_to_choose'},
        {'trigger': 'advance', 'source': 'choose', 'dest': 'muscle', 'conditions': 'is_going_to_muscle'},
        {'trigger': 'advance', 'source': 'choose', 'dest': 'thin', 'conditions': 'is_going_to_thin'},
        {
            'trigger': 'go_back',
            'source': [
                'input_age',
                'input_gender',
                'input_height',
                'input_weight',
                'input_days',
                'choose',
                'muscle',
                'thin',
            ],
            'dest': 'user'
        },
    ],
    initial='user',
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path='')


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

mode = 0

@app.route('/callback', methods=['POST'])
def webhook_handler():
    global mode
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f'Request body: {body}')

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f'\nFSM STATE: {machine.state}')
        print(f'REQUEST BODY: \n{body}')
        
        response = machine.advance(event)         
        
        if response == False:
            if machine.state == 'user':
                send_text_message(event.reply_token, 'Enter "fitness" to start')
            elif machine.state == 'input_age' or machine.state == 'input_height' or machine.state == 'input_weight':
                send_text_message(event.reply_token, 'Please enter an integer')
            elif machine.state == 'input_gender':
                send_text_message(event.reply_token, 'Please enter male or female')
            elif machine.state == 'input_days':
                send_text_message(event.reply_token, 'Please enter an integer(0-7)')
            elif machine.state == 'choose':
                send_text_message(event.reply_token, 'Please enter "build muscle" or "lose fat"')
        
    return 'OK'


@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    machine.get_graph().draw('fsm.png', prog='dot', format='png')
    return send_file('fsm.png', mimetype='image/png')


if __name__ == '__main__':
    port = os.environ.get('PORT', 8000)
    app.run(host='0.0.0.0', port=port, debug=True)