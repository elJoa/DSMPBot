import json
import platform
import time
import discord
import constantes
import asyncio
import paramiko
import minestat
from discord.ext.commands import Bot
from mcstatus import MinecraftServer

client = Bot(command_prefix=constantes.PREFIX, case_insensitive=True)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
VERSION = '1.5-dev'
estaba_on = True


def obtener_logo_servidor():
	return 'https://cdn.discordapp.com/attachments/424759167845138433/735259436008079420/dogesthetic_nuevo_logo.png'


def establecer_estaba_on(valor):
	global estaba_on
	estaba_on = valor


def obtener_estaba_on():
	global estaba_on
	return estaba_on


def footer_embed(context):
	return 'Comando solicitado por {}. \nDSMPBot v{}'.format(str(context.author), VERSION)


def conectar_ssh(comando):
	ssh.connect(constantes.SSH_HOST, port=22, username=constantes.SSH_USER, password=constantes.SSH_PASS)
	(sshin, sshout, ssherr) = ssh.exec_command(comando)
	resultado = sshout.read().decode('utf8').strip()
	ssh.close()
	return resultado


async def ver_estado_servidor_loop(canal_on_off):
	while True:
		servidor = minestat.MineStat(constantes.IP, 25565)
		if servidor.latency is not None:
			if not obtener_estaba_on():
				await canal_on_off.send('¡El servidor está ON!')
				establecer_estaba_on(True)
		else:
			if obtener_estaba_on():
				await canal_on_off.send('¡El servidor está OFF!')
				establecer_estaba_on(False)
		
		await asyncio.sleep(15)


@client.event
async def on_ready():
	canal_on_off = client.get_channel(constantes.CANAL_ON_OFF)
	client.loop.create_task(ver_estado_servidor_loop(canal_on_off))
	await client.change_presence(activity=discord.Game('DSMP - $comandos'))
	print('-----------------------------------------------')
	print('Logueado como {}'.format(client.user))
	print('Versión de Discord.py: {}'.format(discord.__version__))
	print('-----------------------------------------------')


@client.command(name='proyectos', pass_context=True)
async def proyectos(context):
	with open('proyectos_activos.dsmp') as archivo:
		proyectos_activos = json.load(archivo)
		if proyectos_activos['proyectos']:
			proyectos_activos_string = ''
			for p in proyectos_activos['proyectos']:
				nombre_proyecto = p['nombre']
				descripcion_proyecto = p['descripcion']
				autor_proyecto = p['autor']
				prioridad_proyecto = p['prioridad']
				proyectos_activos_string += '{}:\n\nDescripción: {}\nAutor: {}\nPrioridad: {}\n\n'.format(
					nombre_proyecto, descripcion_proyecto, autor_proyecto, prioridad_proyecto
				)
		else:
			proyectos_activos_string = 'No hay proyectos activos.'

	estado_embed = discord.Embed(color=0x00FF00)
	estado_embed.set_thumbnail(url=obtener_logo_servidor())

	estado_embed.add_field(
		name='Proyectos activos:',
		value=proyectos_activos_string
	)

	estado_embed.set_footer(text=footer_embed(context))
	await context.message.channel.send(embed=estado_embed)


