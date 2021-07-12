from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
  return "Use this link to add the bot to your server: https://discord.com/api/oauth2/authorize?client_id=861388063699632148&permissions=268437504&scope=bot"


def run():
  app.run(host='0.0.0.0', port=8080)

def keep_alive():
  server = Thread(target=run)
  server.start()