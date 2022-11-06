import discord
from discord import InputTextStyle
from discord.ui import Modal, InputText
from PracticeSeedBot.bot.main import PracticeSeedBot
from PracticeSeedBot.database import classes
from PracticeSeedBot.bot.ui import views

class SubmitModal(Modal):
    def __init__(self, bot: PracticeSeedBot):
        super().__init__(
            InputText(
                label="Seed:",
                max_length=25
            ),
            InputText(
                style=InputTextStyle.paragraph,
                label="Seed Notes:",
                max_length=100
            ),
            title="Submit Seed"
        )

        self.bot = bot
    
    async def callback(self, interaction: discord.Interaction):
        seed = self.children[0].value
        seed_notes = self.children[1].value

        try: seed = int(seed)
        except ValueError: return await interaction.response.send_message("That is an invalid seed! Please try again.", ephemeral=True)

        db = classes.SeedsDatabase()
        channel = self.bot.get_channel(self.bot.submission_channel_id)
        msg = await channel.send(embed=self.bot.build_new_submission_embed(seed, seed_notes, interaction.user.id), view=views.SeedView(self.bot))
        db.create_seed(seed, msg.id, interaction.user.id, seed_notes)

        return await interaction.response.send_message("Done! Thanks for your submission.", ephemeral=True)
