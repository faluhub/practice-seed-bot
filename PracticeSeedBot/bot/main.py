import discord, os
from datetime import datetime
from discord import ApplicationContext, commands, AutoShardedBot, Interaction
from PracticeSeedBot.database import classes
from PracticeSeedBot.bot.ui import views

class PracticeSeedBot(AutoShardedBot):
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.debug = False
        self.persistent_views_added = False

        self.cog_blacklist = []
        self.cog_folder_blacklist = ["__pycache__"]
        self.cogs_path = "./PracticeSeedBot/bot/cogs"

        self.color = 0x9bc4af

        self.submission_channel_id = 1038788499161235477 if self.debug else 1035808397351714929
        self.community_channel_id = 1042885879569596466 if self.debug else 1039991212716863529
        self.seed_server_id = 1018128160962904114 if self.debug else 1035808396349292546
        self.developer_role_id = 1041756599439593482 if self.debug else 1038468830990708756
        self.top_runner_role_id = self.developer_role_id if self.debug else 1035818019928150027

        super().__init__(
            intents=discord.Intents(guilds=True, members=True),
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(everyone=False),
            owner_ids=[810863994985250836],
            debug_guilds=[self.seed_server_id]
        )

        @commands.slash_command(name="reload", description="Reload the cogs.")
        @discord.default_permissions(manage_guild=True)
        async def reload_cogs(ctx: ApplicationContext):
            msg = await ctx.respond("Thinking...", ephemeral=True)
            if self.get_guild(self.seed_server_id).get_role(self.developer_role_id) in ctx.author.roles:
                print("Reloading cogs...")
                for extension in ctx.bot.extensions:
                    ctx.bot.reload_extension(extension)
                return await msg.edit_original_response(content="Done!")
            await msg.edit_original_response(content="You do not have sufficient permissions to execute this command!")
        
        self.add_application_command(reload_cogs)
    
    def build_submission_embed(self, seed: int, *, upvotes: int=None, downvotes: int=None) -> discord.Embed:
        seed_db = classes.SeedsDatabase()
        upvotes = seed_db.get_upvotes(seed) if upvotes is None else upvotes
        downvotes = seed_db.get_downvotes(seed) if downvotes is None else downvotes
        notes = seed_db.get_notes(seed)
        author = seed_db.get_author(seed)
        return self.build_new_submission_embed(seed, notes, author, upvotes=upvotes, downvotes=downvotes)
    
    def build_new_submission_embed(self, seed: int, notes: str, author: int, *, upvotes: int=0, downvotes: int=0) -> discord.Embed:
        member = self.get_guild(self.seed_server_id).get_member(author)
        embed = discord.Embed(
            title=str(seed),
            color=self.color,
            description=f"Seed Notes:\n||{notes}||"
        )
        embed.add_field(name="Upvotes:", value=f"`{upvotes}`")
        embed.add_field(name="Downvotes:", value=f"`{downvotes}`")
        if not member == None: embed.add_field(name="Author:", value=f"`{member.name}#{member.discriminator}`")
        else: embed.add_field(name="Author:", value=f"`{author}`")
        return embed

    def load_cogs(self, folder=None):
        if folder != None: self.cogs_path = os.path.join(self.cogs_path, folder)
        formatted_path = self.cogs_path.strip("./").replace("/", ".").replace("\\", ".")

        for file in os.listdir(self.cogs_path):
            if not os.path.isdir(os.path.join(self.cogs_path, file)):
                if not file in self.cog_blacklist:
                    try:
                        self.load_extension(f"{formatted_path}.{file[:-3]}")
                        print(f"  Loaded '{file}'")
                    except Exception as e: print(e)
            else:
                if not file in self.cog_folder_blacklist:
                    self.load_cogs(file)
    
    async def out_of_service(self, ctx):
        msg = "This feature is no longer in use.\nRead https://discord.com/channels/1035808396349292546/1041100738731978762/1116074267931590706 for info."
        if isinstance(ctx, ApplicationContext): return await ctx.followup.send(msg, ephemeral=True)
        elif isinstance(ctx, Interaction): return await ctx.response.send_message(msg, ephemeral=True)
    
    async def on_connect(self):
        (
            print("Loading cogs..."),
            self.load_cogs()
        )
        (
            print("Registering commands..."),
            await self.register_commands()
        )
        print("\nConnected")
        return await super().on_connect()

    async def on_ready(self):
        if not self.persistent_views_added:
            print("Adding persistent views...")
            self.add_view(views.SeedView(self))
            self.persistent_views_added = True
        return print(f"Ready, took {(datetime.utcnow() - self.start_time).seconds} seconds.")

if __name__ == "__main__":
    exit("The bot cannot be run directly from the bot file.")
