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



@bot.command(name='check',pass_context=True)
async def _check(ctx):
    """
    !check (user mentions)
    """
    user_mentions = ctx.message.mentions



@bot.command(name='perm',pass_context=True)
async def _perm(ctx):
    """
    !perm (e/d/enable/disable) (r/s/rct/read/send/react/all) (channels to specify) (user mentions) (role mentions)
    """   

    message_string = ctx.message.content.split()
    user_mentions = ctx.message.mentions
    channel_mentions = ctx.message.channel_mentions
    role_mentions = ctx.message.role_mentions
    perm_type = message_string[1]
    target_type = message_string[2]
    overwrite = discord.PermissionOverwrite()
    perm_result = await permTypeCheck(perm_type)
    
    for channel in channel_mentions:
        if(channel.permissions_for(ctx.message.author).administrator):
            for user in user_mentions:
                overwrite.read_messages = await readPerm(perm_result,target_type,user,channel)
                overwrite.send_messages = await sendPerm(perm_result,target_type,user,channel)
                overwrite.add_reactions = await reactPerm(perm_result,target_type,user,channel)
                await bot.edit_channel_permissions(channel,user,overwrite)
                print("Permissions successfully changed for " + user.name + " in " + channel.name + ".")
            for role in role_mentions:
                for member in ctx.message.server.members:
                    if role in member.roles:
                        overwrite.read_messages = await readPerm(perm_result,target_type,member,channel)
                        overwrite.send_messages = await sendPerm(perm_result,target_type,member,channel)
                        overwrite.add_reactions = await reactPerm(perm_result,target_type,member,channel)
                        await bot.edit_channel_permissions(channel,member,overwrite)
                        print("Permissions successfully changed for " + member.name + " of " + role.name + " in " + channel.name + ".")
        else:
            await bot.send_message(ctx.message.channel,"Error: You do not have the needed permissions to call this command. The command is only usable by administrators of the server.")



@bot.event
async def permTypeCheck(perm_type):
    if perm_type == "e" or perm_type == "enable":
        return True
    elif perm_type == "d" or perm_type == "disable":
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