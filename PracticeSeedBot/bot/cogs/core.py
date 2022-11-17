from uuid import UUID as UUIDTest
from discord import commands, ApplicationContext, Option
from discord.ext.commands import Cog
from PracticeSeedBot.bot.main import PracticeSeedBot
from PracticeSeedBot.bot.ui import modals
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
    
    @commands.slash_command(name="submit", description="Submit a practice seed.")
    async def submit(self, ctx: commands.ApplicationContext):
        return await ctx.interaction.response.send_modal(modals.SubmitModal(self.bot))

def setup(bot: PracticeSeedBot):
    bot.add_cog(Submit(bot))
