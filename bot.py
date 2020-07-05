import platform
import discord
import minestat  # ¡Gracias a los creadores de minestat! Sin ellos este bot no existiría.
import constantes  # Este archivo contiene TOKEN, PREFIX, IP, CANAL_ON_OFF y ADMINISTRADORES.
import asyncio
from discord.ext.commands import Bot

client = Bot(command_prefix=constantes.PREFIX)
VERSION = '0.2.0'
servidor = minestat.MineStat(constantes.IP, 25565)
estabaON = True
canalOnOff = None


def obtener_estaba_on():
	return estabaON


async def establecer_estaba_on(valor):
	global estabaON
	estabaON = valor


async def ver_estado_servidor():
	while True:
		if servidor.online:
			if not obtener_estaba_on():
				await canalOnOff.send('¡El servidor está ON!')
				await establecer_estaba_on(True)
		else:
			if obtener_estaba_on():
				await canalOnOff.send('¡El servidor está OFF!')
				await establecer_estaba_on(False)

		await asyncio.sleep(10)


@client.event
async def on_ready():
	global canalOnOff
	canalOnOff = client.get_channel(constantes.CANAL_ON_OFF)
	client.loop.create_task(ver_estado_servidor())
	await client.change_presence(activity=discord.Game('DSMP - $comandos'))
	print('-----------------------------------------------')
	print('Logueado como ' + client.user.name)
	print('Versión de Discord.py: ', discord.__version__)
	print('-----------------------------------------------')


@client.command(name='reglas', pass_context=True)
async def reglas(context):
	reglas = discord.Embed(color=0x00FF00)
	reglas.set_thumbnail(url='https://i.imgur.com/j39vdJs.png')
	reglas.add_field(name='Regla 1:', value='No robar items ni duplicarlos.', inline=False)
	reglas.add_field(name='Regla 2:', value='No usar ningún tipo de hacks (se incluye el X-Ray).', inline=False)
	reglas.add_field(name='Regla 3:', value='No usar mods que den algún tipo de ventaja.', inline=False)
	reglas.add_field(name='Regla 4:', value='Cooperar con lo que puedas en el servidor.', inline=False)
	reglas.add_field(name='Regla 5:', value='Evitar la toxicidad en su totalidad.', inline=False)
	reglas.add_field(name='Regla 6:', value='En lo posible, tener la base en un radio de 2000 bloques desde 0 0.', inline=False)
	reglas.add_field(name='Regla 7:', value='La única granja que está permitida en los spawnchunks es la de hierro, no animales y no aldeanos.', inline=False)
	reglas.add_field(name='Regla 8:', value='El PvP está activado pero matar jugadores para lootearlos está prohibido.', inline=False)
	reglas.add_field(name='Regla 9:', value='No destruir ni dañar de ninguna manera las construcciones de los demás.', inline=False)
	reglas.set_footer(text='Comando solicitado por ' + str(context.author))
	await context.message.channel.send(embed=reglas)


@client.command(name='sobredsmp', pass_context=True)
async def sobredsmp(context):
	infodsmp = discord.Embed(description='Dogesthetic SMP es un servidor survival en el que se mezcla el ámbito '
										 'técnico, estético y sobre todo cooperativo. Es un servidor en el que se '
										 'pueden hacer muchos proyectos y experimentos, este es un servidor serio y por '
										 'esta razón se necesita rellenar un formulario para entrar. El formulario lo '
										 'puedes encontrar en <#437781641201451010>, donde encontrarás instrucciones.',
							 color=0x00FF00)
	infodsmp.set_thumbnail(url='https://i.imgur.com/j39vdJs.png')
	infodsmp.set_footer(text='Comando solicitado por ' + str(context.author))
	await context.message.channel.send(embed=infodsmp)


@client.command(name='ip', pass_context=True)
async def ip(context):
	ip = discord.Embed(color=0x00FF00)
	ip.set_thumbnail(url='https://i.imgur.com/j39vdJs.png')
	ip.add_field(name='Para obtener la ip:', value='<#483373646253916171>', inline=False)
	ip.set_footer(text='Comando solicitado por ' + str(context.author))
	await context.message.channel.send(embed=ip)


@client.command(name='comandos', pass_context=True)
async def comandos(context):
	comandos = discord.Embed(color=0x00FF00)
	comandos.set_thumbnail(url='https://i.imgur.com/j39vdJs.png')
	comandos.add_field(name='Reglas del servidor:', value='$reglas', inline=False)
	comandos.add_field(name='Información sobre el servidor:', value='$sobredsmp', inline=False)
	comandos.add_field(name='IP del servidor:', value='$ip', inline=False)
	comandos.add_field(name='Versión del bot:', value='$version', inline=False)
	comandos.set_footer(text='Comando solicitado por ' + str(context.author))
	await context.message.channel.send(embed=comandos)


@client.command(name='version', pass_context=True)
async def version(context):
	version = discord.Embed(color=0x00FF00)
	version.set_thumbnail(url='https://i.imgur.com/j39vdJs.png')
	version.add_field(name='Versión de discord.py:', value=discord.__version__, inline=False)
	version.add_field(name='Versión de Dogesthetic:', value=VERSION, inline=False)
	version.add_field(name='Versión de Python:', value=platform.python_version(), inline=False)
	version.add_field(name='Actualmente hosteado en:', value=platform.system() + ' ' + platform.release(), inline=False)
	version.add_field(name='Repositorio de GitHub:', value='<https://github.com/elJoa/Dogesthetic-Bot>')
	version.set_footer(text='Comando solicitado por ' + str(context.author))
	await context.message.channel.send(embed=version)


client.run(constantes.TOKEN)
