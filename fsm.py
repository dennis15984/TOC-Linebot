from transitions.extensions import GraphMachine
from utils import send_text_message, send_carousel_message, send_button_message, send_image_message
from bs4 import BeautifulSoup
import requests
from linebot.models import ImageCarouselColumn, URITemplateAction, MessageTemplateAction
import pandas as pd

# global variable
age = 0
gender = ''
height = 0
weight = 0
days = 0
BMR = 0
TDEE = 0
part = ''
diet_type = -1

class TocMachine(GraphMachine):

    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    # user start
    def is_going_to_input_gender(self, event):
        text = event.message.text
        return text.lower() == 'fitness'

    def on_enter_input_gender(self, event):
        title = 'Please provide basic info'
        text = 'Male or Female?'
        btn = [
            MessageTemplateAction(
                label = 'Male',
                text ='Male'
            ),
            MessageTemplateAction(
                label = 'Female',
                text = 'Female'
            ),
        ]
        url = 'https://bpic.588ku.com/element_origin_min_pic/20/06/11/8426690445d358314e5120d0c3e3f448.jpg'
        send_button_message(event.reply_token, title, text, btn, url)

    def is_going_to_input_age(self, event):
        global gender
        text = event.message.text

        if text == 'Male':
            gender = 'Male'
            return True
        elif text == 'Female':
            gender = 'Female'
            return True
        return False

    def on_enter_input_age(self, event):
        send_text_message(event.reply_token, 'Please enter your age')

    def is_going_to_input_height(self, event):
        global age
        text = event.message.text

        if text.lower().isnumeric():
            age = int(text)
            return True
        return False

    def on_enter_input_height(self, event):
        send_text_message(event.reply_token, 'Please enter your height')

    def is_going_to_input_weight(self, event):
        global height
        text = event.message.text

        if text.lower().isnumeric():
            height = int(text)
            return True
        return False

    def on_enter_input_weight(self, event):
        send_text_message(event.reply_token, 'Please enter your weight')

    def is_going_to_input_days(self, event):
        global weight
        text = event.message.text

        if text.lower().isnumeric():
            weight = int(text)
            return True
        return False

    def on_enter_input_days(self, event):
        send_text_message(event.reply_token, 'Please enter days of exercise per week')

    def is_going_to_choose(self, event): 
       return True 
    

    # state of choose
    def on_enter_choose(self, event):
        global age, gender, height, weight, days
        title = 'GOAL: build muscle or lose weight?'
        text = 'age: ' + str(age) + ', gender: ' + gender + ',\nheight: ' + str(height) + 'cm, weight: ' + str(weight) + 'kg'
        btn = [
            MessageTemplateAction(
                label = 'build muscle',
                text ='build muscle'
            ),
            MessageTemplateAction(
                label = 'lose weight',
                text = 'lose weight'
            ),
        ]
        url = 'https://img.lovepik.com/element/40136/7121.png_1200.png'
        send_button_message(event.reply_token, title, text, btn, url)

    def is_going_to_muscle(self, event):
        global diet_type
        text = event.message.text
        if (text == 'build muscle'):
            return True
        return False

    # state of muscle
    def on_enter_muscle(self, event):
        send_text_message(event.reply_token, 'If you want to build muscle, you can eat 300kcal more than your TDEE\nTDEE is the amount of calories your body comsumes everyday\nIn your daily diet, protein 35%, carb 50%, fat 15%')

    def is_going_to_thin(self, event):
        global diet_type
        text = event.message.text
        if (text == 'lose fat'):
            return True
        return False

    # state of thin
    def on_enter_thin(self, event):
        send_text_message(event.reply_token, 'If you want to build muscle, you can eat 300kcal more than your TDEE\nTDEE is the amount of calories your body comsumes everyday\nIn your daily diet, protein 45%, carb 45%, fat 10%')
       
