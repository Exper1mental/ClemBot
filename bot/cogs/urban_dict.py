# Thomas Delvaux
# 12-15-2020

# API Used:
# https://rapidapi.com/community/api/urban-dictionary/endpoints

import logging

import discord
import discord.ext.commands as commands
from bot.messaging.events import Events
from bot.bot_secrets import BotSecrets
from bot.consts import Colors

#import requests
import aiohttp
import asyncio
import re

log = logging.getLogger(__name__)

class UrbanDictCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.api_key = BotSecrets.get_instance().urbandict_key
        self.wordPages = []

    def getPageData(self,word,res_txt):
        pages = []

        w_def = re.findall(r'definition":"(.*?)","permalink', res_txt)

        #pages = [f'Definition: {w_def[0]}']

        for i in range(len(w_def)):
            page = f'Definition: {w_def[i]}'
            #page = page.replace('*',' | ')
            pages.append(page)

        """
        for i in enumerate(m1):
            print(m1[i])
            print('\n')
        """

        return pages

    @commands.command()
    async def urban(self, ctx, word):
        """
        Given a word, find its definition and any other relevant information
        
        USE: define <word>
        EXAMPLE: define schadenfreude
        For phrases, use underscores
        EXAMPLE: define computer_science
        """

        actualWord = word.replace("_"," ")
        word = word.replace("_","%20").lower()

        url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"
        querystring = {"term":word}
        # API Key Needs to get Moved to BotSecrets
        headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com"
            }

        """
        with requests.request("GET", url, headers=headers, params=querystring) as response:
            res_txt = response.text
            self.wordPages = self.getPageData(word,res_txt)
        """

        async with aiohttp.request("GET", url, headers=headers, params=querystring) as response:
            if (response.status == 200):
                res_txt = await response.text()
                wordPages = self.getPageData(word,res_txt)
            
            else:
                embed = discord.Embed(title='Urban Dictionary', color=Colors.Error)
                ErrMsg = f'Error Code: {response.status}'
                embed.add_field(name='Error with API', value=ErrMsg, inline=False)
                await ctx.send(embed=embed)
                return

            await self.bot.messenger.publish(Events.on_set_pageable,
                embed_name = 'Urban Dictionary',
                field_title = f'Word: {actualWord}',
                pages = wordPages,
                author = ctx.author,
                channel = ctx.channel)


def setup(bot):
    bot.add_cog(UrbanDictCog(bot))