import discord
from uuid import UUID as UUIDTest
from discord import commands, ApplicationContext, Option
from discord.ext.commands import Cog
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
        await ctx.defer()

        if not self.check_uuid(uuid):
            return await ctx.followup.send("That is an invalid UUID!", ephemeral=True)
        db = classes.UUIDDatabase()
        db.set_uuid(ctx.author.id, uuid)
        return await ctx.followup.send("Your UUID has been linked!\nYou can now play practice seeds via Discord.", ephemeral=True)
    
    @commands.slash_command(name="unlink", description="Unlink your UUID from the mod.")
    async def unlink(self, ctx: ApplicationContext):
        await ctx.defer()

        db = classes.UUIDDatabase()
        if not db.id_exists(ctx.author.id):
            return await ctx.followup.send("You don't have a UUID linked!", ephemeral=True)
        db.delete_uuid(ctx.author.id)
        return await ctx.followup.send("Your UUID has been unlinked!", ephemeral=True)
    
    @commands.slash_command(name="submit", description="Submit a practice seed.")
    async def submit(self, ctx: ApplicationContext):
        return await ctx.response.send_modal(modals.SubmitModal(self.bot))
    
    @commands.slash_command(name="play", description="Play a seed.")
    async def play(self, ctx: ApplicationContext, seed: Option(str, "The seed to play.")):
        await ctx.defer()

        try: int(seed)
        except ValueError: return await ctx.followup.send("That is an invalid seed!", ephemeral=True)

        db = classes.UUIDDatabase()
        if db.id_exists(ctx.author.id):
            args = [db.get_uuid(ctx.author.id), str(seed)]
            seed_db = classes.SeedsDatabase()
            if seed_db.seed_exists(str(seed)):
                args.append(seed_db.get_notes(str(seed)))

            await self.bot.io.emit("play", args)
            return await ctx.followup.send(f"Added seed `{seed}` to the queue!", ephemeral=True)
        return await ctx.followup.send("Link your UUID first before running this command!\n*Read #how-to for instructions.*", ephemeral=True)
    
    @commands.slash_command(name="race", description="Race against your friends!")
    async def race(self, ctx: commands.ApplicationContext, password: Option(str, "The race password."), seed: Option(str, "The seed to play.")):
        await ctx.defer()

        try: int(seed)
        except ValueError: return await ctx.followup.send("That is an invalid seed!", ephemeral=True)
        
        embed = discord.Embed(
            title=f"Race: {seed}",
            description=f"> Click `start` to start the race.\n> This message will expire in `3 minutes`.\n> Password: ||`{password}`||",
            color=self.bot.color
        )
        return await ctx.followup.send(embed=embed, view=views.RaceView(password, seed, ctx.author), ephemeral=True, delete_after=180)
    
    @commands.slash_command(name="random", description="Queue a random seed.")
    @discord.default_permissions(manage_guild=True)
    async def random(self, ctx: commands.ApplicationContext, amount: Option(int, "The amount of seeds.", default=1)):
        await ctx.defer()

        uuid_db = classes.UUIDDatabase()
        if uuid_db.id_exists(ctx.author.id):
            db = classes.SeedsDatabase()
            seeds = db.get_random_seeds(amount)
            content = "```\n"
            uuid = uuid_db.get_uuid(ctx.author.id)

            for seed in seeds:
                content += seed + "\n"
                await self.bot.io.emit("play", [uuid, str(seed)])
            content += "```"

            embed = discord.Embed(
                title="Random Seeds",
                description=f"The following seeds have been queued:\n{content}",
                color=self.bot.color
            )
            embed.set_footer(text=f"Requested {amount} seed{'s' if amount > 1 else ''}.")

            return await ctx.followup.send(embed=embed, ephemeral=True)
        return await ctx.followup.send("Link your UUID first before running this command!\n*Read #how-to for instructions.*", ephemeral=True)

def setup(bot: PracticeSeedBot):
    bot.add_cog(Submit(bot))
