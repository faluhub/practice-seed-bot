import discord
from uuid import UUID as UUIDTest
from discord import commands, ApplicationContext, Option
from discord.ext.commands import Cog
from PracticeSeedBot import constants
from PracticeSeedBot.bot.main import PracticeSeedBot
from PracticeSeedBot.bot.ui import modals, views
from PracticeSeedBot.database import classes

class Submit(Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        
        self.bot: PracticeSeedBot = bot

    def check_uuid(self, uuid: str):
        try: uuid_obj = UUIDTest(uuid, version=4)
        except ValueError: return False
        return str(uuid_obj) == uuid
    
    @commands.slash_command(name="link", description="Link your UUID from the mod.")
    async def link(self, ctx: ApplicationContext, uuid: Option(str, "Enter the UUID.")):
        msg = await ctx.respond("Thinking...", ephemeral=True)
        if not self.check_uuid(uuid):
            return await msg.edit_original_response(content="That is an invalid UUID!")
        db = classes.UUIDDatabase()
        db.set_uuid(ctx.author.id, uuid)
        return await msg.edit_original_response(content="Your UUID has been linked!\nYou can now play practice seeds via Discord.")
    
    @commands.slash_command(name="unlink", description="Unlink your UUID from the mod.")
    async def unlink(self, ctx: ApplicationContext):
        msg = await ctx.respond("Thinking...", ephemeral=True)
        db = classes.UUIDDatabase()
        if not db.id_exists(ctx.author.id):
            return await msg.edit_original_response(content="You don't have a UUID linked!")
        db.delete_uuid(ctx.author.id)
        return await msg.edit_original_response(content="Your UUID has been unlinked!")
    
    @commands.slash_command(name="submit", description="Submit a practice seed.")
    async def submit(self, ctx: ApplicationContext):
        return await ctx.interaction.response.send_modal(modals.SubmitModal(self.bot))
    
    @commands.slash_command(name="play", description="Play a seed.")
    async def play(self, ctx: ApplicationContext, seed: Option(str, "The seed to play.")):
        try: int(seed)
        except ValueError: return await ctx.response.send_message("That is an invalid seed!")

        msg = await ctx.respond("Thinking...", ephemeral=True)
        db = classes.UUIDDatabase()
        if db.id_exists(ctx.author.id):
            args = [self.uuid_db.get_uuid(ctx.author.id), str(seed)]
            seed_db = classes.SeedsDatabase()
            if seed_db.seed_exists(str(seed)):
                args.append(seed_db.get_notes(str(seed)))

            await constants.IO.emit("play", args)
            return await msg.edit_original_response(content=f"Added seed `{seed}` to the queue!")
    
    @commands.slash_command(name="race", description="Race against your friends!")
    async def race(self, ctx: commands.ApplicationContext, password: Option(str, "The race password."), seed: Option(str, "The seed to play.")):
        try: int(seed)
        except ValueError: return await ctx.response.send_message("That is an invalid seed!")
        
        embed = discord.Embed(
            title=f"Race: {seed}",
            description=f"> Click `start` to start the race.\n> This message will expire in `3 minutes`.\n> Password: ||`{password}`||",
            color=constants.COLOR
        )
        return await ctx.response.send_message(embed=embed, view=views.RaceView(password, seed, ctx.author), ephemeral=True, delete_after=180)

def setup(bot: PracticeSeedBot):
    bot.add_cog(Submit(bot))
