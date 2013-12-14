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
    def get_gif (filename):
        with open (filename, "rb") as image_file:
            data =  base64.b64encode(image_file.read())
            gif = "data:image/gif;base64," + data
            return gif

    def __init__(self, name, files):
        self.name = name
        self.appear_file = os.sep.join([files, "appear.gif"])
        self.attack_file = os.sep.join([files, "attack.gif"])
        self.appear_gif = Monster.get_gif(self.appear_file)
        self.attack_gif = Monster.get_gif(self.attack_file)

class MeatMonsters(object):
    
    def __init__(self):
        
        with open ('meatmonsters.json', 'r') as conf:
            self.config = json.load(conf)

        self.api_key = self.config["key"]
        self.address = self.config["address"]
        self.monsters_dir = "./monsters/"

        self.fingerprint = "thisisthemeatmonsterfingerprint"
        self.debug = True
        self.monsters = []
        self.load_monsters()

    def load_monsters(self):
        for monster_name in os.walk(self.monsters_dir).next()[1]:
            monster_dir = os.sep.join([self.monsters_dir, monster_name])
            self.monsters.append(Monster(name=monster_name, files=monster_dir))

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
        if post['message'] == '!summon':
            monster = choice(self.monsters)
            self.send_message ("SKREEEEEEEEEONGK!", monster.appear_gif)
        if post['message'] == '!attack':
            monster = choice(self.monsters)
            self.send_message ("SKREEEEEEEEEONGK!", monster.attack_gif)


if __name__ == '__main__':
    game = MeatMonsters()
    game.run()
