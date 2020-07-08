import platform
import discord
import constantes
import asyncio
import paramiko
import minestat
from discord.ext.commands import Bot

client = Bot(command_prefix=constantes.PREFIX)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
servidor = minestat.MineStat(constantes.IP, 25565)
VERSION = '1.0'
estaba_on = True


def establecer_estaba_on(valor):
	global estaba_on
	estaba_on = valor


def obtener_estaba_on():
	global estaba_on
	return estaba_on


def footer_embed(context):
	return 'Comando solicitado por {}. \nDSMPBot Ver: {}'.format(str(context.author), VERSION)


async def ver_estado_servidor_loop(canal_on_off):
	while True:
		if servidor.motd is not None:
			if not obtener_estaba_on():
				await canal_on_off.send('¡El servidor está ON!')
				establecer_estaba_on(True)
		else:
			if obtener_estaba_on():
				await canal_on_off.send('¡El servidor está OFF!')
				establecer_estaba_on(False)
		
		await asyncio.sleep(6)


@client.event
async def on_ready():
	canal_on_off = client.get_channel(constantes.CANAL_ON_OFF)
	client.loop.create_task(ver_estado_servidor_loop(canal_on_off))
	await client.change_presence(activity=discord.Game('DSMP - $comandos'))
	print('-----------------------------------------------')
	print('Logueado como {}'.format(client.user))
	print('Versión de Discord.py: {}'.format(discord.__version__))
	print('-----------------------------------------------')


@client.command(name='reiniciar', pass_context=True)
async def reiniciar(context):
	if context.message.author.id in constantes.PERMISOS_REINICIO:
		try:
			ssh.connect(constantes.SSH_HOST, port=22, username=constantes.SSH_USER, password=constantes.SSH_PASS)
			ssh.exec_command('systemctl restart dogesthetic')
			
			estado_embed = discord.Embed(
				description='{} está reiniciando el servidor.'.format(context.author),
				color=0x00FF00
			)
			
			await context.message.channel.send(embed=estado_embed)
		finally:
			ssh.close()
	else:
		await context.message.delete()
		error = discord.Embed(
			title='¡Vaya!',
			description='¡No tienes permisos para usar este comando, pequeño curioso!',
			color=0xCC0000
		)
		mensaje = await context.message.channel.send(embed=error)
		await asyncio.sleep(2)
		await mensaje.delete()


@client.command(name='estado', pass_context=True)
async def estado(context):
	try:
		# Obtener datos
		ssh.connect(constantes.SSH_HOST, port=22, username=constantes.SSH_USER, password=constantes.SSH_PASS)
		(sshin, sshout, ssherr) = ssh.exec_command('systemctl status dogesthetic | grep -i Active')
		resultado = sshout.read().decode('utf8').strip()
		
		# Mostrar datos
		estado_servicio = 'INACTIVO'
		estado_servidor = 'INACTIVO'
		estado_jugadores = 0
		
		if 'running' in resultado:
			estado_servicio = 'ACTIVO'
		
		if servidor.version is not None:
			estado_servidor = 'ACTIVO'
		
		if servidor.current_players is not None:
			estado_jugadores = servidor.current_players
		
		if estado_servidor == 'ACTIVO':
			color_embed = 0x00FF00
		else:
			color_embed = 0xCC0000
		
		estado_embed = discord.Embed(color=color_embed)
		estado_embed.set_thumbnail(url='https://i.imgur.com/j39vdJs.png')
		
		estado_embed.add_field(
			name='Estado del servicio:',
			value=estado_servicio,
			inline=False
		)
		
		estado_embed.add_field(
			name='Estado del servidor:',
			value=estado_servidor,
			inline=False
		)
		
		estado_embed.add_field(
			name='Jugadores activos:',
			value=estado_jugadores
		)
		
		estado_embed.set_footer(text=footer_embed(context))
		await context.message.channel.send(embed=estado_embed)
	finally:
		ssh.close()


@client.command(name='reglas', pass_context=True)
async def reglas(context):
	reglas_embed = discord.Embed(color=0x00FF00)
	reglas_embed.set_thumbnail(url='https://i.imgur.com/j39vdJs.png')
	reglas_embed.add_field(
		name='Regla 1:',
		value='No robar items ni duplicarlos.',
		inline=False
	)
	reglas_embed.add_field(
		name='Regla 2:',
		value='No usar ningún tipo de hacks (se incluye el X-Ray).',
		inline=False
	)
	reglas_embed.add_field(
		name='Regla 3:',
		value='No usar mods que den algún tipo de ventaja.',
		inline=False
	)
	reglas_embed.add_field(
		name='Regla 4:',
		value='Cooperar con lo que puedas en el servidor.',
		inline=False
	)
	reglas_embed.add_field(
		name='Regla 5:',
		value='Evitar la toxicidad en su totalidad.',
		inline=False
	)
	reglas_embed.add_field(
		name='Regla 6:',
		value='En lo posible, tener la base en un radio de 2000 bloques desde 0 0.',
		inline=False
	)
	reglas_embed.add_field(
		name='Regla 7:',
		value='La única granja que está permitida en los spawnchunks es la de hierro, no animales y no aldeanos.',
		inline=False
	)
	reglas_embed.add_field(
		name='Regla 8:',
		value='El PvP está activado pero matar jugadores para lootearlos está prohibido.',
		inline=False
	)
	reglas_embed.add_field(
		name='Regla 9:',
		value='No destruir ni dañar de ninguna manera las construcciones de los demás.'
	)
	reglas_embed.set_footer(text=footer_embed(context))
	await context.message.channel.send(embed=reglas_embed)


