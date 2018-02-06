import discord
from discord.ext import commands
from discord.ext.commands import Bot
import logging
from discord import utils
import asyncio
import Token

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log',encoding='utf-8',mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


bot = Bot(command_prefix='!')


@bot.event
async def on_ready():
    print('Logged in as')
    print('Name: ', bot.user.name)
    print('ID: ', bot.user.id)
    print(discord.__version__)
    print('------')
    for member in bot.get_all_members():
        print(member.name, member.id)
    print('------')
    for server in bot.servers:
        print(server.name, server.owner.name)


#!perm (e/d/enable/disable) (r/s/rct/read/send/react/all) (channels to specify) (user mentions)

@bot.command(name='perm',pass_context=True)
async def _perm(ctx):
    message_string = ctx.message.content.split()
    user_mentions = ctx.message.mentions
    channel_mentions = ctx.message.channel_mentions
    perm_type = message_string[0]
    target_type = message_string[1]
    overwrite = discord.PermissionOverwrite()
    for channel in channel_mentions:
        if(channel.permissions_for(ctx.message.author).administrator):
            for user in user_mentions:
                if(await checkPerm(perm_type)):
                    overwrite.read_messages = await readPerm(True,target_type,user,channel)
                    overwrite.send_messages = await sendPerm(True,target_type,user,channel)
                    overwrite.add_reactions = await reactPerm(True,target_type,user,channel)
                    await bot.edit_channel_permissions(channel,user,overwrite)
                    print(ctx.message.channel,"Permissions successfully enabled for " + user.name + " in " + channel.name + ".")
                elif(not await checkPerm(perm_type)):
                    overwrite.read_messages = await readPerm(False,target_type,user,channel)
                    overwrite.send_messages = await sendPerm(False,target_type,user,channel)
                    overwrite.add_reactions = await reactPerm(False,target_type,user,channel)
                    await bot.edit_channel_permissions(channel,user,overwrite)
                    print(ctx.message.channel,"Permissions successfully disabled for " + user.name + " in " + channel.name + ".")
                else:
                    print(ctx.message.channel,"Incorrect permission type; please call the command as following, picking one of the permission types and target types: \n ```\n!perm (e/d/enable/disable) (r/s/rct/read/send/react/all) (channels to specify) (user mentions)```")
                    break
        else:
            await bot.send_message(ctx.message.channel,"Error: You do not have the needed permissions to call this command. The command is only usable by administrators of the server.")



@bot.event
async def checkPerm(perm_type):
    if perm_type in ("e","enable"):
        return True
    elif perm_type in ("d","disable"):
        return False
    else:
        return None


@bot.event
async def readPerm(perm_bool, target_type,user,channel):
    if(perm_bool):
        if(target_type in ("r","s","rct","read","send","react","all")):
            return True
        else:
            return channel.permissions_for(user).read_messages
    elif(not perm_bool):
        if(target_type in ("r","read","all")):
            return False
        else:
            return channel.permissions_for(user).read_messages


@bot.event
async def sendPerm(perm_bool, target_type,user,channel):
    if(perm_bool):
        if(target_type in ("s","send","all")):
            return True
        else:
            return channel.permissions_for(user).send_messages
    elif(not perm_bool):
        if(target_type in ("r","read","s","send","all")):
            return False
        else:
            return channel.permissions_for(user).send_messages


@bot.event
async def reactPerm(perm_bool, target_type,user,channel):
    if(perm_bool):
        if(target_type in ("rct","react","all")):
            return True
        else:
            return channel.permissions_for(user).add_reactions
    elif(not perm_bool):
        if(target_type in ("r","read","rct","react","all")):
            return False
        else:
            return channel.permissions_for(user).add_reactions



bot.run(Token.token)