import discord
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
    async def link(self, ctx: ApplicationContext, _: Option(str, "Enter the UUID.")):
        await ctx.defer(ephemeral=True)
        return await self.bot.out_of_service(ctx)
    
    @commands.slash_command(name="unlink", description="Unlink your UUID from the mod.")
    async def unlink(self, ctx: ApplicationContext):
        await ctx.defer(ephemeral=True)
        return await self.bot.out_of_service(ctx)
    
    @commands.slash_command(name="submit", description="Submit a practice seed.")
    async def submit(self, ctx: ApplicationContext):
        return await ctx.response.send_modal(modals.SubmitModal(self.bot))
    
    @commands.slash_command(name="play", description="Play a seed.")
    async def play(self, ctx: ApplicationContext, seed: Option(str, "The seed to play.")):
        await ctx.defer(ephemeral=True)
        return await self.bot.out_of_service(ctx)
    
    @commands.slash_command(name="race", description="Race against your friends!")
    async def race(self, ctx: commands.ApplicationContext, password: Option(str, "The race password."), seed: Option(str, "The seed to play.")):
        await ctx.defer(ephemeral=True)
        return await self.bot.out_of_service(ctx)
    
    @commands.slash_command(name="random", description="Queue a random seed.")
    async def random(self, ctx: commands.ApplicationContext, amount: Option(int, "The amount of seeds.", default=1)):
        await ctx.defer(ephemeral=True)

        db = classes.SeedsDatabase()
        seeds = db.get_random_seeds(amount)
        content = "```\n"
        for seed in seeds:
            content += seed + "\n"
        content += "```"

        embed = discord.Embed(
            title="Random Seeds",
            description=f"The following seeds have been queried:\n{content}",
            color=self.bot.color
        )
        embed.set_footer(text=f"Requested {amount} seed{'s' if amount > 1 else ''}.")

        return await ctx.followup.send(embed=embed, ephemeral=True)

def setup(bot: PracticeSeedBot):
    bot.add_cog(Submit(bot))
