import asyncio
import os

from datetime import datetime, timedelta

import discord
from discord.ext import commands
from discord import option
from discord.ui import button, View
from discord.ext import commands, tasks

import time

import dotenv
dotenv.load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False
intents.guilds = True
bot = discord.Bot(debug_guilds=[...])

statuses = ["Ready or Not", "Six Days", "Training", "Ground Branch"]
current_status_index = 0
bot = commands.Bot(command_prefix='/', intents=intents)
squad_creator = None


class Squad(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)
    self.user_statuses = {
    }  

  @discord.ui.button(label="JOIN",
                     custom_id="button-1",
                     style=discord.ButtonStyle.success)
  async def button_callback(self, button, interaction):
    await interaction.response.send_message("You joined the squad!",
                                            ephemeral=True)
    await self.update_status(interaction, "✅")

  @discord.ui.button(label="Join later",
                     custom_id="button-2",
                     style=discord.ButtonStyle.secondary)
  async def button2_callback(self, button, interaction):
    await interaction.response.send_message("You will join the squad later!",
                                            ephemeral=True)
    await self.update_status(interaction, "🕑")

  @discord.ui.button(label="Dismiss",
                     custom_id="button-3",
                     style=discord.ButtonStyle.red)
  async def button3_callback(self, button, interaction):
    await interaction.response.send_message("You dismissed!", ephemeral=True)
    await self.update_status(interaction, "❌")

  async def update_status(self, interaction, status_icon):
    original_embed = interaction.message.embeds[0]
    user_id = interaction.user.id

    if user_id == squad_creator:
      await interaction.response.send_message("Abort Squad?", ephemeral=True)

    if user_id not in self.user_statuses:
      self.user_statuses[user_id] = status_icon
    else:
      self.user_statuses[user_id] = status_icon

    for field in original_embed.fields:
      if field.name.endswith((f"✅ {interaction.user.display_name}",
                              f"🕑 {interaction.user.display_name}",
                              f"❌ {interaction.user.display_name}")):
        field.name = f"{status_icon} {interaction.user.display_name}"
        break
    else:
      original_embed.add_field(
          name=f"{status_icon} {interaction.user.display_name}",
          value="\u200B",
          inline=False)

    await interaction.message.edit(embed=original_embed)

  @bot.event
  async def on_ready():
    botlog = 1124237862729170945
    botlogchannel = bot.get_channel(botlog)
    embedVar = discord.Embed(title="Status",
                             description="Bot is ready!",
                             color=0x5e1000)
    embedVar.set_author(name="Squad Leader",
                        icon_url="https://i.ibb.co/GCGtxKs/maxresdefault.jpg")
    await botlogchannel.send(embed=embedVar)
    bot.add_view(Squad())
    print(f"{bot.user} is ready!")
    
    @tasks.loop(seconds=10)
    async def change_status():
      global current_status_index
      new_game_name = statuses[current_status_index]
      await bot.change_presence(activity=discord.Game(name=new_game_name),
                                status=discord.Status.do_not_disturb)
      current_status_index = (current_status_index + 1) % len(statuses)

    change_status.start()


@bot.slash_command()
async def ready(ctx):
  user_id = ctx.author.id
  await ctx.respond(f"Ready! {user_id}")


ger_td_today = None
ger_td_tmmrw = None

dt_today = datetime.now().date()
dt_tmmrw = dt_today + timedelta(days=1)

ger_dt_today = dt_today.strftime("%d.%m.%Y")
ger_dt_tmmrw = dt_tmmrw.strftime("%d.%m.%Y")

user_id = None


@bot.slash_command(name="create_squad",
                   description="Create a new embed for a squad!")
@option("game",
        description="Choose a game!",
        choices=["Ready or Not", "Arma 3", "Six Days", "Ground Branch"])
@option("date",
        description="Choose a date!",
        choices=[f"{ger_dt_today}", f"{ger_dt_tmmrw}"])
async def sendembed(ctx, game, date, time):
  ping = None
  image = None
  embedcolor = None
  thumbnail = None
  squad_creator = ctx.author.id

  if game == "Ready or Not":
    ping = ctx.guild.get_role(1123235053812596816)
    image = "https://i.ibb.co/XxttMNh/wallhaven-g8q983.jpg"
    embedcolor = 0xff0015
    thumbnail = "https://i.ibb.co/YcDTTNH/21151679277867.png"

  elif game == "Arma 3":
    ping = ctx.guild.get_role(1124234701226389545)
    image = "https://i.ibb.co/t4Rb14k/arma3.png"
    embedcolor = 0x0e4d07
    thumbnail = "https://i.ibb.co/dWX3Y9f/arma-3-wallpaper-8.jpg"

  elif game == "Six Days":
    ping = ctx.guild.get_role(1123236101310660669)
    image = "https://i.ibb.co/qDSw59t/HD-crop.jpg"
    embedcolor = 0xb38c02
    thumbnail = "https://i.ibb.co/rwf5x45/maxresdefault.jpg"

  elif game == "Ground Branch":
    ping = ctx.guild.get_role(1123235373858963517)
    image = "https://i.ibb.co/m0YD7nW/header.jpg"
    embedcolor = 0x046466
    thumbnail = "https://i.ibb.co/T8nMNX7/F9-S7w-PPbs-AAhxn-Q.jpg"

  if ping is not None:
    embedVar = discord.Embed(title="ATTENTION SOLDIERS",
                             description="",
                             color=embedcolor)
    embedVar.set_author(name="Tactical Squad",
                        icon_url="https://i.ibb.co/GCGtxKs/maxresdefault.jpg")
    embedVar.set_footer(
        text="Interact with the buttons below to join or ignore the squad!")
    embedVar.add_field(
        name="NEW INVITE TO SQUAD",
        value=
        f"{ctx.author.mention} created a new squad!\n\nGame: **{game}**\nDate: **{date}**\nTime: **{time}**",
        inline=False)
    embedVar.add_field(name="MEMBER:", value="", inline=False)
    embedVar.add_field(name=f"✅ {ctx.author.display_name}",
                       value="\u200B",
                       inline=False)
    if image is not None:
      embedVar.set_image(url=image)
    if thumbnail is not None:
      embedVar.set_thumbnail(url=thumbnail)
      view = Squad()
    await ctx.respond("Sent", ephemeral=True)
    await ctx.send(content=f"{ping.mention}", view=view, embed=embedVar)
  else:
    await ctx.respond("Error: Invalid game selected", ephemeral=True)



bot.run(os.getenv('TOKEN'))
