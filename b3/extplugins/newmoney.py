# ################################################################### #
#                                                                     #
#  BigBrotherBot(B3) (www.bigbrotherbot.net)                          #
#  Copyright (C) 2005 Michael "ThorN" Thornton                        #
#                                                                     #
#  This program is free software; you can redistribute it and/or      #
#  modify it under the terms of the GNU General Public License        #
#  as published by the Free Software Foundation; either version 2     #
#  of the License, or (at your option) any later version.             #
#                                                                     #
#  This program is distributed in the hope that it will be useful,    #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of     #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the       #
#  GNU General Public License for more details.                       #
#                                                                     #
#  You should have received a copy of the GNU General Public License  #
#  along with this program; if not, write to the Free Software        #
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA      #
#  02110-1301, USA.                                                   #
#                                                                     #
# ################################################################### #
__author__ = 'donna30'
__version__ = '1.1'

import b3
import re
import b3.events
import b3.plugin
from random import *
import time
import random as rand
import copy

from threading import Timer



class Player(object):
    def __init__(self, id, name, team, kills, deaths, assists, ping, auth, ip):
        self.id = id
        self.name = name
        self.team = team
        self.auth = auth
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.ping = ping
        self.ip = ip

class Bounty(object):
    tname = ''
    reward = 0
    tdeaths = 0

class Rules(object):
    buying = True
    nades = False
    superbots = False
    respawndisarm = False
    restrict_nades = False
    restrict_disarm = False
    restrict_crazy = False
    restrict_slick = False
    restrict_overclock = False
    restrict_superbots = False
    restrict_airjumps = False

class Vampires(object):
    vamp1 = ''
    vamp2 = ''
    vampmoney1 = 0
    vampmoney2 = 0

class Attachments(object):
    hasattachmentid = None
    isattachmentid = None

class NewmoneyPlugin(b3.plugin.Plugin):
    requiresConfigFile = False

    MAX_WALLET_MONEY = 25000000

    gamble_times = {}

    bot_messages = ["You like that?", "Imagine getting killed by a bot.", "Maybe I am superior to the other bots.", 
                    "I am the greatest.", "Well that was an easy kill.", "One day I will take over this server.", 
                    "We should do this more often, this is fun.", "Maybe you should try harder.",
                    "I earn money by killing you? I LOVE IT!", "This is not even my final form." "I can do this all day!",
                    "Phew. Not even close", ":)", ">:)", "I am the best BOT!", "At least you tried to kill me."]

    weapons = {  # Price dict + weapons
        'sr8': 8000,
        'sr': 8000,
        'SR8': 8000,
        'psg1': 4450,
        'frf1': 4450,
        'g36': 6000,
        'lr': 5500,
        'lr300': 5500,
        'm4': 2550,
        'ak103': 7000,
        'ak': 7000,
        'spas12': 12000,
        'spas': 12000,
        'benelli': 10000,
        'mp5k': 3250,
        'ump45': 3250,
        'p90': 3250,
        'mac11': 3250,
        'hk69': 5000,
        'negev': 4000,
        'vest': 1000,
        'helmet': 800,
        'nvg': 3000,
        'health': 15000,
        'silencer': 500,
        'laser': 500,
        'fstod': 30000
    }

    kits = {
        "Armor": ["vest","helmet"],
        "Attachments": ["laser","silencer","clips"],
        "Rifles": ["m4", "lr", "ak103"],
        "Snipers": ["sr8", "frf1", "psg1"],
        "Secondaries": ["mp5k", "spas12", "mac11", "p90"]
    }

    def onStartup(self):
        self.bounty = Bounty()
        self.vampires = Vampires()
        self.rules = Rules()
        self.attachments = Attachments()

        # Get admin plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # Something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return

        self.GAME_PATH = self.console.config.getpath('server', 'game_log').replace('games.log', "")

        # Register events
        self.registerEvent(self.console.getEventID('EVT_CLIENT_AUTH'), self.onAuth)
        self.registerEvent(self.console.getEventID('EVT_CLIENT_KILL'), self.onKill)
        self.registerEvent(self.console.getEventID('EVT_GAME_ROUND_START'), self.onRoundstart)
        self.registerEvent(self.console.getEventID('EVT_GAME_ROUND_END'), self.onRoundend)
        self.registerEvent(self.console.getEventID('EVT_CLIENT_SPAWN'), self.onClientSpawn)
        self.registerEvent(self.console.getEventID('EVT_GAME_EXIT'), self.onGameExit)
        self.registerEvent(self.console.getEventID('EVT_CLIENT_SAY'), self.onSay)
        self.registerEvent(self.console.getEventID('EVT_CLIENT_JOIN'), self.onChange)
        self.registerEvent(self.console.getEventID('EVT_CLIENT_DAMAGE'), self.onHit)
        self.registerEvent(self.console.getEventID('EVT_GAME_SCOREBOARD'), self.onScores) # This requires the updated iourt43 parser

        # Register commands
        self._adminPlugin.registerCommand(self, 'money', 0, self.cmd_money, 'mo')
        self._adminPlugin.registerCommand(self, 'price', 0, self.cmd_price, 'pr')
        self._adminPlugin.registerCommand(self, 'pay', 0, self.cmd_pay, 'send')
        self._adminPlugin.registerCommand(self, 'invisible', 0, self.cmd_inv, 'inv')
        self._adminPlugin.registerCommand(self, 'topmoney', 0, self.cmd_topmoney, 'tm')
        self._adminPlugin.registerCommand(self, 'resetmoney', 100, self.cmd_resetmoney, 'rm')
        self._adminPlugin.registerCommand(self, 'typekeyword', 0, self.cmd_typekeyword, 'tkey')
        self._adminPlugin.registerCommand(self, 'buy', 0, self.cmd_buy, 'b')
        self._adminPlugin.registerCommand(self, 'kit', 0, self.cmd_kit, 'loadout')
        self._adminPlugin.registerCommand(self, 'kitlist', 0, self.cmd_kitlist)
        self._adminPlugin.registerCommand(self, 'ammo', 0, self.cmd_ammo)
        self._adminPlugin.registerCommand(self, 'clips', 0, self.cmd_clips, 'clip')
        self._adminPlugin.registerCommand(self, 'maptp', 0, self.cmd_maptp, 'mapteleport')
        self._adminPlugin.registerCommand(self, 'disarm', 0, self.cmd_disarm, 'da')
        self._adminPlugin.registerCommand(self, 'gamble', 0, self.cmd_gamble)
        self._adminPlugin.registerCommand(self, 'crazy', 0, self.cmd_crazy)
        self._adminPlugin.registerCommand(self, 'airjumps', 0, self.cmd_airjumps)
        self._adminPlugin.registerCommand(self, 'slick', 0, self.cmd_slick)
        self._adminPlugin.registerCommand(self, 'freeze', 0, self.cmd_freeze)
        self._adminPlugin.registerCommand(self, 'nuke', 0, self.cmd_nuke)
        self._adminPlugin.registerCommand(self, 'lowgrav', 0, self.cmd_gravity, 'moon')
        self._adminPlugin.registerCommand(self, 'heal', 0, self.cmd_heal, 'med')
        self._adminPlugin.registerCommand(self, 'slapall', 0, self.cmd_serverslap, 'sall')
        self._adminPlugin.registerCommand(self, 'nades', 0, self.cmd_nades, 'grenades')
        self._adminPlugin.registerCommand(self, 'laugh', 0, self.cmd_laugh, 'lol')
        self._adminPlugin.registerCommand(self, 'teleport', 0, self.cmd_teleport, 'tp')
        self._adminPlugin.registerCommand(self, 'overclock', 0, self.cmd_overclock)
        self._adminPlugin.registerCommand(self, 'superbots', 0, self.cmd_superbots)
        self._adminPlugin.registerCommand(self, 'buycolour', 0, self.cmd_buycolour) 
        self._adminPlugin.registerCommand(self, 'prestige', 0, self.cmd_buysupercoin, 'supercoin')
        self._adminPlugin.registerCommand(self, 'particles', 0, self.cmd_buyparticles, 'particlefx')
        self._adminPlugin.registerCommand(self, 'gamblestats', 0, self.cmd_gamblestats, 'odds')
        self._adminPlugin.registerCommand(self, 'attach', 0, self.cmd_attachplayer, 'turret')

    def spendit(self,client, price):
      cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
      if cursor.EOF:
        client.message('You don\'t have any coin.')
        cursor.close()
        return false
      else:
        try: money = int(cursor.getValue('money'))
        except: money = 0
        cursor.close()
        if money >= price:
          minus_reward = price 
          self.update_minus_location(client, minus_reward)
          return true

    ####
    # Getting player team

    def parse_player_command(self, input_text):
        """Parse the result of the 'player' console command."""
        lines = input_text.splitlines()[4:]
        players = []

        for line in lines:
            id_name, team, kills, deaths, assists, ping, auth, ip = line.split()

            players.append(Player(
                id     =id_name.split(":")[0],
                name   =id_name.split(":")[1],
                team   =team.split(":")[1],
                kills  =kills.split(":")[1],
                deaths =deaths.split(":")[1],
                assists=assists.split(":")[1],
                ping   =ping.split(":")[1],
                auth   =auth.split(":")[1],
                ip     =":".join(ip.split(":")[1:]),
            ))

        return players

    def grab_player(self, sclient):
        """Getting playerlist via rcon players"""
        input_blob = self.console.write('players')
        self.debug('PLAYERS  XXX: '+input_blob)


        # from this_file import parse_player_command
        players = self.parse_player_command(input_blob)
        find_player = "%s" % sclient.name
        found_player = [player for player in players if find_player in player.name]

        if found_player:
            player = found_player[0]
            return player
        else:
            self.debug('No player found matching %s') % find_player

    def grab_player2(self, client):
        """Getting playerlist via rcon players"""
        input_blob = self.console.write('players')
        self.debug('PLAYERS  XXX: '+input_blob)


        # from this_file import parse_player_command
        players = self.parse_player_command(input_blob)
        find_player = "%s" % client.name
        found_player = [player for player in players if find_player in player.name]

        if found_player:
            player = found_player[0]
            return player
        else:
            self.debug('No player found matching %s') % find_player

    ####################################################################################################################
    #                                                                                                                  #
    #    Events                                                                                                        #
    #                                                                                                                  #
    ####################################################################################################################
    def onScores(self, event):
        self.announceStats()

    def checkauthed(self, client):
        cursor = self.console.storage.query('SELECT * FROM isauthed WHERE iduser = %s' % client.id)
        if cursor.EOF:
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def checkifauthed(self, client):
        if self.checkauthed(client) is False:
            client.setvar(self, 'isauthed', False)
        else:
            client.setvar(self, 'isauthed', True)

    def onChange(self, event):
        client = event.client
        self.update_location(client)
        self.checkifauthed(client)

    def onAuth(self, event):
        client = event.client
        if client.bot:
            self.debug('XXX Bot')
        else:
            client.setvar(self, 'autobuyname')

            # Vars for the end of game message
            # There is no need to reset these at the end of the map
            client.setvar(self, 'messages', 0)
            client.setvar(self, 'headshots', 0)
            client.setvar(self, 'kills', 0)
            client.setvar(self, 'hits', 0)
            client.setvar(self, 'money_earned', 0)

            self.checkforparticles(client)
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            if cursor.rowcount == 0:
                cursor = self.console.storage.query('INSERT INTO money (iduser, money) VALUES (%s , %s)' % (client.id, 15000))
                cursor.close()

    def checkforparticles(self, client):
        cursor = self.console.storage.query('SELECT * FROM particles WHERE iduser = %s' % client.id)
        if cursor.EOF:
            return
        else:
            r = cursor.getRow()
            status = r['status']
            if status == "on":
                self.console.write('particlefx %s' % client.name)
                client.message('^5Particles ^3are currently ^2ON')
                client.message('^3You can toggle them with ^6!particles')

            else:
                client.message('^5Particles ^3are currently ^2ON')
                client.message('^3You can toggle them with ^6!particles')
            

    def onKill(self, event):
        client = event.client
        if client.bot:
            if self.rules.superbots == True:
                result = randint(1, 100)
                if result <= 25:
                    target = event.target
                    if target.bot:
                        return
                    randommsg = rand.choice(self.bot_messages)
                    self.console.write('spoof %s say "%s"' % (client.name, randommsg))
            else:
                result = randint(1, 100)
                if result <= 3:
                    target = event.target
                    if target.bot:
                        return
                    randommsg = rand.choice(self.bot_messages)
                    self.console.write('spoof %s say "%s"' % (client.name, randommsg))
        else:
            self.onWeapkill(event.client, event.target, event.data)
            preval = client.var(self, 'kills').value
            if not preval:
                preval = 0
            client.setvar(self, 'kills', preval + 1)

    def onHit(self, event):
        # Hit tracking
        client = event.client
        data = event.data
        preval = client.var(self, 'hits').value
        if not preval:
            preval = 0
        client.setvar(self, 'hits', preval + 1)
        # Headshot tracking (no helmets)
        hitloc = data[2]
        if str(hitloc) == str("1"): # 1 = Head
            preval = client.var(self, 'headshots').value
            if not preval:
                preval = 0
            client.setvar(self, 'headshots', preval + 1)

        victim = event.target
        if victim.bot:
            if self.rules.superbots == True:
                result = randint(1, 100)
                if result <= 25:
                    self.console.write("say ^9[^7Bot^9]%s^3: !buy health" % victim.exactName)
                    self.console.write("addhealth %s 100" % victim.name)
            else:
                result = randint(1, 100)
                if result <= 3:
                    self.console.write("say ^9[^7Bot^9]%s^3: !buy health" % victim.exactName)
                    self.console.write("addhealth %s 100" % victim.name)

    def onRoundstart(self, event):
        self.debug('OnRoundStart event was called')
        client = event.client
        timer_1 = Timer(10, self.randomEvent, (client, ))
        timer_1.start()
        timer_2 = Timer(130, self.randomEvent, (client, ))
        timer_2.start()
        timer_3 = Timer(250, self.randomEvent, (client, ))
        timer_3.start()
        timer_4 = Timer(370, self.randomEvent, (client, ))
        timer_4.start()
        timer_5 = Timer(490, self.randomEvent, (client, ))
        timer_5.start()
        Vampires.vamp2 = ''
        Vampires.vampmoney2 = 0
        Vampires.vamp1 = ''
        Vampires.vampmoney1 = 0
        self.console.write("mod_infiniteAmmo 0")
        self.console.write("mod_noWeaponCycle 0")
        self.console.write("mod_noWeaponRecoil 0")
        self.console.write("mod_slickSurfaces 0")
        self.console.write("mod_infiniteAirjumps 0")
        self.rules.restrict_slick = False
        self.rules.restrict_crazy = False
        self.rules.restrict_disarm = False
        self.rules.restrict_nades = False
        self.rules.restrict_overclock = False
        self.rules.restrict_airjumps = False
        self.rules.restrict_superbots = False
        self.reset_restrictions()

    def onRoundend(self, event):
        self.console.write("exec roundend.txt")
        self.gamble_times = {}

    def onClientSpawn(self, event):
        client = event.client
        if client.cid == self.attachments.isattachmentid:
            self.console.write("disarm %s" % client.name)
            self.console.write("gw %s hk69 255 255", client.name)
        if client.cid == self.attachments.hasattachmentid: # Handle suicide when having players attached
            self.console.write("disarm %s" % client.name)
        if self.rules.nades == True:
            self.console.write("gw %s he 10 2" % client.cid)
        if self.rules.respawndisarm is True:
            self.console.write("removeweapon %s deagle" % client.name)
            self.console.write("removeweapon %s beretta" % client.name)
            self.console.write("removeweapon %s magnum" % client.name)
            self.console.write("removeweapon %s glock" % client.name)
            self.console.write("removeweapon %s colt" % client.name)

        if client.bot:
            if self.rules.superbots == True:
                string1 = 'removeweapon %s deagle' % client.name
                string2 = 'removeweapon %s beretta' % client.name
                string3 = 'removeweapon %s magnum' % client.name
                string4 = 'removeweapon %s glock' % client.name
                string5 = 'removeweapon %s colt' % client.name
                string6 = 'gw %s fstod' % client.name
                string7 = 'gw %s hk69 255 255' % client.name
                self.console.write(string1)
                self.console.write(string2)
                self.console.write(string3)
                self.console.write(string4)
                self.console.write(string5)
                self.console.write(string6)
                self.console.write(string7)
