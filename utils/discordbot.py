import os, httpx, disnake, dotenv, psycopg2, asyncio, base64, requests
from openai import OpenAI
from dotenv import load_dotenv
from disnake.ext import commands
from disnake import TextInputStyle
from cryptography.fernet import Fernet
load_dotenv()

bot = commands.Bot(intents=disnake.Intents.all())
conn = psycopg2.connect(database=os.getenv('DATABASENAME'), host=os.getenv('DATABASEHOST'), user=os.getenv('DATABASEUSER'), password=os.getenv('DATABASEPASSWORD'))
fernet_key = os.getenv("fernetkey")
f = Fernet(fernet_key)

def fencrypt(string):
	ciphertext = f.encrypt(string.encode())
	encoded = base64.b64encode(ciphertext).decode()
	return encoded

def fdecrypt(string):
	ciphertext = base64.b64decode(string)
	result = f.decrypt(ciphertext)
	return result

class MyModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Secret 1",
                placeholder="Your Secret 1",
                custom_id="secret_1",
                style=TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Secret 2",
                placeholder="Your Secret 2",
                custom_id="secret_2",
                style=TextInputStyle.short,
                max_length=50,
            ),
        ]
        super().__init__(title="Insert Token", components=components)
    async def callback(self, inter: disnake.ModalInteraction):
    	secret1 = inter.text_values.get("secret_1")
    	secret2 = inter.text_values.get("secret_2")
    	user_id_local = inter.user.id
    	field1 = fencrypt(secret1)
    	field2 = fencrypt(secret2)
    	cursor = conn.cursor()
    	cursor.execute(
    		"SELECT field1 FROM public.tokens WHERE user_id=%s", (str(user_id_local),)
    	)
    	result = cursor.fetchone()
    	if result:
    		update_query = """ UPDATE public.tokens SET field1 = %s, field2 = %s WHERE user_id = %s """
    		data = (field1, field2, str(user_id_local))
    		cursor.execute(update_query, data)
    		conn.commit()
    	else:
	    	insert_query = """ INSERT INTO public.tokens (user_id, field1, field2) VALUES (%s, %s, %s); """
	    	data = (user_id_local, field1, field22)
	    	cursor.execute(insert_query, data)
	    	conn.commit()
    	await inter.response.send_message(f"Successfully sent!!!")


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
		await ctx.response.send_message("Deployment works!!!")

	@bot.slash_command(description="Get trading 212 balance.")
	async def getbalance(inter, ctx):
		apis_trading_212_public_api_yaml = "https://demo.trading212.com"
		url = "https://demo.trading212.com/api/v0/equity/account/cash"
		user_id_local = ctx.user.id

		cursor = conn.cursor()

		cursor.execute("SELECT field1, field2 FROM public.tokens WHERE user_id=%s", (str(user_id_local),))

		result = cursor.fetchone()

		secret1 = fdecrypt(result[0])
		secret2 = fdecrypt(result[1])
		response = requests.get(url, auth=(secret1, secret2))
		if response:
			data = response.json()
		else:
			data = "Failed"

		embed = disnake.Embed(
		    title="Trading 212 Balance",
		    color=disnake.Colour.blue(),
		)

		embed.set_author(
		    name="Trading Bot",
		)
		embed.add_field(name="Total", value=str(data["total"]), inline=True)
		embed.add_field(name="Free", value=str(data["free"]), inline=True)
		embed.add_field(name="Invested", value=str(data["invested"]), inline=True)
		embed.add_field(name="Blocked", value=str(data["blocked"]), inline=True)

		await ctx.response.send_message(embed=embed)

	@bot.slash_command(description="Authenticate")
	async def auth(self, inter: disnake.AppCmdInter):
		await inter.response.send_modal(modal=MyModal())

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