@client.command(name='reiniciar', pass_context=True)
async def reiniciar(context):
	if context.message.author.id in constantes.PERMISOS_REINICIO:
		try:
			conectar_ssh('systemctl restart dsmp')
			
			estado_embed = discord.Embed(
				description='{} reinició el servidor.'.format(context.author),
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
		servidor = minestat.MineStat(constantes.IP, 25565)
		servidor_jugadores = MinecraftServer(constantes.IP, 25565)
		
		estado_jugadores = servidor_jugadores.status().raw
		
		try:
			resultado_peso = conectar_ssh('du -sh /opt/DSMP/*/ | sort -rh | head -3')
			peso_end = resultado_peso.splitlines()[0].split('/')[0]
			peso_world = resultado_peso.splitlines()[1].split('/')[0]
			peso_nether = resultado_peso.splitlines()[2].split('/')[0]
		except:
			peso_end = 'ERROR'
			peso_nether = 'ERROR'
			peso_world = 'ERROR'
		
		# Mostrar datos
		estado_servidor = 'INACTIVO'
		nombres_jugadores = ''
		for x in range(0, servidor_jugadores.status().players.online):
			nombres_jugadores += str(json.loads(json.dumps(estado_jugadores))['players']['sample'][x]['name'])
			nombres_jugadores += ', '
		
		nombres_jugadores = nombres_jugadores.rstrip(', ')
		temp_jugadores = nombres_jugadores[::-1]
		temp_jugadores_2 = temp_jugadores.replace(', '[::-1], ' y '[::-1], 1)
		nombres_jugadores = temp_jugadores_2[::-1]
		
		estado_jugadores = '0/{}'.format(servidor.max_players)
		
		if servidor.version is not None:
			estado_servidor = 'ACTIVO'
		
		if servidor.current_players != 0:
			estado_jugadores = '{}/{} ({})'.format(
				servidor.current_players, servidor.max_players, nombres_jugadores
			)
		
		if estado_servidor == 'ACTIVO':
			color_embed = 0x00FF00
		else:
			color_embed = 0xCC0000
		
		estado_embed = discord.Embed(color=color_embed)
		estado_embed.set_thumbnail(url=obtener_logo_servidor())
		
		estado_embed.add_field(
			name='Estado del servidor:',
			value=estado_servidor,
			inline=False
		)
		
		estado_embed.add_field(
			name='Tamaño del overworld:',
			value=peso_world,
			inline=False
		)
		
		estado_embed.add_field(
			name='Tamaño del end:',
			value=peso_end,
			inline=False
		)
		
		estado_embed.add_field(
			name='Tamaño del nether:',
			value=peso_nether,
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
	reglas_embed.set_thumbnail(url=obtener_logo_servidor())
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


@client.command(name='latencia', pass_context=True)
async def latencia(context):
	tiempo = time.monotonic()
	mensaje = await context.message.channel.send("Midiendo mi latencia.")
	ping = (time.monotonic() - tiempo) * 1000
	await mensaje.edit(content='La latencia entre Discord y yo es de {} ms.'.format(int(ping)))


@client.command(name='sobredsmp', pass_context=True)
async def sobredsmp(context):
	infodsmp = discord.Embed(
		description='Dogesthetic SMP es un servidor survival en el que se mezcla el ámbito técnico, estético y sobre '
		'todo cooperativo. Es un servidor en el que se pueden hacer muchos proyectos y experimentos, '
		'este es un servidor serio y por esta razón se necesita rellenar un formulario para entrar. El '
		'formulario lo puedes encontrar en <#437781641201451010>, donde encontrarás instrucciones.',
		color=0x00FF00
	)
	infodsmp.set_thumbnail(url=obtener_logo_servidor())
	infodsmp.set_footer(text=footer_embed(context))
	await context.message.channel.send(embed=infodsmp)


@client.command(name='ip', pass_context=True)
async def ip(context):
	ip_embed = discord.Embed(color=0x00FF00)
	ip_embed.set_thumbnail(url=obtener_logo_servidor())
	ip_embed.add_field(
		name='Para obtener la ip:',
		value='<#483373646253916171>'
	)
	ip_embed.set_footer(text=footer_embed(context))
	await context.message.channel.send(embed=ip_embed)


@client.command(name='comandos', pass_context=True)
async def comandos(context):
	comandos_embed = discord.Embed(color=0x00FF00)
	comandos_embed.set_thumbnail(url=obtener_logo_servidor())
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
		value='$estado',
		inline=False
	)
	comandos_embed.add_field(
		name='Mi latencia:',
		value='$latencia'
	)
	comandos_embed.set_footer(text=footer_embed(context))
	await context.message.channel.send(embed=comandos_embed)


@client.command(name='version', pass_context=True)
async def version(context):
	version_embed = discord.Embed(color=0x00FF00)
	version_embed.set_thumbnail(url=obtener_logo_servidor())
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
		value='{} {}'.format(platform.system(), platform.release()),
		inline=False
	)
	version_embed.add_field(
		name='Repositorio de GitHub:',
		value='<https://github.com/elJoa/DSMPBot>'
	)
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
		
		if numero > 400:
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
async def limpiar_error(context, mensaje):
	await context.message.delete()
	error_embed = discord.Embed(
		title='¡Vaya!',
		description='¡No colocaste ningún argumento!',
		color=0xCC0000
	)
	mensaje = await context.message.channel.send(embed=error_embed)
	await asyncio.sleep(2)
	await mensaje.delete()


@añadirproyecto.error
async def añadirproyecto_error(context, mensaje):
	await context.message.delete()
	error_embed = discord.Embed(
		title='¡Vaya!',
		description='Uso correcto del comando: $añadirproyecto (Nombre del proyecto) (Descripción del proyecto) (Autor/es del proyecto) (Prioridad, puede ser Baja, Media o Alta).\n\n$añadirproyecto "Granja de guardianes" "Granja que da mucho lag" "Sugus, Poporonga y Benjathje" "MEDIA"',
		color=0xCC0000
	)
	mensaje = await context.message.channel.send(embed=error_embed)
	await asyncio.sleep(15)
	await mensaje.delete()
	
client.run(constantes.TOKEN)
