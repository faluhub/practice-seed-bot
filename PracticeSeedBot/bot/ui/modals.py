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
        if \
            not self.bot.get_guild(self.bot.seed_server_id).get_role(self.bot.top_runner_role_id) in interaction.user.roles or \
            not self.bot.get_guild(self.bot.seed_server_id).get_role(self.bot.developer_role_id) in interaction.user.roles:
                channel = self.bot.get_channel(self.bot.community_channel_id)

        if not db.seed_exists(self.children[0].value):
            msg = await channel.send(embed=self.bot.build_new_submission_embed(seed, seed_notes, interaction.user.id), view=views.SeedView(self.bot))
            db.create_seed(self.children[0].value, msg.id, interaction.user.id, seed_notes)

            return await interaction.response.send_message("Done! Thank you for your submission.", ephemeral=True)
        return await interaction.response.send_message("That seed has already been submitted!", ephemeral=True)
