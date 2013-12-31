import sys
sys.path.append('../')
import web
import glob
import random
from gothonweb import map, game_lexicon

web.config.debug = False

urls = (
    '/game', 'GameEngine',
    '/', 'Index',
)
app = web.application(urls, globals())

if web.config.get('__session') is None:
    store = web.session.DiskStore('sessions')
    session = web.session.Session(app, store, initializer={'room': None, 'attempts': None})
    web.config.__session = session
else:
    session = web.config.__session

render = web.template.render('templates/', base='layout')


class Index(object):
    @staticmethod
    def GET():
        session.room = map.START
        session.attempts = 5
        web.seeother("/game")


class GameEngine(object):
    def __init__(self):
        pic = glob.glob("static/*.jpg")
        random_pic = random.choice(pic)
        actions = game_lexicon.ListActions()
        self.view = render.show_room(room=session.room, picture=random_pic,
                                     actions=actions.actions(session.room.name), attempts=session.attempts)

    def GET(self):
        if session.room:
            user_data = web.input(action=None)
            if user_data.action:
                session.room = session.room.go(user_data.action)
                web.seeother("/game")
            else:
                return self.view
        else:
            return render.you_died()

    def POST(self):
        code = web.input(armory_code=None)
        if code.armory_code:
            if session.attempts != 1:
                if code.armory_code != "0132":
                    session.attempts -= 1
                    web.seeother("/game")
                else:
                    session.room = session.room.go(code.armory_code)
                    web.seeother("/game")
            else:
                return render.you_died()
        else:
            return self.view

if __name__ == "__main__":
    app.run()