import socketio
from datetime import datetime
from PracticeSeedBot.bot import main
from PracticeSeedBot import database, secrets, constants

if __name__ == "__main__":
    constants.START_TIME = datetime.utcnow()

    constants.IO = socketio.AsyncClient()

    database.create()
    main.PracticeSeedBot().run(secrets.Discord.TOKEN)
