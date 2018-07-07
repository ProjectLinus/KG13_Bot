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




testBotServerId = '410296221383786497'
t_ty = '300041462593224704'

roomDict = {}
roomDict[testBotServerId] = ['kitchen','lounge','elevator','control-room']
roomDict[t_ty] = []

serverIdList = [testBotServerId]

serverLocked = {}

for id in serverIdList:
    serverLocked[id] = {}
    for room in roomDict[id]:
        serverLocked[id][room] = True


print(serverLocked)




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
        print(server.name, server.id)
        for channel in server.channels:
            if(channel.name in roomDict[server.id]):
                await channelLock(server,channel)
                print(channel.name + " was locked.")




@bot.command(name='check',pass_context=True)
async def _check(ctx):
    """
    !check (user mentions) #channel
    """
    user_mentions = ctx.message.mentions
    channel_mentions = ctx.message.channel_mentions

    for channel in channel_mentions:
        if(channel.permissions_for(ctx.message.author).administrator):
            for user in user_mentions:
                outputUserString = "```Permissions for " + user.name + " in " + channel.name + ": \n"
                permissionsUser = await checkUserPerms(channel.permissions_for(user))       #read_messages; send_messages; add_reactions;
                outputUserString += "Reading messages: " + permissionsUser["read_messages"] + "\n"
                outputUserString += "Sending messages: " + permissionsUser["send_messages"] + "\n"
                outputUserString += "Reacting to messages: " + permissionsUser["add_reactions"] + "```"
                await bot.send_message(ctx.message.channel,outputUserString)
                
    



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



@bot.command(name='move',pass_context=True)
async def _move(ctx):

    message_string = ctx.message.content.split()
    channelName = message_string[1]
    user = ctx.message.author
    server = ctx.message.server
    channel = await getChannel(server,channelName)

    await channelMove(server,channel,user)
    print(user.name + " moved to " + channel.name + ".")
    
    




@bot.command(name='list',pass_context=True)
async def _list(ctx):

    message = ""
    server = ctx.message.server
    unlockedChannels = []
    for key in serverLocked[server.id].keys():
        if(not serverLocked[server.id][key]):
            unlockedChannels.append(key)
    
    if(len(unlockedChannels) > 0):
        message += "You can currently access the following channels by typing !move [channel]:\n"
            
        for channel in unlockedChannels:
            message += channel.name + "\n"

    else:
        message += "All of the channels are locked at the moment. Please try again later, or contact the Administrator of your server."

    await bot.send_message(ctx.message.channel,message)
    



@bot.command(name="lock",pass_context=True)
async def _lock(ctx):

    channel = ctx.message.channel
    server = ctx.message.server

    if(channel.permissions_for(ctx.message.author).administrator):

        serverLocked[server.id][channel] = True
        await channelLock(server,channel)
        print(channel.name + " was succesfully locked.")



@bot.command(name="unlock",pass_context=True)
async def _unlock(ctx):

    channel = ctx.message.channel
    server = ctx.message.server

    if(channel.permissions_for(ctx.message.author).administrator):

        serverLocked[server.id][channel] = False
        print(channel.name + " was succesfully unlocked.")






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


@bot.event
async def checkUserPerms(permissionsUser):
    
    permArray = {}
    if(permissionsUser.read_messages):
        permArray["read_messages"] = "Enabled"
    else:
        permArray["read_messages"] = "Disabled"

    if(permissionsUser.send_messages):
        permArray["send_messages"] = "Enabled"
    else:
        permArray["send_messages"] = "Disabled"

    if(permissionsUser.add_reactions):
        permArray["add_reactions"] = "Enabled"
    else:
        permArray["add_reactions"] = "Disabled"

    return permArray



@bot.event
async def getChannel(server,channelName):
    for channel in server.channels:
        if(channel.name == channelName):
            return channel


@bot.event
async def channelLock(server,channel):
    for member in server.members:
        overwrite = discord.PermissionOverwrite()
        overwrite.read_messages = await readPerm(False,"all",member,channel)
        overwrite.send_messages = await sendPerm(False,"all",member,channel)
        overwrite.add_reactions = await reactPerm(False,"all",member,channel)
        await bot.edit_channel_permissions(channel,member,overwrite)
        
        
@bot.event
async def channelMove(server,targetChannel,member):

    for channel in server.channels:
        if(channel.name in roomDict[server.id]):
            overwrite = discord.PermissionOverwrite()
            overwrite.read_messages = await readPerm(False,"all",member,channel)
            overwrite.send_messages = await sendPerm(False,"all",member,channel)
            overwrite.add_reactions = await reactPerm(False,"all",member,channel)
            await bot.edit_channel_permissions(channel,member,overwrite)


    overwrite = discord.PermissionOverwrite()
    overwrite.read_messages = await readPerm(True,"all",member,targetChannel)
    overwrite.send_messages = await sendPerm(True,"all",member,targetChannel)
    overwrite.add_reactions = await reactPerm(True,"all",member,targetChannel)
    await bot.edit_channel_permissions(targetChannel,member,overwrite)
    
            


bot.run(Token.token)
