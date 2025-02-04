import discord
from discord.ext import commands, tasks
from discord.ui import View, Select


intents = discord.Intents.all()  
bot = commands.Bot(command_prefix='+', intents=intents)


@bot.command()
async def dmall(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Vous n'avez pas la permission d'utiliser cette commande")
        return

    embed = discord.Embed(title="DM All", description="Configurez votre message à envoyer à tous les membres", color=discord.Color.blue())
    embed.add_field(name="Instructions", value="Choisissez un message, une couleur et une image via les options ci-dessous")

    class DMConfig(View):
        def __init__(self):
            super().__init__(timeout=None)
            self.message = ""
            self.color = discord.Color.blue()
            self.image_url = ""

        @discord.ui.select(placeholder="Choisissez un paramètre", options=[
            discord.SelectOption(label="Message", description="Définir le texte du message"),
            discord.SelectOption(label="Couleur", description="Choisir une couleur pour l'embed"),
            discord.SelectOption(label="Image", description="Ajouter une URL d'image")
        ])
        async def select_callback(self, interaction: discord.Interaction, select):
            selected_option = interaction.data["values"][0]
            if selected_option == "Message":
                await interaction.response.send_message("Entrez le message à envoyer :", ephemeral=False)

                def check(msg):
                    return msg.author == interaction.user and msg.channel == interaction.channel

                try:
                    msg = await bot.wait_for("message", check=check, timeout=60)
                    self.message = msg.content
                    await interaction.followup.send("Message mis à jour !", ephemeral=False)
                except asyncio.TimeoutError:
                    await interaction.followup.send("Temps écoulé", ephemeral=False)

            elif selected_option == "Couleur":
                await interaction.response.send_message("Entrez un code hexadécimal pour la couleur :", ephemeral=False)

                def check(msg):
                    return msg.author == interaction.user and msg.channel == interaction.channel

                try:
                    msg = await bot.wait_for("message", check=check, timeout=60)
                    self.color = discord.Color(int(msg.content.strip("#"), 16))
                    await interaction.followup.send("Couleur mise à jour !", ephemeral=False)
                except ValueError:
                    await interaction.followup.send("Code de couleur invalide", ephemeral=False)
                except asyncio.TimeoutError:
                    await interaction.followup.send("Temps écoulé", ephemeral=False)

            elif selected_option == "Image":
                await interaction.response.send_message("Entrez une URL d'image :", ephemeral=False)

                def check(msg):
                    return msg.author == interaction.user and msg.channel == interaction.channel

                try:
                    msg = await bot.wait_for("message", check=check, timeout=60)
                    self.image_url = msg.content
                    await interaction.followup.send("URL de l'image mise à jour !", ephemeral=False)
                except asyncio.TimeoutError:
                    await interaction.followup.send("Temps écoulé.", ephemeral=False)

        @discord.ui.button(label="Lancer", style=discord.ButtonStyle.green)
        async def send_dm(self, interaction: discord.Interaction, button):
            if not self.message:
                await interaction.response.send_message("Le message ne peut pas être vide.", ephemeral=False)
                return

            members = [member for member in ctx.guild.members if not member.bot]
            total = len(members)
            sent = 0

            embed = discord.Embed(title="Annonce", description=self.message, color=self.color)
            if self.image_url:
                embed.set_image(url=self.image_url)

            await interaction.response.send_message(f"Envoi en cours à {total} membres...", ephemeral=False)

            for member in members:
                try:
                    await member.send(embed=embed)
                    sent += 1
                except discord.Forbidden:
                    pass

                progress = (sent / total) * 100
                print(f"Progression : {progress:.2f}%")

            await ctx.send(f"Message envoyé à {sent}/{total} membres.")

    view = DMConfig()
    await ctx.send(embed=embed, view=view)

bot.run("Token de ton bot")