@client.command(name='sobredsmp', pass_context=True)
async def sobredsmp(context):
	infodsmp = discord.Embed(
		description='Dogesthetic SMP es un servidor survival en el que se mezcla el ámbito técnico, estético y sobre '
		'todo cooperativo. Es un servidor en el que se pueden hacer muchos proyectos y experimentos, '
		'este es un servidor serio y por esta razón se necesita rellenar un formulario para entrar. El '
		'formulario lo puedes encontrar en <#437781641201451010>, donde encontrarás instrucciones.',
		color=0x00FF00
	)
	infodsmp.set_thumbnail(url='https://i.imgur.com/j39vdJs.png')
	infodsmp.set_footer(text=footer_embed(context))
	await context.message.channel.send(embed=infodsmp)


@client.command(name='ip', pass_context=True)
async def ip(context):
	ip_embed = discord.Embed(color=0x00FF00)
	ip_embed.set_thumbnail(url='https://i.imgur.com/j39vdJs.png')
	ip_embed.add_field(
		name='Para obtener la ip:',
		value='<#483373646253916171>'
	)
	ip_embed.set_footer(text=footer_embed(context))
	await context.message.channel.send(embed=ip_embed)


@client.command(name='comandos', pass_context=True)
async def comandos(context):
	comandos_embed = discord.Embed(color=0x00FF00)
	comandos_embed.set_thumbnail(url='https://i.imgur.com/j39vdJs.png')
	comandos_embed.add_field(
		name='Reglas del servidor:',
		value='$reglas',
		inline=False
	)
	comandos_embed.add_field(
		name='Información sobre el servidor:',
		value='$sobredsmp',
		inline=False
	)
	comandos_embed.add_field(
		name='IP del servidor:',
		value='$ip',
		inline=False
	)
	comandos_embed.add_field(
		name='Versión del bot:',
		value='$version',
		inline=False
	)
	comandos_embed.add_field(
		name='Estado del servidor:',
		value='$estado'
	)
	comandos_embed.set_footer(text=footer_embed(context))
	await context.message.channel.send(embed=comandos_embed)


@client.command(name='version', pass_context=True)
async def version(context):
	version_embed = discord.Embed(color=0x00FF00)
	version_embed.set_thumbnail(url='https://i.imgur.com/j39vdJs.png')
	version_embed.add_field(
		name='Versión de discord.py:',
		value=discord.__version__,
		inline=False
	)
	version_embed.add_field(
		name='Versión de Dogesthetic:',
		value=VERSION,
		inline=False
	)
	version_embed.add_field(
		name='Versión de Python:',
		value=platform.python_version(),
		inline=False
	)
	version_embed.add_field(
		name='Actualmente hosteado en:',
		value='{} {}'.format(platform.system(), platform.release())
	)
	version_embed.add_field(name='Repositorio de GitHub:', value='<https://github.com/elJoa/DSMPBot>')
	version_embed.set_footer(text=footer_embed(context))
	await context.message.channel.send(embed=version_embed)


@client.command(name='callate', pass_context=True)
async def callate(context):
	if context.message.author.id in constantes.ADMINISTRADORES:
		await context.message.channel.send('Okey, okey. Me callo. :(')
		await client.close()
	else:
		await context.message.delete()
		error = discord.Embed(
			title='¡Vaya!',
			description='¡No tienes permisos para usar este comando, pequeño curioso!',
			color=0xCC0000
		)
		mensaje = await context.message.channel.send(embed=error)
		await asyncio.sleep(2)
		await mensaje.delete()


@client.command(name='dogedice', pass_context=True)
async def dogedice(context, *, mensaje):
	await context.message.delete()
	await context.message.channel.send(mensaje)


@client.command(name='limpiar', pass_context=True)
async def limpiar(context, numero):
	if context.message.author.id in constantes.ADMINISTRADORES:
		numero = int(numero)
		
		if numero > 100:
			await context.message.delete()
			error_embed = discord.Embed(
				title='¡Vaya!',
				description='¡El valor que colocaste es muy grande y probablemente iba a causar un error!',
				color=0xCC0000
			)
			mensaje = await context.message.channel.send(embed=error_embed)
			await asyncio.sleep(2)
			await mensaje.delete()
			return
		
		await context.message.delete()
		await context.message.channel.purge(limit=numero)
		
		if numero != 1:
			info_embed = discord.Embed(
				title='Fui utilizado para:',
				description='Eliminar {} mensajes.'.format(numero),
				color=0x00FF00
			)
		else:
			info_embed = discord.Embed(
				title='Fui utilizado para:',
				description='Eliminar {} mensaje.'.format(numero),
				color=0x00FF00
			)
		
		mensaje = await context.message.channel.send(embed=info_embed)
		await asyncio.sleep(2)
		await mensaje.delete()
	else:
		await context.message.delete()
		error_embed = discord.Embed(
			title='¡Vaya!',
			description='¡No tienes permisos para usar este comando, pequeño curioso!',
			color=0xCC0000
		)
		mensaje = await context.message.channel.send(embed=error_embed)
		await asyncio.sleep(2)
		await mensaje.delete()


@limpiar.error
async def limpiar_error(context):
	await context.message.delete()
	error_embed = discord.Embed(
		title='¡Vaya!',
		description='¡No colocaste ningún argumento!',
		color=0xCC0000
	)
	mensaje = await context.message.channel.send(embed=error_embed)
	await asyncio.sleep(2)
	await mensaje.delete()


client.run(constantes.TOKEN)