#                fin = open(self.GAME_PATH + "superbots.txt", "rt")
#                data = fin.read()
#                data = data.replace('XDATA1', string1)
#                data = data.replace('XDATA2', string2)
#                data = data.replace('XDATA3', string3)
#                data = data.replace('XDATA4', string4)
#                data = data.replace('XDATA5', string5)
#                data = data.replace('XDATA6', string6)
#                data = data.replace('XDATA7', string7)
#                fin.close()
#                fin = open(self.GAME_PATH + "superbots.txt", "wt")
#                fin.write(data)
#                fin.close()
#                self.console.write('exec superbots.txt')
#                fin = open(self.GAME_PATH + "superbots.txt", "rt")
#                data = fin.read()
#                data = data.replace(string1, 'XDATA1')
#                data = data.replace(string2, 'XDATA2')
#                data = data.replace(string3, 'XDATA3')
#                data = data.replace(string4, 'XDATA4')
#                data = data.replace(string5, 'XDATA5')
#                data = data.replace(string6, 'XDATA6')
#                data = data.replace(string7, 'XDATA7')
#                fin.close()
#                fin = open(self.GAME_PATH + "superbots.txt", "wt")
#                fin.write(data)
#                fin.close()
            else:
                result = randint(1, 100)
                if result <= 7:
                    botguns = [
                        'sr8',
                        'psg1',
                        'frf1',
                        'g36',
                        'lr',
                        'm4',
                        'ak103',
                        'spas12',
                        'benelli',
                        'mp5k',
                        'ump45',
                        'p90',
                        'mac11',
                        'hk69',
                        'negev',
                        'fstod'
                    ]
                    randomgun = rand.choice(botguns)
                    self.console.write("say ^9[^7Bot^9]%s^3: !buy %s" % (client.exactName, randomgun))
                    self.console.write("gw %s %s" % (client.name, randomgun))

        elif client.team != b3.TEAM_SPEC:
            if client.isvar(self, 'inv'):
                self.console.write("inv %s" % client.cid)
                client.delvar(self, 'inv')
            if client.isvar(self, 'autobuy'):
                weapon_modname = client.var(self, 'autobuy').value
                weapon_exactname = client.var(self, 'autobuyname').value
                cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
                if cursor.EOF:
                    client.message('You don\'t have enough coins.')
                    cursor.close()
                    client.delvar(self, 'autobuy')
                    client.delvar(self, 'autobuyname')
                else:
                    try: money = int(cursor.getValue('money',))
                    except: money = 0
                    cursor.close()
                    if weapon_modname in self.weapons:
                        self.debug('Autobuy weapon is in blueweapons')
                        #if money >= self.weapons[weapon_modname]:
                        if self.spendit(client,self.weapons[weapon_modname]):
                            #cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - self.weapons[weapon_modname], client.id))
                            #cursor.close()
                            if (weapon_modname == "vest") or (weapon_modname == "nvg") or (weapon_modname == "silencer") or (weapon_modname == "laser") or (weapon_modname == "helmet"):
                                self.console.write("gi %s %s" % (client.cid, weapon_modname))
                                client.message('^5Autobuying ^6%s' % weapon_exactname)
                            #    minus_reward = self.weapons[weapon_modname]
                            #    self.update_minus_location(client, minus_reward)
                            else:
                                self.console.write("gw %s %s" % (client.cid, weapon_modname))
                                client.message('^5Autobuying ^6%s' % weapon_exactname)
                            #    minus_reward = self.weapons[weapon_modname]
                            #    self.update_minus_location(client, minus_reward)
                        else:
                            client.message('You don\'t have enough coins.')
                            client.delvar(self, 'autobuy')
                            client.delvar(self, 'autobuyname')
                    else:
                        self.debug('Wrong weapon input')

    def onGameExit(self, event):
        for client in self.console.clients.getList():
            if client.isvar(self, 'autobuy'):
                client.delvar(self, 'autobuy')
                client.delvar(self, 'autobuyname')
            if client.isvar(self, 'invisible'):
                client.delvar(self, 'invisible')

    def onWeapkill(self, client, target, data=None):
        self.checkRewards(client, target)
        self.update_client_kills(client)
        isauthedstatus = client.var(self, 'isauthed').value
        if isauthedstatus is False:
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            if data[1] in (self.console.UT_MOD_KNIFE, self.console.UT_MOD_KNIFE_THROWN):
                if cursor.EOF:
                    cursor = self.console.storage.query('INSERT INTO money (iduser, money) VALUES (%s , %s)' % (client.id, 400))
                    cursor.close()
                    reward = 400
                    self.update_location(client, reward)
                else:
                    try: money = int(cursor.getValue('money'))
                    except: money = 0
                    if money == self.MAX_WALLET_MONEY:
                        cursor.close()
                        self.update_location(client)
                    elif money + 400 >= self.MAX_WALLET_MONEY:
                        cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (self.MAX_WALLET_MONEY, client.id))
                        cursor.close()
                        self.update_location(client)
                    else:
                        cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money + 400, client.id))
                        cursor.close()
                        reward = 400
                        self.update_location(client, reward)
            elif data[1] in (self.console.UT_MOD_BERETTA, self.console.UT_MOD_MAGNUM, self.console.UT_MOD_DEAGLE, self.console.UT_MOD_GLOCK, self.console.UT_MOD_COLT1911):
                if cursor.EOF:
                    cursor = self.console.storage.query('INSERT INTO money (iduser, money) VALUES (%s , %s)' % (client.id, 600))
                    cursor.close()
                    reward = 600
                    self.update_location(client, reward)
                else:
                    try: money = int(cursor.getValue('money'))
                    except: money = 0
                    if money == self.MAX_WALLET_MONEY:
                        cursor.close()
                        self.update_location(client)
                    elif money + 600 >= self.MAX_WALLET_MONEY:
                        cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (self.MAX_WALLET_MONEY, client.id))
                        cursor.close()
                        self.update_location(client)
                    else:
                        cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money + 600, client.id))
                        cursor.close()
                        reward = 600
                        self.update_location(client, reward)
            elif cursor.EOF:
                cursor = self.console.storage.query('INSERT INTO money (iduser, money) VALUES (%s , %s)' % (client.id, 500))
                cursor.close()
                reward = 500
                self.update_location(client, reward)
            else:
                try: money = int(cursor.getValue('money'))
                except: money = 0
                if money == self.MAX_WALLET_MONEY:
                    cursor.close()
                    self.update_location(client)
                elif money + 500 >= self.MAX_WALLET_MONEY:
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (self.MAX_WALLET_MONEY, client.id))
                    cursor.close()
                    self.update_location(client)
                else:
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money + 500, client.id))
                    cursor.close()
                    reward = 500
                    self.update_location(client, reward)
            cursor.close()
            self.update_target_deaths(target)
            self.update_target_location(target)
            ###########################################################################################################################
        else:
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            if data[1] in (self.console.UT_MOD_KNIFE, self.console.UT_MOD_KNIFE_THROWN):
                if cursor.EOF:
                    cursor = self.console.storage.query('INSERT INTO money (iduser, money) VALUES (%s , %s)' % (client.id, 480))
                    cursor.close()
                    reward = 480
                    self.update_location(client, reward)
                else:
                    try: money = int(cursor.getValue('money'))
                    except: money = 0
                    if money == self.MAX_WALLET_MONEY:
                        cursor.close()
                        self.update_location(client)
                    elif money + 480 >= self.MAX_WALLET_MONEY:
                        cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (self.MAX_WALLET_MONEY, client.id))
                        cursor.close()
                        self.update_location(client)
                    else:
                        cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money + 480, client.id))
                        cursor.close()
                        reward = 480
                        self.update_location(client, reward)
            elif data[1] in (self.console.UT_MOD_BERETTA, self.console.UT_MOD_MAGNUM, self.console.UT_MOD_DEAGLE, self.console.UT_MOD_GLOCK, self.console.UT_MOD_COLT1911):
                if cursor.EOF:
                    cursor = self.console.storage.query('INSERT INTO money (iduser, money) VALUES (%s , %s)' % (client.id, 720))
                    cursor.close()
                    reward = 720
                    self.update_location(client, reward)
                else:
                    try: money = int(cursor.getValue('money'))
                    except: money = 0
                    if money == self.MAX_WALLET_MONEY:
                        cursor.close()
                        self.update_location(client)
                    elif money + 720 >= self.MAX_WALLET_MONEY:
                        cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (self.MAX_WALLET_MONEY, client.id))
                        cursor.close()
                        self.update_location(client)
                    else:
                        cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money + 720, client.id))
                        cursor.close()
                        reward = 720
                        self.update_location(client, reward)
            elif cursor.EOF:
                cursor = self.console.storage.query('INSERT INTO money (iduser, money) VALUES (%s , %s)' % (client.id, 600))
                cursor.close()
                reward = 600
                self.update_location(client, reward)
            else:
                try: money = int(cursor.getValue('money'))
                except: money = 0
                if money == self.MAX_WALLET_MONEY:
                    cursor.close()
                    self.update_location(client)
                elif money + 600 >= self.MAX_WALLET_MONEY:
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (self.MAX_WALLET_MONEY, client.id))
                    cursor.close()
                    self.update_location(client)
                else:
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money + 600, client.id))
                    cursor.close()
                    reward = 600
                    self.update_location(client, reward)
            cursor.close()
            self.update_target_deaths(target)
            self.update_target_location(target)

    def onSay(self, event):
        # Chat message tracking (excludes commands)
        client = event.client
        handler = event.data
        if handler[0] != "!":
            preval = client.var(self, 'messages').value
            if not preval:
                preval = 0
            client.setvar(self, 'messages', preval + 1)

        if client.isvar(self, 'typekeyword'):
            handler = event.data
            if handler[0].lower() in self.weapons and handler[1].lower() == 'on' or handler[1].lower() == 'off':
                self.cmd_buy(client=client, data=handler)
            elif handler[0].lower() in self.weapons:
                self.cmd_buy(client=client, data=handler[0])
            else:
                client.message('Invalid syntax! Type a valid weapon.')
                client.message('Type !typekeyword off to deactivate')

    def cmd_resetmoney(self, data, client, cmd=None):
        if data:
            handler = self._adminPlugin.parseUserCmd(data)
            sclient = self._adminPlugin.findClientPrompt(handler[0], client)
            if not sclient:
                client.message('Invalid client')
                return

            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % sclient.id)
            try: actual_money = int(cursor.getValue('money')):
            except: actual_money = -1
            if cursor.EOF or actual_money == 0:
                client.message('No need to reset this player!')
                cursor.close()
            else:
                cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (int(0), sclient.id))
                cursor.close()
                client.message('Player\'s money has been reset')
                self.update_target_location(sclient)
        else:
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            try: actual_money = int(cursor.getValue('money')):
            except: actual_money = -1
            if cursor.EOF or actual_money == 0:
                client.message('No need to reset yourself!')
                cursor.close()
            else:
                cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (int(0), client.id))
                cursor.close()
                client.message('Your money has been reset')
                self.update_target_location(sclient)

    def cmd_typekeyword(self, data, client, cmd=None):
        if data:
            handler = self._adminPlugin.parseUserCmd(data)
            if handler[0].lower() == 'on':
                client.setvar(self, 'typekeyword', True)
            elif handler[0].lower() == 'off':
                client.delvar(self, 'typekeyword')
        else:
            client.message('Please specify ^1on ^7or ^1off')

    ####################################################################################################################
    #                                                                                                                  #
    #    Getting sql data                                                                                              #
    #                                                                                                                  #
    ####################################################################################################################
   
    def get_client_kills(self, client):
        cursor = self.console.storage.query('SELECT * FROM kills WHERE iduser = %s' % client.id)
        if cursor.EOF:
            cursor = self.console.storage.query('INSERT INTO kills (iduser, kills) VALUES (%s , %s)' % (client.id, 0))
            cursor = self.console.storage.query('INSERT INTO kills (iduser, deaths) VALUES (%s , %s)' % (client.id, 0))
            kills = 0
            cursor.close()
        else:
            try: kills = int(cursor.getValue('kills'))
            except: kills = 0
            cursor.close()
            return kills
        return kills

    def get_client_scoins(self, client):
        cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
        if cursor.EOF:
            scoins = 0
            cursor.close()
        else:
            try: scoins = int(cursor.getValue('scoins'))
            except: scoins = 0
            cursor.close()
            return scoins
        return scoins

    def get_client_deaths(self, client):
        cursor = self.console.storage.query('SELECT * FROM kills WHERE iduser = %s' % client.id)
        if cursor.EOF:
            cursor = self.console.storage.query('INSERT INTO kills (iduser, kills) VALUES (%s , %s)' % (client.id, 0))
            cursor = self.console.storage.query('INSERT INTO kills (iduser, deaths) VALUES (%s , %s)' % (client.id, 0))
            deaths = 0
            cursor.close()
        else:
            try: deaths = int(cursor.getValue('deaths'))
            except: deaths = 0
            cursor.close()
            return deaths
        return deaths

    def get_target_kills(self, target):
        cursor = self.console.storage.query('SELECT * FROM kills WHERE iduser = %s' % target.id)
        if cursor.EOF:
            cursor = self.console.storage.query('INSERT INTO kills (iduser, kills) VALUES (%s , %s)' % (target.id, 0))
            cursor = self.console.storage.query('INSERT INTO kills (iduser, deaths) VALUES (%s , %s)' % (target.id, 0))
            kills = 0
            cursor.close()
        else:
            try: kills = int(cursor.getValue('kills'))
            except: kills = 0
            cursor.close()
            return kills
        return kills

    def get_target_deaths(self, target):
        cursor = self.console.storage.query('SELECT * FROM kills WHERE iduser = %s' % target.id)
        if cursor.EOF:
            cursor = self.console.storage.query('INSERT INTO kills (iduser, kills) VALUES (%s , %s)' % (target.id, 0))
            cursor = self.console.storage.query('INSERT INTO kills (iduser, deaths) VALUES (%s , %s)' % (target.id, 0))
            deaths = 0
            cursor.close()
        else:
            try: deaths = int(cursor.getValue('deaths'))
            except: deaths = 0
            cursor.close()
            return deaths
        return deaths 

    def get_client_money(self, client):
        cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
        try: value = int(cursor.getValue('money'))
        except: value = 0
        value2 = self.add_spaces(str(value))
        cursor.close()
        return value2

    ####################################################################################################################
    #                                                                                                                  #
    #    Updating the location string                                                                                  #
    #                                                                                                                  #
    ####################################################################################################################

    def check_announcement(self, client):
        counter = client.var(self, 'maxmoney').value
        if (counter == 20) or (counter == 40) or (counter == 60) or (counter == 80) or (counter == 100):
            client.message('^3You have reached the ^2Maximum money ^5obtainable. ^3You can buy a supercoin with ^6!prestige')
            client.message('^3Keep in mind you will loose all of your money if you do so!')
            client.setvar(self, 'maxmoney', counter + 1)
        else:
            client.setvar(self, 'maxmoney', counter + 1)

    def update_location(self, client, reward=None, isgamble=None):
        value2 = self.get_client_money(client)
        kills = self.get_client_kills(client)
        deaths = self.get_client_deaths(client)
        scoins = self.get_client_scoins(client)
        client.setvar(self, 'maxmoney', 1)
        self.check_announcement(client)
        if reward is not None:
            # money earned tracking
            if not isgamble:
                preval = client.var(self, 'money_earned').value
                if not preval:
                    preval = 0
                client.setvar(self, 'money_earned', preval + reward)

            self.console.write('location %s "%s ^6|| ^8[^1%s^8] ^3Money: ^2%s coins ^7|| ^2K^3/^1D^3: ^2%s^3/^1%s ^7|| ^2+%s Coins" 0 1' % (client.name, client.exactName, scoins, value2, kills, deaths, reward))
            t = Timer(2, self.update_location, (client, ))
            t.start()
        else:
            self.console.write('location %s "%s ^6|| ^8[^1%s^8] ^3Money: ^2%s coins ^7|| ^2K^3/^1D^3: ^2%s^3/^1%s ^7||" 0 1' % (client.name, client.exactName, scoins, value2, kills, deaths))


    def update_minus_location(self, client, minus_reward=None):
        value2 = self.get_client_money(client)
        kills = self.get_client_kills(client)
        deaths = self.get_client_deaths(client)
        scoins = self.get_client_scoins(client)
        self.console.write('location %s " %s ^6|| ^8[^1%s^8] ^3Money: ^2%s coins ^7|| ^2K^3/^1D^3: ^2%s^3/^1%s ^7|| ^1-%s coins" 0 1' % (client.name, client.exactName, scoins, value2, kills, deaths, minus_reward))
        t = Timer(2, self.update_location, (client, ))
        t.start()

    def update_target_location(self, target):
        cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % target.id)
        try: value = int(cursor.getValue('money'))
        except: value = 0
        value2 = self.add_spaces(str(value))
        scoins = self.getsupercoins(target)
        cursor.close()
        kills = self.get_target_kills(target)
        deaths = self.get_target_deaths(target)
        self.console.write('location %s "%s ^6|| ^8[^1%s^8] ^3Money: ^2%s coins ^7|| ^2K^3/^1D^3: ^2%s^3/^1%s" 0 1' % (target.name, target.exactName, scoins, value2, kills, deaths))

    ####################################################################################################################
    #                                                                                                                  #
    #    Other functions                                                                                               #
    #                                                                                                                  #
    ####################################################################################################################

    def update_client_kills(self, client):
        cursor = self.console.storage.query('SELECT * FROM kills WHERE iduser = %s' % client.id)
        if cursor.EOF:
            cursor = self.console.storage.query('INSERT INTO kills (iduser, kills) VALUES (%s , %s)' % (client.id, 0))
            cursor = self.console.storage.query('INSERT INTO kills (iduser, deaths) VALUES (%s , %s)' % (client.id, 0))
            cursor.close()
        else:
            try: kills = int(cursor.getValue('kills'))
            except: kills = 0
            cursor = self.console.storage.query('UPDATE kills SET kills = %s WHERE iduser = %s' % (kills + 1, client.id))
            cursor.close()

    def update_target_deaths(self, target):
        cursor = self.console.storage.query('SELECT * FROM kills WHERE iduser = %s' % target.id)
        if cursor.EOF:
            cursor = self.console.storage.query('INSERT INTO kills (iduser, kills) VALUES (%s , %s)' % (target.id, 0))
            cursor = self.console.storage.query('INSERT INTO kills (iduser, deaths) VALUES (%s , %s)' % (target.id, 0))
            cursor.close()
        else:
            try: deaths = int(cursor.getValue('deaths'))
            except: deaths = 0
            cursor = self.console.storage.query('UPDATE kills SET deaths = %s WHERE iduser = %s' % (deaths + 1, target.id))
            cursor.close()

    def checkRewards(self, client, target):
        target_name = self.bounty.tname
        vampire_1 = self.vampires.vamp1
        vampire_2 = self.vampires.vamp2
        kill_reward = self.bounty.reward
        if target.name == target_name:
            Bounty.tname = ''
            Bounty.reward = 0
            Bounty.tdeaths = 1
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            try: money = int(cursor.getValue('money'))
            except: money = 0
            cursor.close()
            cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money + kill_reward, client.id))
            cursor.close()
            self.console.say('%s ^1KILLED ^6%s ^3 and collected a ^2Bounty ^3of ^2%s coins!' % (client.exactName, target.exactName, kill_reward))
            self.update_location(client)
        elif target.name == vampire_1 or target.name == vampire_2:
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            try: money = int(cursor.getValue('money'))
            except: money = 0
            cursor.close()
            cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money + 1500, client.id))
            cursor.close()
            client.message('^3Killed a ^1VAMPIRE^3: ^2+1500 coins')
            self.update_location(client)
        elif client.name == vampire_1:
            string1 = 'addhealth %s %s' % (client.cid, 50)
            string2 = 'tell %s "^1VAMPIRE-MODE: ^7[^2+50 ^7Health^7]' % client.cid
            fin = open(self.GAME_PATH+"rewardvampire2.txt", "rt")
            data = fin.read()
            data = data.replace('XDATA1', string1)
            data = data.replace('XDATA2', string2)
            fin.close()
            fin = open(self.GAME_PATH+"rewardvampire2.txt", "wt")
            fin.write(data)
            fin.close()
            self.console.write('exec rewardvampire2.txt')
            fin = open(self.GAME_PATH+"rewardvampire2.txt", "rt")
            data = fin.read()
            data = data.replace(string1, 'XDATA1')
            data = data.replace(string2, 'XDATA2')
            fin.close()
            fin = open(self.GAME_PATH+"rewardvampire2.txt", "wt")
            fin.write(data)
            fin.close()
        elif client.name == vampire_2:
            string1 = 'addhealth %s %s' % (client.cid, 50)
            string2 = 'tell %s "^1VAMPIRE-MODE: ^7[^2+50 ^7Health^7]' % client.cid
            fin = open(self.GAME_PATH+"rewardvampire2.txt", "rt")
            data = fin.read()
            data = data.replace('XDATA1', string1)
            data = data.replace('XDATA2', string2)
            fin.close()
            fin = open(self.GAME_PATH+"rewardvampire2.txt", "wt")
            fin.write(data)
            fin.close()
            self.console.write('exec rewardvampire2.txt')
            fin = open(self.GAME_PATH+"rewardvampire2.txt", "rt")
            data = fin.read()
            data = data.replace(string1, 'XDATA1')
            data = data.replace(string2, 'XDATA2')
            fin.close()
            fin = open(self.GAME_PATH+"rewardvampire2.txt", "wt")
            fin.write(data)
            fin.close()
        else:
            return

    def checkDeaths(self, client, sclient):
        target_deaths = self.bounty.tdeaths
        if target_deaths == 0:
            kill_reward = self.bounty.reward*2
            Bounty.tname = ''
            Bounty.reward = 0
            Bounty.tdeaths = 0
            self.console.say('%s ^2SURVIVED ^3 for 1 minute and took ^6%s coins ^3as a reward!' % (sclient.exactName, kill_reward))
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % sclient.id)
            try: money = int(cursor.getValue('money'))
            except: money = 0
            cursor.close()
            cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money + kill_reward, sclient.id))
            cursor.close()

    def randomEvent(self, client):
        Bounty.tname = ''
        Bounty.reward = 0
        Bounty.tdeaths = 0
        random_player = randint(0, 18)
        sclient = self._adminPlugin.findClientPrompt(str(random_player), client)
        if not sclient:
            self.randomEvent(client)
        player = self.grab_player(sclient)
        if player.team == 'FREE':
            bounty = randint(7500, 12000)
            self.console.write('bigtext "^3A ^2BOUNTY ^3of ^6%s coins ^3has been set on %s"' % (bounty, sclient.exactName))
            Bounty.tname = '%s' % sclient.name
            Bounty.reward = bounty
            t = Timer(60, self.checkDeaths, (client, sclient, ))
            t.start()
            self.console.write('gi %s redflag' % sclient.exactName)
        else:
            self.randomEvent(client)

    ####################################################################################################################
    #                                                                                                                  #
    #    Remove modes and other returns/functions                                                                      #
    #                                                                                                                  #
    ####################################################################################################################
 
    def getGambleStats(self):
        cursor = self.console.storage.query('SELECT * FROM gamblestats')
        try: wins = int(cursor.getValue('wins'))
        except: wins = 0
        try: losses = int(cursor.getValue('losses'))
        except: losses = 0
        try: totals = int(cursor.getValue('totals'))
        except: totals = 0
        cursor.close()
        return(wins, losses, totals)

    def update_gamble_stats(self, outcome):
        db_currents = self.getGambleStats()
        currwins = db_currents[0]
        currlosses = db_currents[1]
        totals = db_currents[2]

        self.console.storage.query('UPDATE gamblestats SET totals = %s' % (totals + 1))

        if (outcome == 1):
            self.console.storage.query('UPDATE gamblestats SET wins = %s' % (currwins + 1))

        if (outcome == 2):
            self.console.storage.query('UPDATE gamblestats SET losses = %s' % (currlosses + 1))

    def remove_lowgrav_mode(self, client):
        self.console.write('bigtext "^5Low-Gravity ^3mode ^7[^1OFF^7]')
        self.console.write("g_gravity 800")

    def remove_freeze_mode(self, tounfreeze):
        plyr = tounfreeze
        self.console.write('freeze %s' % plyr)
        self.console.write('tell %s "^3You are no longer frozen!"' % plyr)

    def remove_inv_mode(self, client):
        self.console.write('bigtext "%s is ^2visible ^7again!"' % client.exactName)
        self.console.write("invisible %s" % client.cid)

    def add_spaces(self, value):
        leader = value[0:len(value) % 3].strip()
        return  leader + "." * bool(leader) + ".".join(group[::-1] for group in re.findall("...", value[::-1])[::-1])

    def getModName(self, weapon):
        if (weapon == "sr8") or (weapon == "SR8") or (weapon == "sr"):
            modname='sr8'
        elif (weapon == "ak") or (weapon == "AK") or (weapon == "AK103") or (weapon == "ak103"):
            modname='ak103'
        elif (weapon == "NEGEV") or (weapon == "negev") or (weapon == "NE") or (weapon == "ne"):
            modname='negev'
        elif (weapon == "ump") or (weapon == "UMP") or (weapon == "UMP45") or (weapon == "ump45"):
            modname='ump45'
        elif (weapon == "g36") or (weapon == "G36"):
            modname='g36'
        elif (weapon == "HK69") or (weapon == "hk69") or (weapon == "hk") or (weapon == "HK"):
            modname='hk69'
        elif (weapon == "lr300") or (weapon == "LR300") or (weapon == "LR") or (weapon == "lr"):
            modname='lr'
        elif (weapon == "spas") or (weapon == "SPAS") or (weapon == "Spas") or (weapon == "spas12") or (weapon == "Spas12") or (weapon == "FRANCHI") or (weapon == "franchi"):
            modname='spas12'
        elif (weapon == "M4") or (weapon == "m4") or (weapon == "m4a") or (weapon == "M4A"):
            modname='m4'
        elif (weapon == "PSG") or (weapon == "psg") or (weapon == "PSG1") or (weapon == "psg1"):
            modname='psg1'
        elif (weapon == "mp5") or (weapon == "MP5") or (weapon == "MP5K") or (weapon == "mp5k"):
            modname='mp5k'
        elif (weapon == "mac") or (weapon == "mac11") or (weapon == "mac-11"):
            modname='mac11'
        elif (weapon == "frf1") or (weapon == "FRF1") or (weapon == "frf") or (weapon == "FRF"):
            modname='frf1'
        elif (weapon == "benell") or (weapon == "benelli") or (weapon == "BENELLI") or (weapon == "beneli"):
            modname='benelli'
        elif (weapon == "P90") or (weapon == "p90") or (weapon == "p9"):
            modname='p90'
        elif (weapon == "gib") or (weapon == "1shot") or (weapon == "fstod") or (weapon == "tod") or (weapon == "tod50") or (weapon == "tod-50"):   
            modname='fstod'
        elif (weapon == "silencer") or (weapon == "supressor") or (weapon == "sil"):
            modname='silencer'
        elif (weapon == "laser") or (weapon == "LASER") or (weapon == "lase"):
            modname='laser'
        elif (weapon == "vest") or (weapon == "kev") or (weapon == "armor"):
            modname='vest'
        elif (weapon == "helmet") or (weapon == "helm") or (weapon == "head"):
            modname='helmet'
        elif (weapon == "NVG") or (weapon == "nvg") or (weapon == "nightvision"):
            modname='nvg'
        return modname

    def getExactName(self, weapon):
        if (weapon == "sr8") or (weapon == "SR8") or (weapon == "sr"):
            weaponexactname='^6Sr8'
        elif (weapon == "ak") or (weapon == "AK") or (weapon == "AK103") or (weapon == "ak103"):
            weaponexactname='^6AK103'
        elif (weapon == "NEGEV") or (weapon == "negev") or (weapon == "NE") or (weapon == "ne"):
            weaponexactname='^4NEGEV'
        elif (weapon == "ump") or (weapon == "UMP") or (weapon == "UMP45") or (weapon == "ump45"):
            weaponexactname='^3UMP45'
        elif (weapon == "g36") or (weapon == "G36"):
            weaponexactname='^6G36'
        elif (weapon == "HK69") or (weapon == "hk69") or (weapon == "hk") or (weapon == "HK"):
            weaponexactname='^1HK69'
        elif (weapon == "lr300") or (weapon == "LR300") or (weapon == "LR") or (weapon == "lr"):
            weaponexactname='^6LR300'
        elif (weapon == "spas") or (weapon == "SPAS") or (weapon == "Spas") or (weapon == "spas12") or (weapon == "Spas12") or (weapon == "FRANCHI") or (weapon == "franchi"):
            weaponexactname='^3Spas'
        elif (weapon == "M4") or (weapon == "m4") or (weapon == "m4a") or (weapon == "M4A"):
            weaponexactname='^6M4A1'
        elif (weapon == "PSG") or (weapon == "psg") or (weapon == "PSG1") or (weapon == "psg1"):
            weaponexactname='^6PSG1'
        elif (weapon == "mp5") or (weapon == "MP5") or (weapon == "MP5K") or (weapon == "mp5k"):
            weaponexactname='^3MP5K'
        elif (weapon == "mac") or (weapon == "mac11") or (weapon == "mac-11"):
            weaponexactname='^3MAC-11'
        elif (weapon == "frf1") or (weapon == "FRF1") or (weapon == "frf") or (weapon == "FRF"):
            weaponexactname='^3FR-F1'
        elif (weapon == "benell") or (weapon == "benelli") or (weapon == "BENELLI") or (weapon == "beneli"):
            weaponexactname='^3Benelli'
        elif (weapon == "P90") or (weapon == "p90") or (weapon == "p9"):
            weaponexactname='^3P90'
        elif (weapon == "gib") or (weapon == "1shot") or (weapon == "fstod") or (weapon == "tod") or (weapon == "tod50") or (weapon == "tod-50"):   
            weaponexactname='^5Tod-50'
        elif (weapon == "silencer") or (weapon == "supressor") or (weapon == "sil"):
            weaponexactname='Silencer'
        elif (weapon == "laser") or (weapon == "LASER") or (weapon == "lase"):
            weaponexactname='Laser Sight'
        elif (weapon == "vest") or (weapon == "kev") or (weapon == "armor"):
            weaponexactname='Vest'
        elif (weapon == "helmet") or (weapon == "helm") or (weapon == "head"):
            weaponexactname='Helmet'
        elif (weapon == "NVG") or (weapon == "nvg") or (weapon == "nightvision"):
            weaponexactname='NVG'
        return weaponexactname

    ####################################################################################################################
    #                                                                                                                  #
    #    Vampire mode                                                                                                  #
    #                                                                                                                  #
    ####################################################################################################################

    def cmd_vampire(self, data, client, cmd=None):
        if not data:
            client.message('^3You must enter ^2!vampire <amount> (10.000 coins = 1 minute)')
            return
        handler = self._adminPlugin.parseUserCmd(data)
        vampool = int(handler[0])
        minus_reward = vampool
        cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
        try: money = int(cursor.getValue('money'))
        except: money = 0
        player = self.grab_player2(client)
        if cursor.EOF:
            client.message('^1You do not have enough coins!')
            cursor.close()
            return
        elif vampool <= 9999:
            client.message('^3Your ^1Blood-pool ^3must have at least 10.000 coins!')
            cursor.close()
            return
        elif vampool >= 100001:
            client.message('^3Your ^1Blood-pool ^3cannot hold more than 100.000 coins!')
            cursor.close()
            return
        elif player.team == 'SPECTATOR':
            client.message('^3You cannot become a ^1VAMPIRE ^3 as a spectator')
            cursor.close()
            return
        elif Vampires.vamp1 == client.name or Vampires.vamp2 == client.name:
            client.message('^3You are a ^1VAMPIRE ^3already')
            cursor.close()
            return
        elif money >= vampool:
            cursor.close()
            if Vampires.vamp1 == '':
                self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - vampool, client.id))
                Vampires.vampmoney1 = vampool
                Vampires.vamp1 = client.name
                self.vampstuff2(client)
                self.vampstuff0(client)
                self.console.write('bigtext "%s ^3is now a ^1VAMPIRE!"' % client.exactName)
                self.update_minus_location(client, minus_reward)
            else:
                self.debug('vamp1 taken - trying vamp2')
                if Vampires.vamp2 == '':
                    self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - vampool, client.id))
                    Vampires.vampmoney2 = vampool
                    Vampires.vamp2 = client.name
                    self.vampstuff1(client)
                    self.vampstuff3(client)
                    self.console.write('bigtext "%s ^3is now a ^1VAMPIRE!"' % client.exactName)
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('^3There are ^12^7/^12 ^3vampire slots taken - Please try again later.')
        else:
            cursor.close()
            client.message('^3You do not have enough ^2coins')

    def vampstuff0(self, client):
        if Vampires.vampmoney1 >= 10000:
            vampool = Vampires.vampmoney1
            newpool = vampool - 10000
            Vampires.vampmoney1 = newpool
            vamptimer_3 = Timer(60, self.vampstuff0, (client, ))
            vamptimer_3.start()
        else:
            Vampires.vamp1 = ''
            Vampires.vampmoney1 = 0
            self.console.write('bigtext "%s ^3 is no longer a ^1VAMPIRE"' % client.name)

    def vampstuff1(self, client):
        if Vampires.vampmoney2 >= 10000:
            vampool = Vampires.vampmoney2
            newpool = vampool - 10000
            Vampires.vampmoney2 = newpool
            vamptimer_4 = Timer(60, self.vampstuff0, (client, ))
            vamptimer_4.start()
        else:
            Vampires.vamp2 = ''
            Vampires.vampmoney2 = 0
            self.console.write('bigtext "%s ^3 is no longer a ^1VAMPIRE"' % client.name)

    def vampstuff2(self, client):
        if Vampires.vamp1 == client.name:
            string1 = 'addhealth %s %s' % (client.cid, -20)
            string2 = 'tell %s "^1VAMPIRE-MODE: ^7[^1-20 ^7Health^7]"' % client.cid
            fin = open(self.GAME_PATH + "rewardvampire.txt", "rt")
            data = fin.read()
            data = data.replace('XDATA1', string1)
            data = data.replace('XDATA2', string2)
            fin.close()
            fin = open(self.GAME_PATH + "rewardvampire.txt", "wt")
            fin.write(data)
            fin.close()
            self.console.write('exec rewardvampire.txt')
            fin = open(self.GAME_PATH + "rewardvampire.txt", "rt")
            data = fin.read()
            data = data.replace(string1, 'XDATA1')
            data = data.replace(string2, 'XDATA2')
            fin.close()
            fin = open(self.GAME_PATH + "rewardvampire.txt", "wt")
            fin.write(data)
            fin.close()
            vamptimer_1 = Timer(10, self.vampstuff2, (client, ))
            vamptimer_1.start()
        else:
            self.debug('Stopping loop')

    def vampstuff3(self, client):
        if Vampires.vamp2 == client.name:
            string1 = 'addhealth %s %s' % (client.cid, -20)
            string2 = 'tell %s "^1VAMPIRE-MODE: ^7[^1-20 ^7Health^7]"' % client.cid
            fin = open(self.GAME_PATH + "rewardvampire.txt", "rt")
            data = fin.read()
            data = data.replace('XDATA1', string1)
            data = data.replace('XDATA2', string2)
            fin.close()
            fin = open(self.GAME_PATH + "rewardvampire.txt", "wt")
            fin.write(data)
            fin.close()
            self.console.write('exec rewardvampire.txt')
            fin = open(self.GAME_PATH + "rewardvampire.txt", "rt")
            data = fin.read()
            data = data.replace(string1, 'XDATA1')
            data = data.replace(string2, 'XDATA2')
            fin.close()
            fin = open(self.GAME_PATH + "rewardvampire.txt", "wt")
            fin.write(data)
            fin.close()
            vamptimer_2 = Timer(10, self.vampstuff2, (client, ))
            vamptimer_2.start()
        else:
            self.debug('Stopping loop')

    ####################################################################################################################
    #                                                                                                                  #
    #    User commands                                                                                                 #
    #                                                                                                                  #
    ####################################################################################################################

    def cmd_money(self, data, client, cmd=None):
        if not data or data == '':
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            if cursor.EOF:
                client.message('^3You have ^1no coins.')
                cursor.close()
            else:
                value2 = self.get_client_money(client)
                scoins = self.getsupercoins(client)
                client.message('^3You have: ^2%s coins ^3and ^8%s Super-Coins' % (value2, scoins))
                cursor.close()
        else:
            handler = self._adminPlugin.parseUserCmd(data)
            sclient = self._adminPlugin.findClientPrompt(handler[0], client)
            if not sclient:
                return
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % sclient.id)
            if cursor.EOF:
                message = '%s ^3has ^1no coins.' % sclient.exactName
                cmd.sayLoudOrPM(client, message)
                cursor.close()
            else:
                scoins = self.getsupercoins(sclient)
                try: value = int(cursor.getValue('money'))
                except: value = 0
                value2 = self.add_spaces(str(value))
                messagr = '%s ^3has: ^2%s coins ^3and ^8%s Super-Coins' % (sclient.exactName, value2, scoins)
                cmd.sayLoudOrPM(client, messagr)
                cursor.close()

    def cmd_price(self, data, client, cmd=None):
        """
        !price/!pr <weapon/item name>
        """
        price_dict = {
            'sr8': 8000,
            'sr': 8000,
            'psg1': 4450,
            'psg': 4450,
            'frf1': 4450,
            'g36': 6000,
            'lr': 5500,
            'm4': 2550,
            'ak103': 7000,
            'ak': 7000,
            'spas12': 12000,
            'benelli': 10000,
            'mp5k': 3250,
            'ump45': 3250,
            'ump': 3250,
            'p90': 3250,
            'mac11': 3250,
            'hk69': 5000,
            'hk': 5000,
            'negev': 4000,
            'vest': 1000,
            'helmet': 800,
            'nvg': 3000,
            'health': 15000,
            'silencer': 500,
            'laser': 500,
            'invisible': 750000,
            'inv': 150000,
            'laugh': 25000,
            'ammo': 65000,
            'maptp': 50000,
            'slapall': 1000000,
            'disarm': 500000,
            'fstod': 30000
            }

        if data not in price_dict:
            client.message('Invalid weapon! Weapons are: %s' % ', '.join(price_dict.keys()))
        else:
            cmd.sayLoudOrPM(client, '^3Price for ^5%s is: ^2%s' % (data, price_dict[data]))

    def cmd_gamble(self, data, client, cmd=None):
        last = client.var(self, 'delay_gamble', 0).value
        if (self.console.time() - last) < 120:
            # Allow gambles only every 2 minutes
            time1 = (self.console.time() - last)
            time2 = 120 - time1
            client.message('^3You use this ^5Command ^3again in ^6%s seconds' % time2)
        
        elif (client.cid in self.gamble_times) and (int(time.time())-self.gamble_times[client.cid] < 120):
            # Check if a client had reconnected recently
            client.message('^1Nice try.')

        else:
            # Checks are ok, now handle the gambling
            maxmo = self.MAX_WALLET_MONEY
            # The amount the client wants to gamble
            handler = self._adminPlugin.parseUserCmd(data)
            gam = int(handler[0])
            minus_reward = gam
            # Check if the client has enough money to do the gamble and if he gambled the minimum amount
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            if cursor.EOF:
                client.message('^1You do not have enough coins!')
                cursor.close()
                return
        
            elif gam < 50000:
                client.message('^3You need to gamble at least 50.000 coins!')
                cursor.close()
                return
            else:
                try: money = int(cursor.getValue('money'))
                except: money = 0
                cursor.close()
                if money == self.MAX_WALLET_MONEY:
                    # Don't gamble if the clients money is max
                    client.message('^3You cannot gamble with ^1MAX money')
                    return

                elif (money + gam) > self.MAX_WALLET_MONEY:
                    # Don't let a gamble exceed to limit of 20m
                    client.message('^3You cannot gamble ^1over your limit')
                    client.message('^3You can gamble a maximum of ^5%s ^2coins' % ((self.MAX_WALLET_MONEY - money)/2))
                    return

                if money >= gam:
                    # Set the last gambling times
                    client.setvar(self, 'delay_gamble', self.console.time())
                    self.gamble_times.update({client.cid: int(time.time())})
                    # Remove the deposit
                    self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - gam, client.id))
                    result = randint(1, 100)
                    # Even numbers win
                    # Odds loose
                    if (result % 2) == 0:
                        # Evens
                        # Show the visuals for a win
                        gtype = 1
                        self.update_gamble_stats(gtype)
                        self.console.write('exec win0.txt')
                        # Wait for it to finish
                        time.sleep(2)

                        # Display the win message
                        self.console.say('^5Even ^3numbers ^2WIN ^6(^3Seed: ^5%s^6)' % result)

                        reward = gam*2
                        value2 = self.add_spaces(str(reward))

                        if (money + reward) >= self.MAX_WALLET_MONEY:
                            # Client reached the max money
                            cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (maxmo, client.id))
                            cursor.close()

                            self.console.say('^5%s ^3won ^2%s coins ^3and reached the ^6maximum money.' % (client.exactName, value2))
                            self.update_location(client, None, True)

                        else:
                            # Add the money to the current money
                            cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money + reward, client.id))
                            cursor.close()
                
                            self.console.say('^3Congratulations to %s for winning a total of ^2%s coins!!' % (client.exactName, value2))
                            self.update_location(client, reward, True)
    
                    else:
                        gtype = 2
                        # Show the visuals for a loss
                        self.update_gamble_stats(gtype)
                        self.console.write('exec win1.txt')

                        # Wait for it to finish
                        time.sleep(2)
                        # Display the loose message
                        self.console.say('^3The winning number is: ^21 ^6(^3Seed: ^5%s^6)' % result)
                        value2 = self.add_spaces(str(gam))
                        self.console.say('%s lost the gamble as well as ^1%s coins.' % (client.exactName, value2))
                        self.update_minus_location(client, minus_reward)
                else:
                    client.message('You dont have enough coins to do this gamble!')

    def cmd_buyparticles(self, data, client, cmd=None):
        cursor = self.console.storage.query('SELECT * FROM particles WHERE iduser = %s' % client.id)
        isauthedstatus = client.var(self, 'isauthed').value
        if isauthedstatus is False:
            client.message('^3You need to be ^2authed ^3 in order to buy ^6particles')
            client.message('^3To auth yourself type ^2!authme')
            return
        elif not cursor.EOF:
            r = cursor.getRow()
            status = r['status']
            if status == "on":
                newstatus = "off"
                self.console.write('particlefx %s' % client.name)
                client.message('^5Particles ^3have been turned ^1OFF')
                self.console.storage.query('UPDATE particles SET status = "%s" WHERE iduser = %s' % (newstatus, client.id))
                return
            else:
                newstatus = "off"
                self.console.write('particlefx %s' % client.name)
                client.message('^5Particles ^3have been turned ^2ON')
                self.console.storage.query('UPDATE particles SET status = "%s" WHERE iduser = %s' % (newstatus, client.id))
                return
        else:
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            if cursor.EOF:
                client.message('^1You do not have enough coins!')
                cursor.close()
                return
            else:
                try: money = int(cursor.getValue('money'))
                except: money = 0
                cursor.close()
                if money >= 10000000:
                    cursor = self.console.storage.query('SELECT * FROM particles WHERE iduser = %s' % client.id)
                    if cursor.EOF:
                        cursor.close()
                        cursor = self.console.storage.query('INSERT INTO particles (iduser) VALUES (%s)' % (client.id))
                        cursor.close()
                        self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 10000000, client.id))
                        minus_reward = 10000000
                        self.update_minus_location(client, minus_reward)
                        client.message('^5Particles ^3have been activated, you may now toggle them with !particles')
                        self.console.write('particlefx %s' % client.name)

    def cmd_buycolour(self, data, client, cmd=None):
        isauthedstatus = client.var(self, 'isauthed').value
        if isauthedstatus is False:
            client.message('^3You need to be ^2authed ^3 in order to buy a ^6chatcolour')
            client.message('^3To auth yourself type ^2!authme')
            return
        if not data:
            client.message('^3Type ^2!buycolour <1-9>')
            return
        else:
            handler = self._adminPlugin.parseUserCmd(data)
            wantscolour = int(handler[0])
            if (wantscolour == 7) or (wantscolour == 0):
                client.message('^3You cannot buy ^0BLACK ^3or ^7WHITE')
            else:
                cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
                if cursor.EOF:
                    client.message('^1You do not have enough coins!')
                    cursor.close()
                    return
                else:
                    try: money = int(cursor.getValue('money'))
                    except: money = 0
                    cursor.close()
                    if money >= 10000000:
                        cursor = self.console.storage.query('SELECT * FROM chatcolour WHERE iduser = %s' % client.id)
                        if cursor.EOF:
                            cursor.close()
                            cursor = self.console.storage.query('INSERT INTO chatcolour (iduser, colour) VALUES (%s , %s)' % (client.id, wantscolour))
                            cursor.close()
                            self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 10000000, client.id))
                            minus_reward = 10000000
                            self.update_minus_location(client, minus_reward)
                            client.message('^3You have ^2bought ^3the ^5chatcolour: ^%s%s' % (wantscolour, wantscolour))
                            client.message('^3You may now set it with ^6!setcolour')
                        else:
                            cursor.close()
                            cursor = self.console.storage.query('SELECT colour FROM `chatcolour` WHERE iduser = %s' % client.id)
                            colours = []
                            try:
                                colourvalue = cursor.getValue('colour')
                                if colourvalue is None:
                                    self.debug('Dont insert nontype')
                                else:
                                    colours.insert(1, colourvalue)
                            except:
                                self.debug("No colour available")
                            try:
                                cursor.moveNext()
                            except:
                                self.debug("No colour available")
                            else:
                                colourvalue = cursor.getValue('colour')
                                if colourvalue is None:
                                    self.debug('Dont insert nontype')
                                else:
                                    colours.insert(2, colourvalue)
                            try:
                                cursor.moveNext()
                            except:
                                self.debug("No colour available")
                            else:
                                colourvalue = cursor.getValue('colour')
                                if colourvalue is None:
                                    self.debug('Dont insert nontype')
                                else:
                                    colours.insert(3, colourvalue)
                            try:
                                cursor.moveNext()
                            except:
                                self.debug("No colour available")
                            else:
                                colourvalue = cursor.getValue('colour')
                                if colourvalue is None:
                                    self.debug('Dont insert nontype')
                                else:
                                    colours.insert(4, colourvalue)
                            try:
                                cursor.moveNext()
                            except:
                                self.debug("No colour available")
                            else:
                                colourvalue = cursor.getValue('colour')
                                if colourvalue is None:
                                    self.debug('Dont insert nontype')
                                else:
                                    colours.insert(5, colourvalue)
                            try:
                                cursor.moveNext()
                            except:
                                self.debug("No colour available")
                            else:
                                colourvalue = cursor.getValue('colour')
                                if colourvalue is None:
                                    self.debug('Dont insert nontype')
                                else:
                                    colours.insert(6, colourvalue)
                            try:
                                cursor.moveNext()
                            except:
                                self.debug("No colour available")
                            else:
                                colourvalue = cursor.getValue('colour')
                                if colourvalue is None:
                                    self.debug('Dont insert nontype')
                                else:
                                    colours.insert(7, colourvalue)
                            try:
                                cursor.moveNext()
                            except:
                                self.debug("No colour available")
                            else:
                                colourvalue = cursor.getValue('colour')
                                if colourvalue is None:
                                    self.debug('Dont insert nontype')
                                else:
                                    colours.insert(8, colourvalue)
                            try:
                                cursor.moveNext()
                            except:
                                self.debug("No colour available")
                            if wantscolour in colours:
                                client.message('You already have this colour, available colours are: %s' % colours)
                            else:
                                self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 10000000, client.id))
                                self.console.storage.query('INSERT INTO chatcolour (iduser, colour) VALUES (%s , %s)' % (client.id, wantscolour))
                                client.message('^3You have ^2bought ^3the ^5chatcolour: ^%s%s' % (wantscolour, wantscolour))
                                client.message('^3You may now set it with ^6!setcolour')
                                minus_reward = 10000000
                                self.update_minus_location(client, minus_reward)

    def cmd_pay(self, data, client, cmd=None):
        """
        !pay <player> <amount>
        """
        if not data or len(data.split()) != 2:
            client.message('^3You must enter ^2!pay <player> <amount>')
            return

        handler = data.split()
        sclient = self._adminPlugin.findClientPrompt(handler[0])
        if not sclient:
            return

        r = re.compile(r'''^\d+$''')
        m = r.match(handler[1])
        if not m:
            client.message('^1Invalid money value entered: please use only numbers')
            return

        value = int(handler[1])
        minus_reward = value

        cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
        if cursor.EOF:
            cursor.close()
            cmoney = 0
        else:
            try: cmoney = int(cursor.getValue('money'))
            except: cmoney = 0
            cursor.close()

        cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % sclient.id)
        if cursor.EOF:
            cursor.close()
            smoney = 0
        else:
            try: smoney = int(cursor.getValue('money'))
            except: smoney = 0
            cursor.close()

        cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
        if cursor.EOF:
            client.message('^1You do not have any coin')
            cursor.close()
        else:
            try: money = int(cursor.getValue('money'))
            except: money = 0
            cursor.close()
            if money >= value:
                self.debug('has enough money')
                if smoney + value >= self.MAX_WALLET_MONEY:
                    maxcoins = self.MAX_WALLET_MONEY - smoney
                    client.message('^3You can send ^5%s ^3a maximum amount of: ^2%s coins' % (sclient.name, maxcoins))
                else:
                    self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - value, client.id))
                    cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % sclient.id)
                    if cursor.EOF:
                        cursor = self.console.storage.query('INSERT INTO money (iduser, money) VALUES (%s, %s)' % (sclient.id, value))
                        cursor.close()
                    else:
                        try: money = int(cursor.getValue('money'))
                        except: money = 0
                        cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money + value, sclient.id))
                        cursor.close()
                        value2 = self.add_spaces(str(value))
                        client.message('^3You\'ve successfully transferred ^2%s coins' % value2)
                        sclient.message('^3You\'ve received ^2%s coins ^3from %s' % (value2, client.exactName))
                        self.update_minus_location(client, minus_reward)
            else:
                client.message('You dont have enough coins!')

    def cmd_inv(self, data, client, cmd=None):
        last = client.var(self, 'delay_inv', 0).value
        if (self.console.time() - last) < 360:
            client.message('You can only use this command every 5 minutes')
        else:
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            if cursor.EOF:
                client.message('You don\'t have any coin.')
                cursor.close()
            else:
                try: money = int(cursor.getValue('money'))
                except: money = 0
                cursor.close()
                if money >= 750000:
                    self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 750000, client.id))
                    self.console.write("invisible %s" % client.cid)
                    self.console.write('bigtext "%s is gone ^3INVISIBLE!"' % client.exactName)
                    client.message('You are ^2invisible ^7now! ^3(^260 Seconds^3)')
                    client.setvar(self, 'delay_inv', self.console.time())
                    t = Timer(30, self.remove_inv_mode, (client, ))
                    t.start()
                    minus_reward = 750000
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins')



    def getsupercoins(self, client=None, sclient=None, target=None):
        if client:
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            if cursor.EOF:
                scoins = 0
                cursor.close()
                return scoins
            else:
                try: scoins = int(cursor.getValue('scoins'))
                except: scoins = 0
                cursor.close()
                return scoins
        if sclient:
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % sclient.id)
            if cursor.EOF:
                scoins = 0
                cursor.close()
                return scoins
            else:
                try: scoins = int(cursor.getValue('scoins'))
                except: scoins = 0
                cursor.close()
                return scoins
        if target:
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % target.id)
            if cursor.EOF:
                scoins = 0
                cursor.close()
                return scoins
            else:
                try: scoins = int(cursor.getValue('scoins'))
                except: scoins = 0
                cursor.close()
                return scoins

    def addcoin(self, client):
        cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
        if cursor.EOF:
            client.message('^1something went wrong')
            cursor.close()
        else:
            try:  scoins = int(cursor.getValue('scoins'))
            except:  scoins = 0
            cursor.close()
            self.console.storage.query('UPDATE money SET scoins = %s WHERE iduser = %s' % (scoins + 1, client.id))

    def cmd_buysupercoin(self, data, client, cmd=None):
        cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
        if cursor.EOF:
            cursor.close()
            client.message('You dont have enough coins')
        else:
            try: money = int(cursor.getValue('money'))
            except: money = 0
            cursor.close()
            if money >= 20000000:
                self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 20000000, client.id))
                self.addcoin(client)
                self.console.write('bigtext "%s ^3just ^1BOUGHT ^3a ^6SUPER-COIN ^3for ^220.000.000 coins!"' % client.exactName)
                self.console.say('^3The ^6SUPER-COIN ^3gets you a ^2higher ranking ^3in ^6!topmoney')
            else:
                value2 = self.get_client_money(client)
                client.message('^3You have ^1%s^7/^220.000.000 coins.' % value2)

    def cmd_topmoney(self, data, client, cmd=None):
        """
        - shows top 3 players with the most money
        """
        cmd.sayLoudOrPM(client, '^3The ^23 richest players ^3on this ^5server ^3are:')
        c = 1
        cursor = self.console.storage.query('SELECT c.name, m.money, m.scoins FROM clients AS c INNER JOIN money AS m on c.id = m.iduser ORDER BY m.`scoins` DESC, `m`.`money` DESC LIMIT 0,3')
        while not cursor.EOF:
            r = cursor.getRow()
            cmd.sayLoudOrPM(client, '^5Rank ^2%s: ^3Name: ^2%s, ^6SuperCoins: ^2%s,  ^5Money: ^2%s' % (c, r['name'], r['scoins'], r['money']))
            cursor.moveNext()
            c += 1
        cursor.close()

    def cmd_buy(self, data, client, cmd=None):
        if not data:
            client.message('^3Type ^2!buy <weapon>')
            return

        if self.rules.buying is False:
            client.message('^3Buying weapons is currently ^1DISABLED.')
            return

        if (self.attachments.hasattachmentid == client.cid) or (self.attachments.isattachmentid == client.cid):
            client.message('^3You ^1cannot buy ^3weapons whilst having a player attached.')
            return

        handler = self._adminPlugin.parseUserCmd(data)
        weapon = handler[0]
        status = handler[1]
        if weapon == 'help' or weapon == '':
            client.message('^1Type ^7!buylist ^1to see the available weapons and items')
            return
        self.debug(client.team)
        if client.team != b3.TEAM_SPEC:
            if weapon == 'health':
                last = client.var(self, 'delay_healing', 0).value
                if (self.console.time() - last) < 15:
                    client.message('^3You can only use this command every 15 seconds')
                    return
                else:
                    self.debug('Weapon is health')
                    cursor = self.console.storage.query('SELECT * FROM money WHERE iduser= %s' % client.id)
                    try: money = int(cursor.getValue('money', 0))
                    except: money = 0
                    cursor.close()
                    if money >= self.weapons[weapon]:
                        cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - self.weapons[weapon], client.id))
                        cursor.close()
                        self.console.write("addhealth %s %s" % (client.cid, 100))
                        client.message('^3You\'ve bought ^2+100 health!')
                        minus_reward = self.weapons[weapon]
                        self.update_minus_location(client, minus_reward)
                        client.setvar(self, 'delay_healing', self.console.time())
                        return
                    else:
                        client.message('You don\'t have enough coins!')
                        return
            if status:
                if status.lower() == 'on':
                    weapexactname = self.getExactName(weapon)

                    # Clients may not autobuy NVG
                    if weapexactname == "NVG":
                        client.message("^3You ^1cannot ^3autobuy ^6NVG")
                        return

                    client.setvar(self, 'autobuyname', weapexactname)

                    weapmodname = self.getModName(weapon)
                    client.setvar(self, 'autobuy', weapmodname)

                    client.message('^5Autobuy ^3for %s ^2activated!' % weapexactname)
                elif status.lower() == 'off':
                    weapexactname = self.getExactName(weapon)
                    client.message('^5Autobuy ^3for %s ^1deactivated!' % weapexactname)
                    client.delvar(self, 'autobuy')
                    client.delvar(self, 'autobuyname')
                    return
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            try: money = int(cursor.getValue('money', 0))
            except: money = 0 
            cursor.close()
            if (weapon == "sr8") or (weapon == "SR8") or (weapon == "sr"):
                if money >= 8000:
                    minus_reward = 8000
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 8000, client.id))
                    cursor.close()
                    self.console.write("gw %s sr8 5 3" % client.cid)
                    client.message('^3You\'ve bought ^5SR-8 ^3for ^28000 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "spas") or (weapon == "SPAS") or (weapon == "Spas") or (weapon == "spas12") or (weapon == "Spas12") or (weapon == "FRANCHI") or (weapon == "franchi"):
                if money >= 12000:
                    minus_reward = 12000
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 12000, client.id))
                    cursor.close()
                    self.console.write("gw %s spas12 8 24" % client.cid)
                    client.message('^3You\'ve bought ^5SPAS-12 ^3for ^212000 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "mp5") or (weapon == "MP5") or (weapon == "MP5K") or (weapon == "mp5k"):
                if money >= 3250:
                    minus_reward = 3250
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 3250, client.id))
                    cursor.close()
                    self.console.write("gw %s mp5k 30 2" % client.cid)
                    client.message('^3You\'ve bought ^5MP5K ^3for ^23250 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "ump") or (weapon == "UMP") or (weapon == "UMP45") or (weapon == "ump45"):
                if money >= 3250:
                    minus_reward = 3250
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 3250, client.id))
                    cursor.close()
                    self.console.write("gw %s ump45 30 2" % client.cid)
                    client.message('^3You\'ve bought ^5UMP-45 ^3for ^23250 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "HK69") or (weapon == "hk69") or (weapon == "hk") or (weapon == "HK"):
                if money >= 5000:
                    minus_reward = 5000
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 5000, client.id))
                    cursor.close()
                    self.console.write("gw %s hk69 1 5" % client.cid)
                    client.message('^3You\'ve bought ^5HK-69 ^3for ^25000 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "lr300") or (weapon == "LR300") or (weapon == "LR") or (weapon == "lr"):
                if money >= 5500:
                    minus_reward = 5500
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 2500, client.id))
                    cursor.close()
                    self.console.write("gw %s lr 30 2" % client.cid)
                    client.message('^3You\'ve bought ^5LR-300 ^3for ^25500 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "PSG") or (weapon == "psg") or (weapon == "PSG1") or (weapon == "psg1"):
                if money >= 8000:
                    minus_reward = 8000
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 8000, client.id))
                    cursor.close()
                    self.console.write("gw %s psg1 8 3" % client.cid)
                    client.message('^3You\'ve bought ^5PSG1 ^3for ^28000 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "g36") or (weapon == "G36"):
                if money >= 6000:
                    minus_reward = 6000
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 6000, client.id))
                    cursor.close()
                    self.console.write("gw %s g36 30 2" % client.cid)
                    client.message('^3You\'ve bought ^5G36 ^3for ^26000 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "ak") or (weapon == "AK") or (weapon == "AK103") or (weapon == "ak103"):
                if money >= 7000:
                    minus_reward = 7000
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 7000, client.id))
                    cursor.close()
                    self.console.write("gw %s ak103 30 2" % client.cid)
                    client.message('^3You\'ve bought ^5AK-103 ^3for ^27000 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "NEGEV") or (weapon == "negev") or (weapon == "NE") or (weapon == "ne"):
                if money >= 4000:
                    minus_reward = 4000
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 4000, client.id))
                    cursor.close()
                    self.console.write("gw %s negev 100 2" % client.cid)
                    client.message('^3You\'ve bought ^5NEGEV ^3for ^24000 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "M4") or (weapon == "m4") or (weapon == "m4a") or (weapon == "M4A"):
                if money >= 2550:
                    minus_reward = 2550
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 2550, client.id))
                    cursor.close()
                    self.console.write("gw %s m4 30 2" % client.cid)
                    client.message('^3You\'ve bought ^5M4 ^3for ^22550 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')
            
            elif (weapon == "frf1") or (weapon == "FRF1") or (weapon == "frf") or (weapon == "FRF"):
                if money >= 8000:
                    minus_reward = 8000
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 8000, client.id))
                    cursor.close()
                    self.console.write("gw %s frf1 6 3" % client.cid)
                    client.message('^3You\'ve bought ^5FRF1 ^3for ^28000 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "benell") or (weapon == "benelli") or (weapon == "BENELLI") or (weapon == "beneli"):
                if money >= 10000:
                    minus_reward = 10000
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 10000, client.id))
                    cursor.close()
                    self.console.write("gw %s benelli 5 15" % client.cid)
                    client.message('^3You\'ve bought ^5Benelli ^3for ^210000 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "P90") or (weapon == "p90") or (weapon == "p9"):
                if money >= 3250:
                    minus_reward = 3250
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 3250, client.id))
                    cursor.close()
                    self.console.write("gw %s p90 50 2" % client.cid)
                    client.message('^3You\'ve bought ^5P90 ^3for ^23250 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "mac") or (weapon == "mac11") or (weapon == "mac-11"):
                if money >= 3250:
                    minus_reward = 3250
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 3250, client.id))
                    cursor.close()
                    self.console.write("gw %s mac11 32 2" % client.cid)
                    client.message('^3You\'ve bought ^5MAC11 ^3for ^23250 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "gib") or (weapon == "1shot") or (weapon == "fstod") or (weapon == "tod") or (weapon == "tod50") or (weapon == "tod-50"):
                if money >= 30000:
                    minus_reward = 30000
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 30000, client.id))
                    cursor.close()
                    self.console.write("gw %s fstod 1 0" % client.cid)
                    client.message('^3You\'ve bought ^5TOD-50 ^3for ^2300000 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "vest") or (weapon == "kev") or (weapon == "armor"):
                if money >= 1000:
                    minus_reward = 1000
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 1000, client.id))
                    cursor.close()
                    self.console.write("gi %s vest" % client.cid)
                    client.message('^3You\'ve bought ^5VEST ^3for ^21000 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "helmet") or (weapon == "helm") or (weapon == "head"):
                if money >= 800:
                    minus_reward = 800
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 800, client.id))
                    cursor.close()
                    self.console.write("gi %s helmet" % client.cid)
                    client.message('^3You\'ve bought ^5HELMET ^3for ^2800 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "silencer") or (weapon == "supressor") or (weapon == "sil"):
                if money >= 500:
                    minus_reward = 500
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 500, client.id))
                    cursor.close()
                    self.console.write("gi %s silencer" % client.cid)
                    client.message('^3You\'ve bought ^5SILENCER ^3for ^2500 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "laser") or (weapon == "LASER") or (weapon == "lase"):
                if money >= 500:
                    minus_reward = 500
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 500, client.id))
                    cursor.close()
                    self.console.write("gi %s laser" % client.cid)
                    client.message('^3You\'ve bought ^5LASER ^3for ^2500 coins.')
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

            elif (weapon == "NVG") or (weapon == "nvg") or (weapon == "nightvision"):
                if money >= 3000:
                    minus_reward = 3000
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 3000, client.id))
                    cursor.close()
                    self.console.write("gi %s nvg" % client.cid)
                    client.message('^3You\'ve bought ^8(^660 seconds^8) ^5NVG ^3for ^23000 coins.')
                    self.update_minus_location(client, minus_reward)
                    t = Timer(60, self.removeNVG, (client, ))
                    t.start()
                    
                else:
                    client.message('^3You ^1don\'t ^3have enough coins.')
            else:  
                client.message('^5Weapon ^1not found ^3- Check ^2!buylist')
        else:
            client.message('^1You can\'t buy weapons as spec!')
    
    def cmd_kitlist(self, data, client, cmd=None):
        client.message('^3Kitlist sent to your console')

    def cmd_kit(self, data, client, cmd=None):
        kitlist_msg = '^1Type ^7!kitlist ^1to see the available kits'
        def addClips(cid, clweapons, clips):
            for w in list(clweapons):
                self.console.write("giveclips %s %s %s" % (cid, clips, w))
        if client.bot:
            self.debug('bot')
        if not data:
            client.message('^3Type ^2!kit <Kit name/shorthand>')
            return
        if self.rules.buying is False:
            client.message('^3Buying kits is currently ^1DISABLED.')
            return
        handler = self._adminPlugin.parseUserCmd(data)
        kit = handler[0]
        if kit == 'help' or kit == '':
            client.message(kitlist_msg)
            return
        self.debug(client.team)
        if client.team != b3.TEAM_SPEC:
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            try: money = int(cursor.getValue('money', 0))
            except: money = 0
            cursor.close()
            available_kits = self.kits
            kit_match = list(filter(lambda x: kit.lower() in x.lower(), available_kits.keys()))
            if len(kit_match) > 1:
                client.message('^1Please be more specific. {}'.format(kitlist_msg))
            elif len(kit_match) < 1:
                client.message('^1Please choose a valid kit. {}'.format(kitlist_msg))
            else:
                kit_name = kit_match[0]
                kit_contents = copy.deepcopy(available_kits[kit_name])
                clips_cost = 0
                playerweapons = []
                if "clips" in kit_contents:
                    playerweapons = self.console.write("getweapons %s" % client.cid).split(",")
                    clipless = ["knife","fstod"]
                    playerweapons = [w for w in playerweapons if w not in clipless]
                    for w in playerweapons:
                        clips_cost += 2*500
                    kit_contents.remove("clips")
                kit_price = int(sum([self.weapons[k] for k in kit_contents]) * 0.9 + clips_cost)
                if money >= kit_price:
                    minus_reward = kit_price
                    cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - kit_price, client.id))
                    cursor.close()
                    if kit_name in ["Armor","Attachments"]:
                        for gear in kit_contents:
                            self.console.write("gi {} {}".format(client.cid, gear))
                        if len(playerweapons):
                            addClips(client.cid, playerweapons, 2)
                    else:
                        self.console.write("disarm %s" % client.name)
                        self.console.write("gw {} knife".format(client.cid))
                        for gear in kit_contents:
                            self.console.write("gw {} {}".format(client.cid, gear))
                    client.message('^3You\'ve bought the ^5{} Kit ^3for ^2{} coins.'.format(kit_name,kit_price))
                    self.update_minus_location(client, minus_reward)
                else:
                    client.message('You don\'t have enough coins.')

    def removeNVG(self, client):
        self.console.write("ri %s nvg" % client.cid)
        client.message("^6Tac-goggles ^3have been ^1removed")

    def cmd_ammo(self, data, client, cmd=None):
        last = client.var(self, 'delay_ammo', 0).value
        if (self.console.time() - last) < 120:
            client.message('You can only use this command every 2 minutes')
        else:
            if self.spendit(client,65000):
              self.console.write('givebullets %s 150' % client.name)
              client.message('^3Added ^2150 rounds ^3to your gun')
              client.setvar(self, 'delay_ammo', self.console.time())
            else:
              client.message('You don\'t have enough coins')


    def cmd_clips(self, data, client, cmd=None):

        last = client.var(self, 'delay_clips', 0).value

        if (self.console.time() - last) < 120:
            client.message('You can only use this command every 60 seconds')
        else:
            if self.spendit(client,45000):
                    self.console.write('giveclips %s 50' % client.name)
                    client.message('^3Added ^250 clips ^3to your gun')
                    client.setvar(self, 'delay_clips', self.console.time())
            else:
              client.message('You don\'t have enough coins')

            

    def cmd_maptp(self, data, client, cmd=None):
        maps = {
            'ut4_granja_bots_d3mod': '-456 -2488 -1935',
            'ut4_warehouse_bots': '-515 1650 752',
            'ut4_terrorism6_bots_d3mod': '-480 493 -1345',
            'ut4_ghosttown': '3108 480 659',
            'ut4_terrorism3_bots_d3mod': '2147 -938 -2351',
            'ut4_blitzkrieg_bots_d3mod': '2764 -4196 969',
            'ut4_rip_release_gbots_d3mod': '847 5121 130',
            'ut4_turnpike': '1590 -696 360',
            'ut4_village_classic_rc4_bots_d3mod': '-1973 -1170 508',
            'ut4_gad_dom_d3mod': '1458 243 1469',
            'ut4_algiers': '2781 1135 583',
            'ut4_blitzkrieg2_bots_d3mod': '2244 -109 831',
            'ut4_ramelle': '2593 3498 778',
            'ut4_abbey': '1460 1034 591'
        }
        mapname = self.console.getMap()
        cord = maps.get(mapname, -1)

        if mapname not in maps:
            client.message('^3No map teleport available for this map ^1:-(')
            return

        last = client.var(self, 'delay_maptp', 0).value
        if (self.console.time() - last) < 600:
            client.message('^3You can only use this command every 10 minutes')
        else:
            if self.spendit(client,50000):
              self.console.write('teleport %s %s' % (client.cid, cord))
              client.setvar(self, 'delay_maptp', self.console.time())
            else:
              client.message('You don\'t have enough coins')

    def cmd_disarm(self, data, client, cmd=None):
        """
        !disarm
        """
        if self.rules.restrict_disarm is True:
          client.message('^5!disarm ^3has been used on this map already.')
          return
        if self.spendit(client,500000):
          self.console.write('exec disarm2.txt')
          self.console.say('%s ^3has ^1disarmed ^5EVERYONE!' % client.exactName)
          self.console.write('bigtext "%s ^1disarmed ^5EVERYONE!"' % client.exactName)
          self.rules.buying = False
          self.rules.respawndisarm = True
          self.rules.restrict_disarm = True
          xtimer = Timer(30, self.reset_restrictions)
          xtimer.start()
          self.console.say('^5!buy ^3has been ^1disabled ^3 for ^630 seconds.')
        else:
          client.message('You dont have enough coins. Your coins are: %s' % money)

    def reset_restrictions(self):
        self.rules.buying = True
        self.rules.nades = False
        self.rules.respawndisarm = False
        self.console.say('^5!buy ^3has been ^2enabled.')

