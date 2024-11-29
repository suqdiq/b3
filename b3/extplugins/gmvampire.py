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


class Bounty(object):
    tname = ''
    reward = 0
    tdeaths = 0

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

class Vampires(object):
    vamp1 = ''
    vamp2 = ''
    vampmoney1 = 0
    vampmoney2 = 0

class GmvampirePlugin(b3.plugin.Plugin):
    requiresConfigFile = False

    def onStartup(self):
        self.bounty = Bounty()
        self.vampires = Vampires()

        # Get admin plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # Something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return

        self.GAME_PATH = self.console.config.getpath('server', 'game_log').replace('games.log', "")

        # Register commands
        self._adminPlugin.registerCommand(self, 'vampire', 0, self.cmd_vampire)

        # Register events
        self.registerEvent(self.console.getEventID('EVT_CLIENT_KILL'), self.onKill)

    # Getblobting player team

    """
Map: q_1upxmas_bots
Players: 11
GameType: FFA
GameTime: 00:09:45
[connecting] Chicken
1:^4Buck^7ler^7 TEAM:FREE KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:--- IP:bot
2:PopCat^7 TEAM:FREE KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:popcat IP:94.63.53.70:27960
3:^6Ichnusa^7 TEAM:FREE KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:--- IP:bot
4:^6Mor^3ettone^7 TEAM:FREE KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:--- IP:bot
[connecting] Mantis
7:Franzis^7 TEAM:FREE KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:--- IP:bot
8:TarTofu^7 TEAM:FREE KILLS:1 DEATHS:0 ASSISTS:0 PING:0 AUTH:--- IP:bot
9:Guinness^7 TEAM:FREE KILLS:0 DEATHS:1 ASSISTS:0 PING:0 AUTH:--- IP:bot
11:Heineken^7 TEAM:FREE KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:--- IP:bot
12:KillKenny?^7 TEAM:FREE KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:--- IP:bot
    """

    def parse_player_command(self, input_text):
        """Parse the result of the 'player' console command."""
        ##self.info('XXX PLAYERS INPUT TEXT XXX: '+input_text)
        lines = input_text.splitlines()
        players = []

        for line in lines:
            if line.find(' KILLS')!=-1:
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

    def grab_player2(self, client):
        """Getting playerlist via rcon players"""

        input_blob = self.console.write('players')

        # from this_file import parse_player_command
        #players = self.parse_player_command(input_blob)
        players = [p for p in self.parse_player_command(input_blob) if p != None]
        if players:
          found_player = [p for p in players if client.name in p.name]
          if found_player:
              return found_player[0]
        else:
            self.debug('No player found matching %s' % client.name )

    ####################################################################################################################
    #                                                                                                                  #
    #    Events                                                                                                        #
    #                                                                                                                  #
    ####################################################################################################################

    def onKill(self, event):
        client = event.client
        if not client.bot:
            self.checkRewards(event.client, event.target)

    ####################################################################################################################
    #                                                                                                                  #
    #    Updating the location string                                                                                  #
    #                                                                                                                  #
    ####################################################################################################################


    def checkRewards(self, client, target):
        target_name = self.bounty.tname
        vampire_1 = self.vampires.vamp1
        vampire_2 = self.vampires.vamp2
        kill_reward = self.bounty.reward
        if target.name == vampire_1 or target.name == vampire_2:
            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            try: money = int(cursor.getValue('money'))
            except: money = 0
            cursor.close()
            cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money + 1500, client.id))
            cursor.close()
            client.message('^3Killed a ^1VAMPIRE^3: ^2+1500 coins')
            #self.update_location(client)
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

    def add_spaces(self, value):
        leader = value[0:len(value) % 3].strip()
        return  leader + "." * bool(leader) + ".".join(group[::-1] for group in re.findall("...", value[::-1])[::-1])

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
                #self.update_minus_location(client, minus_reward)
            else:
                self.debug('vamp1 taken - trying vamp2')
                if Vampires.vamp2 == '':
                    self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money - vampool, client.id))
                    Vampires.vampmoney2 = vampool
                    Vampires.vamp2 = client.name
                    self.vampstuff1(client)
                    self.vampstuff3(client)
                    self.console.write('bigtext "%s ^3is now a ^1VAMPIRE!"' % client.exactName)
                    #self.update_minus_location(client, minus_reward)
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
