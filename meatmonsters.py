import os
import sys
import re
import random
import json
import base64 
import hashlib
from random import choice
from socketIO_client import SocketIO

class Monster(object):
   
    @staticmethod
    def random_text (action):
        source_file = ".".join([action, "txt"])
        with open (filename, "r") as source_file:
            lines = [line.rstrip() for line in source_file.read()]
            return choice(lines)

    @staticmethod
    def get_gif (filename):
        with open (filename, "rb") as image_file:
            data =  base64.b64encode(image_file.read())
            gif = "data:image/gif;base64," + data
            return gif

    @staticmethod
    def get_txt (filename):
        with open (filename, "r") as text_file:
            return text_file.read()

    def __init__(self, files):
        with open (os.sep.join([files, "attributes.json"]), 'r') as conf:
            self.config = json.load(conf)
        
        self.name = self.config["name"]
        self.actions = {} 
        
        for action, triggers in self.config["actions"].items():
            if action not in self.actions:
                self.actions[action] = {"gif":None, "txt":None, "triggers":None}

            gif_name = ".".join([action, "gif"])
            gif_path = os.sep.join([files, gif_name])
            self.actions[action]["gif"] = Monster.get_gif(gif_path)

            txt_name = ".".join([action, "txt"])
            txt_path = os.sep.join([files, txt_name])
            self.actions[action]["txt"] = Monster.get_txt(txt_path)

    def action(self, action):
        action = {}
        action["message"] = choice(self.actions[action][txt])
        action["picture"] = self.actions[action][gif]
        return action

class MeatMonsters(object):
    
    def __init__(self):
        
        with open ('meatmonsters.json', 'r') as conf:
            self.config = json.load(conf)

        self.api_key = self.config["key"]
        self.address = self.config["address"]
        self.monsters_dir = "./monsters/"

        self.fingerprint = "thisisthemeatmonsterfingerprint"
        self.debug = True
        self.monsters = {}
        self.load_monsters()

    def load_monsters(self):
        for monster_subdir in os.walk(self.monsters_dir).next()[1]:
            monster_path = os.sep.join([self.monsters_dir, monster_subdir])
            monster = Monster(files=monster_path)
            self.monsters[monster.name] = monster

    def run (self):
        if self.debug:
            print "Listening to %s" % self.address

        with SocketIO(self.address) as socketIO_listen:
            socketIO_listen.on('message', self.on_message)
            socketIO_listen.wait()

    def get_post (self, data):
        post = {}
        post["key"] = data["chat"]["key"]
        post["message"] = data["chat"]["value"]["message"]
        return post

    def get_message (self, reply, image):
        message = {}
        message ['apiKey'] = self.api_key
        message ['message'] = reply
        message ['fingerprint'] = self.fingerprint
        message ['picture'] = image
        return message

    def send_message (self, reply, image):
        SocketIO(self.address).emit('message', self.get_message(reply, image))

    def on_message(self, *args):
        post = self.get_post (args[0])
        print post['message']

if __name__ == '__main__':
    game = MeatMonsters()
    game.run()