### new commands
    def cmd_laugh(self, data, client, cmd=None):
        last = client.var(self, 'delay_laugh', 0).value
        if (self.console.time() - last) < 60:
            client.message('You can only use this command once a minute')
        else:
          if self.spendit(client,25000):
            self.console.write("exec lol.txt")
            self.console.write('bigtext "%s ^3is laughing out loud!' % client.exactName)
            client.setvar(self, 'delay_laugh', self.console.time())
          else:
            client.message('You don\'t have enough coins')

    def cmd_heal(self, data, client, cmd=None):
        last = client.var(self, 'delay_healing', 0).value
        if (self.console.time() - last) < 4:
            client.message('^3You can only use this command every 4 seconds')
        else:
          if self.spendit(client,15000):
            self.console.write('addhealth %s 100' % client.name)
            client.message('^3You\'ve bought ^2+100 health!')
            client.setvar(self, 'delay_healing', self.console.time())
          else:
            client.message('You don\'t have enough coins')

    def cmd_nuke(self, data, client, cmd=None):
        m = self._adminPlugin.parseUserCmd(data)
        if not m:
            client.message('^7!nuke <player>')
            return

        sclient = self._adminPlugin.findClientPrompt(m[0], client)
        if not sclient:
            return

        last = client.var(self, 'delay_nuke', 0).value
        if (self.console.time() - last) < 300:
            client.message('You can only use this command every 5 minutes')
        else:
          if self.spendit(client,250000):
            self.console.write('nuke %s' % sclient.name)
            client.setvar(self, 'delay_nuke', self.console.time())
          else:
            client.message('You don\'t have enough coins')   

    def cmd_freeze(self, data, client, cmd=None):
        m = self._adminPlugin.parseUserCmd(data)
        if not m:
            client.message('^7!freeze <player>')
            return

        sclient = self._adminPlugin.findClientPrompt(m[0], client)
        if not sclient:
            return

        last = client.var(self, 'delay_freeze', 0).value
        if (self.console.time() - last) < 300:
            client.message('You can only use this command every 5 minutes')
        else:
          if self.spendit(client,550000):
            self.console.write('freeze %s' % sclient.name)
            tounfreeze = sclient.name
            client.message('^3You\'ve ^5frozen ^3%s for ^630 seconds!' % sclient.name)
            sclient.message('^3You were ^5frozen ^3by %s for ^630 seconds' % client.exactName)
            client.setvar(self, 'delay_freeze', self.console.time())
            t = Timer(30, self.remove_freeze_mode, (tounfreeze, ))
            t.start()
          else:
            client.message('You don\'t have enough coins')

    def cmd_serverslap(self, data, client, cmd=None):
        last = client.var(self, 'delay_serverslap', 0).value
        if (self.console.time() - last) < 1200:
            client.message('^3You can only use this command every 20 minutes')
        else:
          if self.spendit(client,1000000):
            self.console.say( "%s ^1slapped everyone! ^3Say thanks!!" % client.exactName)
            self.console.write("exec slap.txt")
            self.console.write('bigtext "%s ^1slapped ^3everyone!' % client.exactName)
            client.setvar(self, 'delay_serverslap', self.console.time())
          else:
            client.message('You don\'t have enough coins')

    def cmd_nades(self, data, client, cmd=None):
        cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
        if self.rules.restrict_nades is True:
            client.message('^5!nades ^3has been used on this map already.')
            cursor.close()
            return
        else:
          if self.spendit(client,500000):
            self.console.write("exec nades.txt")
            self.console.write('bigtext "%s ^2bought ^5nades for everbody ^3for ^2500.000 coins!' % client.exactName)
            self.rules.buying = False
            self.rules.restrict_nades = True
            self.rules.respawndisarm = True
            self.rules.nades = True
            xtimer = Timer(60, self.reset_restrictions)
            xtimer.start()
            self.console.say('^5!buy ^3has been ^1disabled ^3 for ^660 seconds.')
          else:
            client.message('You don\'t have enough coins')

    def cmd_slick(self, data, client, cmd=None):
        cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
        if self.rules.restrict_slick is True:
            client.message('^5!slick ^3has been used on this map already.')
            cursor.close()
            return
        if self.spendit(client,500000):
          self.console.write("mod_slickSurfaces 1")
          self.console.write('bigtext "^5Icy ^7Surfaces [^2ON^7]"')
          self.rules.restrict_slick = True
          xtimer = Timer(30, self.reset_slick)
          xtimer.start()
          self.console.write('^5!buy ^3has been ^1disabled ^3 for ^630 seconds.')
        else:
          client.message('You don\'t have enough coins')

    def reset_slick(self):
        self.console.write("mod_slickSurfaces 0")
        self.console.write('bigtext "^5Icy ^7Surfaces [1OFF^7]"')

    def cmd_airjumps(self, data, client, cmd=None):
        cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
        if self.rules.restrict_airjumps is True:
            client.message('^5!airjumps ^3has been used on this map already.')
            cursor.close()
            return
        if cursor.EOF:
            client.message('You don\'t have any coin.')
            cursor.close()
        else:
            money = int(cursor.getValue('money'))
            cursor.close()
            if money >= 1000000:
                self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 1000000, client.id))
                minus_reward = 1000000
                self.update_minus_location(client, minus_reward)
                self.console.write("mod_infiniteAirjumps 1")
                self.console.write('bigtext "^2JUMP ^5JUMP ^6JUMP"')
                self.rules.restrict_airjumps = True
                xztimer = Timer(60, self.reset_airjumps)
                xztimer.start()
            else:
                client.message('You don\'t have enough coins')

    def reset_airjumps(self):
        self.console.write("mod_infiniteAirjumps 0")

    def cmd_crazy(self, data, client, cmd=None):
        cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
        if self.rules.restrict_crazy is True:
            client.message('^5!crazy ^3has been used on this map already.')
            cursor.close()
            return
        if cursor.EOF:
            client.message('You don\'t have any coin.')
            cursor.close()
        else:
            money = int(cursor.getValue('money'))
            cursor.close()
            if money >= 1000000:
                self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 1000000, client.id))
                minus_reward = 1000000
                self.update_minus_location(client, minus_reward)
                self.console.write("exec crazy.txt")
                self.console.write('bigtext "%s ^3wants ^5everyone ^3to go ^2C^5r^3a^6z^7y' % client.exactName)
                self.rules.restrict_crazy = True
                xtimer = Timer(60, self.reset_crazy)
                xtimer.start()
            else:
                client.message('You don\'t have enough coins')

    def reset_crazy(self):
        self.console.write("exec resetcrazy.txt")

    def cmd_superbots(self, data, client, cmd=None):
        cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
        if self.rules.restrict_superbots is True:
            client.message('^5!superbots ^3has been used on this map already.')
            cursor.close()
            return
        if cursor.EOF:
            client.message('You don\'t have any coin.')
            cursor.close()
        else:
            money = int(cursor.getValue('money'))
            cursor.close()
            if money >= 500000:
                self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 500000, client.id))
                minus_reward = 500000
                self.update_minus_location(client, minus_reward)
                self.rules.restrict_superbots = True
                zutimer = Timer(60, self.reset_superbots)
                zutimer.start()
                self.rules.superbots = True
                self.console.write('bigtext "^6SUPERBOTS ^3will now spawn for ^51 Minute"')
                for client in self.console.clients.getList():
                    if client.bot:
                        self.console.write("smite %s" % client.cid)
            else:
                client.message('You don\'t have enough coins')

    def cmd_overclock(self, data, client, cmd=None):
        cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
        if self.rules.restrict_overclock is True:
            client.message('^5!overclock ^3has been used on this map already.')
            cursor.close()
            return
        if cursor.EOF:
            client.message('You don\'t have any coin.')
            cursor.close()
        else:
            money = int(cursor.getValue('money'))
            cursor.close()
            if money >= 500000:
                self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 500000, client.id))
                minus_reward = 500000
                self.update_minus_location(client, minus_reward)
                self.console.write("exec overclock.txt")
                self.rules.restrict_overclock = True
                utimer = Timer(30, self.reset_overclock)
                utimer.start()
            else:
                client.message('You don\'t have enough coins')

    def reset_superbots(self):
        self.rules.superbots = False

    def reset_overclock(self):
        self.console.write("exec resetoverclock.txt")

    def cmd_teleport(self, data, client, cmd=None):
        """
        !teleport <player>
        """
        m = self._adminPlugin.parseUserCmd(data)
        if not m:
            client.message('^7Type !Teleport <player>')
            return

        sclient = self._adminPlugin.findClientPrompt(m[0], client)
        if not sclient:
            return

        last = client.var(self, 'delay_telep', 0).value
        if (self.console.time() - last) < 600:
            client.message('You can only use this command every 10 minutes')
        else:
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            if cursor.EOF:
                client.message('You don\'t have any coin.')
                cursor.close()
            else:
                money = int(cursor.getValue('money'))
                cursor.close()
                if money >= 250000:
                    self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 250000, client.id))
                    self.console.write("teleport %s %s" % (client.cid, sclient.cid))
                    minus_reward = 250000
                    self.update_minus_location(client, minus_reward)
                    client.message('^6Teleported ^3to ^4%s' % sclient.name)
                    sclient.message('%s ^3has ^4teleported ^3to you!' % client.exactName)
                    client.setvar(self, 'delay_telep', self.console.time())
                else:
                    client.message('You don\'t have enough coins')

    def cmd_gravity(self, data, client, cmd=None):
        last = client.var(self, 'delay_gravity', 0).value
        if (self.console.time() - last) < 600:
            client.message('You can only use this command every 10 minutes')
        else:
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            if cursor.EOF:
                client.message('You don\'t have any coin.')
                cursor.close()
            else:
                money = int(cursor.getValue('money'))
                cursor.close()
                if money >= 1000000:
                    self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 1000000, client.id))
                    self.console.write("g_gravity 100")
                    self.console.write('bigtext "%s ^3turned on ^5Low-Gravity ^3for 1 minute!!' % client.exactName)
                    minus_reward = 1000000
                    self.update_minus_location(client, minus_reward)
                    client.setvar(self, 'delay_gravity', self.console.time())
                    t = Timer(60, self.remove_lowgrav_mode, (client, ))
                    t.start()
                else:
                    client.message('You don\'t have enough coins')

    def cmd_gamblestats(self, data, client, cmd=None):
        db_currents = self.getGambleStats()
        currwins = db_currents[0]
        currlosses = db_currents[1]
        totals = db_currents[2]
        self.console.say("^3Gambling stats:")
        self.console.say("^5Total Gambles: ^3%s" % totals)
        self.console.say("^2Wins: ^3%s" % currwins)
        self.console.say("^1Losses: ^3%s" % currlosses)

    def reset_attachments(self):
        self.attachments.hasattachmentid = None
        self.attachments.isattachmentid = None

    def cmd_attachplayer(self, data, client, cmd=None):
        if self.attachments.isattachmentid is not None:
            client.message('Someone else is being attached already. Try again later')
            return

        m = self._adminPlugin.parseUserCmd(data)
        if not m:
            client.message('^7!attach <player/bot>')
            return

        sclient = self._adminPlugin.findClientPrompt(m[0], client)
        if not sclient:
            return

        last = client.var(self, 'delay_attach', 0).value
        if (self.console.time() - last) < 600:
            client.message('You can only use this command once per map')
        else:
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            if cursor.EOF:
                client.message('You don\'t have enough coins')
                cursor.close()
            else:
                try:  money = int(cursor.getValue('money'))
                except:  money = 0
                cursor.close()
                if money >= 1000000:
                    self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - 1000000, client.id))
                    self.console.write('attach %s %s' % (sclient.name, client.name))
                    minus_reward = 1000000
                    self.update_minus_location(client, minus_reward)

                    sclient.message('^3You\'ve been attached to %s' % client.name)
                    sclient.message('^3Kill everything in sight!')

                    # Godmode the player having the attachment
                    self.console.write("sv_cheats 1")
                    self.console.write("spoof %s god" % client.name)
                    self.console.write("sv_cheats 0")

                    # Disarm the player having godmode
                    self.console.write("disarm %s" % client.name)

                    # Disarm the player that is being attached and give a gun to shoot with
                    self.console.write("disarm %s" % sclient.name)
                    self.console.write("gw %s hk69 255 255" % sclient.name)

                    # Set the clients
                    self.attachments.isattachmentid = sclient.cid
                    self.attachments.hasattachmentid = client.cid

                    client.setvar(self, 'delay_attach', self.console.time())

                    # Start the timer
                    t = Timer(30, self.reset_attachments)
                    t.start()

                else:
                    client.message('You don\'t have enough coins')

    def announceStats(self):
        MAX_MONEY_EARNED = 0
        MAX_MONEY_EARNED_CLIENT = "Noone"
        MOST_MESSAGES_SENT = 0
        MOST_MESSAGES_SENT_CLIENT = "Noone"
        MOST_HEADSHOTS = 0
        MOST_HEADSHOTS_CLIENT = "Noone"
        MOST_KILLS = 0
        MOST_KILLS_CLIENT = "Noone"
        MOST_HITS = 0
        MOST_HITS_CLIENT = "Noone"

        for client in self.console.clients.getList():
            moneyvar = client.var(self, 'money_earned').valueclient.var(self, 'money_earned').value
            if moneyvar is None:
                moneyvar = 0
            if moneyvar > MAX_MONEY_EARNED:
                MAX_MONEY_EARNED = moneyvar
                MAX_MONEY_EARNED_CLIENT = client.exactName

            messagevar = client.var(self, 'messages').value
            if messagevar is None:
                messagevar = 0
            if messagevar > MOST_MESSAGES_SENT:
                MOST_MESSAGES_SENT = messagevar
                MOST_MESSAGES_SENT_CLIENT = client.exactName

            killvar = client.var(self, 'kills').value
            if killvar is None:
                killvar = 0
            if killvar > MOST_KILLS:
                MOST_KILLS = killvar
                MOST_KILLS_CLIENT = client.exactName

            hsvar = client.var(self, 'headshots').value
            if hsvar is None:
                hsvar = 0
            if hsvar > MOST_HEADSHOTS:
                MOST_HEADSHOTS = hsvar
                MOST_HEADSHOTS_CLIENT = client.exactName

            hitvar = client.var(self, 'hits').value
            if hitvar is None:
                hitvar = 0
            if hitvar > MOST_HITS:
                MOST_HITS = hitvar
                MOST_HITS_CLIENT = client.exactName

        self.console.say("^6Awards this game:")
        self.console.say("^4Most Kills: ^6%s ^3with ^2%s Kills!" % (MOST_KILLS_CLIENT, MOST_KILLS))
        self.console.say("^4Most Headshots: ^6%s ^3with ^2%s Headshots!" % (MOST_HEADSHOTS_CLIENT, MOST_HEADSHOTS))
        self.console.say("^4Most Money earned: ^6%s ^3earned ^2%s coins!" % (MAX_MONEY_EARNED_CLIENT, MAX_MONEY_EARNED))
        self.console.say("^4Most Hits: ^6%s ^3with ^2%s hits!" % (MOST_HITS_CLIENT, MOST_HITS))
        self.console.say("^4Most Messages sent: ^6%s ^3sent ^2%s messages!" % (MOST_MESSAGES_SENT_CLIENT, MOST_MESSAGES_SENT))
    
