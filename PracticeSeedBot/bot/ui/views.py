import discord
from discord import ButtonStyle, PartialEmoji
from discord.ui import View, Button
from PracticeSeedBot import constants
from PracticeSeedBot.database import classes
from PracticeSeedBot.bot.main import PracticeSeedBot

class SeedView(View):
    def __init__(self, bot: PracticeSeedBot):
        super().__init__(timeout=None)

        self.uuid_db = classes.UUIDDatabase()
        self.seed_db = classes.SeedsDatabase()
        
        self.bot = bot
    
    @discord.ui.button(
        style=ButtonStyle.blurple,
        label="Play"
    )
    async def play(self, button: Button, interaction: discord.Interaction):
        if self.uuid_db.id_exists(interaction.user.id):
            seed = self.seed_db.get_seed(interaction.message.id)
            if seed != None:
                await constants.IO.emit("play", [self.uuid_db.get_uuid(interaction.user.id), seed])
                return await interaction.response.send_message(f"Added seed `{seed}` to the queue!", ephemeral=True)
            return await interaction.response.send_message("Something went wrong while fetching this seed!", ephemeral=True)
        return await interaction.response.send_message("You do not have a UUID linked!", ephemeral=True)

    @discord.ui.button(
        style=ButtonStyle.green,
        label="",
        emoji=PartialEmoji.from_str("<:heart_eyes:1038801251099496458>")
    )
    async def upvote(self, button: Button, interaction: discord.Interaction):
        seed = self.seed_db.get_seed(interaction.message.id)
        if seed != None:
            if not self.seed_db.has_upvoted(seed, interaction.user.id):
                upvotes = self.seed_db.add_upvote(seed, interaction.user.id)
                embed = self.bot.build_submission_embed(seed, upvotes)
                try:
                    await interaction.message.edit(embed=embed)
                    return await interaction.response.send_message("Upvoted!", ephemeral=True)
                except discord.Forbidden:
                    pass
            return await interaction.response.send_message("You've already upvoted this seed!", ephemeral=True)
        return await interaction.response.send_message("Something went wrong while fetching this seed!", ephemeral=True)
