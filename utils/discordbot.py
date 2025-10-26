import os
import httpx
import disnake
from openai import OpenAI
from dotenv import load_dotenv
from disnake.ext import commands
import asyncio
load_dotenv()

bot = commands.Bot(intents=disnake.Intents.all())

class ArtificialIntelligence():
	messages = [{"role": "system", "content": "You are a professionist trader assistant. Do not make too long messages because of the discord limitation. Keep in mind to only use English or Romanian"}]
	client = OpenAI(
    	api_key=os.getenv('grok_token'),
    	base_url="https://api.x.ai/v1",
    	timeout=httpx.Timeout(3600.0),
	)

	def get_message(self, message):
		self.messages.append({"role": "user", "content": message})
		response = self.client.chat.completions.create(
			model="grok-4",
			messages=self.messages,
			stream=False
		)
		self.messages.append(response.choices[0].message)
		return response.choices[0].message.content


grokPart = ArtificialIntelligence()

class DiscordBot():
	token = os.getenv('discord_token')
	@bot.slash_command(description="Command for test")
	async def test(inter, ctx):
		await ctx.response.send_message(f"")

	@bot.slash_command(description="Test deployment")
	async def testdeploy(inter, ctx):
		await ctx.response.send_message("Deployment works!!!!")
			

	@bot.event
	async def on_message(message):
		if message.author == bot.user:
			return
		if bot.user in message.mentions:
			async with message.channel.typing():
				response = grokPart.get_message(message.content)
				await message.reply(response)
	
	@bot.event
	async def on_ready():
		activity = disnake.Game(name="with Stocks 📈")
		await bot.change_presence(status=disnake.Status.idle, activity=activity)
	bot.run(token)