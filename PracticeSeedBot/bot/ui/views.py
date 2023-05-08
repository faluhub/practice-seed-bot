import discord
from discord import ButtonStyle, PartialEmoji
from discord.ui import View, Button
from PracticeSeedBot.database import classes

class SeedView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)

        self.uuid_db = classes.UUIDDatabase()
        self.seed_db = classes.SeedsDatabase()
        
        self.bot = bot
    
    @discord.ui.button(
        style=ButtonStyle.blurple,
        label="Play",
        custom_id="seedview:play"
    )
    async def play(self, _: Button, interaction: discord.Interaction):
        if self.uuid_db.id_exists(interaction.user.id):
            seed = self.seed_db.get_seed(interaction.message.id)
            if seed != None:
                notes = self.seed_db.get_notes(seed)
                if not notes == None:
                    author: discord.Member = self.bot.get_guild(self.bot.seed_server_id).get_member(self.seed_db.get_author(seed))
                    if not author == None:
                        notes = "<" + author.name + "> " + notes
                await self.bot.io.emit("play", [self.uuid_db.get_uuid(interaction.user.id), seed, notes])
                return await interaction.response.send_message(f"Added seed `{seed}` to the queue!", ephemeral=True)
            return await interaction.response.send_message("Something went wrong while fetching this seed!", ephemeral=True)
        return await interaction.response.send_message("You do not have a UUID linked!", ephemeral=True)

    @discord.ui.button(
        style=ButtonStyle.gray,
        label="",
        emoji=PartialEmoji.from_str("<:thumbs_up:1041742988528844890>"),
        custom_id="seedview:upvote"
    )
    async def upvote(self, _: Button, interaction: discord.Interaction):
        seed = self.seed_db.get_seed(interaction.message.id)
        if not seed == None:
            if not self.seed_db.has_downvoted(seed, interaction.user.id):
                if not self.seed_db.has_upvoted(seed, interaction.user.id):
                    if not self.seed_db.get_author(seed) == interaction.user.id or self.bot.debug:
                        upvotes = self.seed_db.add_upvote(seed, interaction.user.id)
                        embed = self.bot.build_submission_embed(seed, upvotes=upvotes)
                        try:
                            await interaction.message.edit(embed=embed)
                            return await interaction.response.send_message("Upvoted!", ephemeral=True)
                        except discord.Forbidden: return
                    return await interaction.response.send_message("You cannot upvote your own seed!", ephemeral=True)
                upvotes = self.seed_db.remove_upvote(seed, interaction.user.id)
                embed = self.bot.build_submission_embed(seed, upvotes=upvotes)
                try:
                    await interaction.message.edit(embed=embed)
                    return await interaction.response.send_message("Removed upvote!", ephemeral=True)
                except discord.Forbidden: return
            return await interaction.response.send_message("You have already downvoted this seed!", ephemeral=True)
        return await interaction.response.send_message("Something went wrong while fetching this seed!", ephemeral=True)
    
    @discord.ui.button(
        style=ButtonStyle.gray,
        label="",
        emoji=PartialEmoji.from_str("<:thumbs_down:1041742979930521621>"),
        custom_id="seedview:downvote"
    )
    async def downvote(self, _: Button, interaction: discord.Interaction):
        seed = self.seed_db.get_seed(interaction.message.id)
        if not seed == None:
            if self.bot.get_guild(self.bot.seed_server_id).get_role(self.bot.top_runner_role_id) in interaction.user.roles:
                if not self.seed_db.has_upvoted(seed, interaction.user.id):
                    if not self.seed_db.has_downvoted(seed, interaction.user.id):
                        if not self.seed_db.get_author(seed) == interaction.user.id or self.bot.debug:
                            downvotes = self.seed_db.add_downvote(seed, interaction.user.id)
                            embed = self.bot.build_submission_embed(seed, downvotes=downvotes)
                            try:
                                await interaction.message.edit(embed=embed)
                                return await interaction.response.send_message("Downvoted!", ephemeral=True)
                            except discord.Forbidden: return
                        return await interaction.response.send_message("You cannot downvote your own seed!", ephemeral=True)
                    downvotes = self.seed_db.remove_downvote(seed, interaction.user.id)
                    embed = self.bot.build_submission_embed(seed, downvotes=downvotes)
                    try:
                        await interaction.message.edit(embed=embed)
                        return await interaction.response.send_message("Removed downvote!", ephemeral=True)
                    except discord.Forbidden: return
                return await interaction.response.send_message("You have already upvoted this seed!", ephemeral=True)
            return await interaction.response.send_message("You are not allowed to downvote this seed!", ephemeral=True)
        return await interaction.response.send_message("Something went wrong while fetching this seed!", ephemeral=True)

class RaceView(View):
    def __init__(self, password: str, seed: str, host: discord.Member):
        super().__init__()

        self.password = password
        self.seed = seed
        self.host = host
    
    @discord.ui.button(
        style=ButtonStyle.blurple,
        label="Start!",
        custom_id="raceview:start"
    )
    async def start(self, _: discord.Button, interaction: discord.Interaction):
        await self.io.emit("race", [self.password, self.seed, f"{self.host.name}#{self.host.discriminator}"])
        await interaction.response.send_message("Started!", ephemeral=True)
        self.stop()
    
    @discord.ui.button(
        style=ButtonStyle.red,
        label="Cancel",
        custom_id="raceview:cancel"
    )
    async def cancel(self, _: discord.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Cancelled! (This message will delete itself after 10 seconds)", ephemeral=True, delete_after=10)
        self.stop()
