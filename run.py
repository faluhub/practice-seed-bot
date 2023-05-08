from PracticeSeedBot.bot import main
from PracticeSeedBot import database, secrets

if __name__ == "__main__":
    database.create()
    main.PracticeSeedBot().run(secrets.Discord.TOKEN)
