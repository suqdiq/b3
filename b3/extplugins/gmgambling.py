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
__version__ = '1.1a'

import b3
import re
import b3.events
import b3.plugin
from random import *
import time
import random as rand
import copy

class GmgamblingPlugin(b3.plugin.Plugin):

    requiresConfigFile = False

    MAX_WALLET_MONEY = 250000000

    gamble_times = {}

    def onStartup(self):

        # Get admin plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # Something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return

        # Register commands
        self._adminPlugin.registerCommand(self, 'gamble', 0, self.cmd_gamble)

        self.GAME_PATH = self.console.config.getpath('server', 'game_log').replace('games.log', "")

        # Register events
        self.registerEvent(self.console.getEventID('EVT_CLIENT_AUTH'), self.onAuth)
        self.registerEvent(self.console.getEventID('EVT_GAME_ROUND_END'), self.onRoundend)


    def onAuth(self, event):
        client = event.client
        if client.bot:
            self.debug('XXX Bot')
        else:
            # set money earned this session
            client.setvar(self, 'money_earned', 0)

            cursor = self.console.storage.query('SELECT * FROM money WHERE iduser = %s' % client.id)
            if cursor.rowcount == 0:
                cursor = self.console.storage.query('INSERT INTO money (iduser, money) VALUES (%s , %s)' % (client.id, 15000))
                cursor.close()

    def onRoundend(self, event):
        self.console.write("exec roundend.txt")
        self.gamble_times = {}

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

    def add_spaces(self, value):
        leader = value[0:len(value) % 3].strip()
        return  leader + "." * bool(leader) + ".".join(group[::-1] for group in re.findall("...", value[::-1])[::-1])

    def cmd_gamble(self, data, client, cmd=None):
        last = client.var(self, 'delay_gamble', 0).value
        if (self.console.time() - last) < 30:
            # Allow gambles only every 2 minutes
            time1 = (self.console.time() - last)
            time2 = 30 - time1
            client.message('^3You use this ^5Command ^3again in ^6%s seconds' % time2)
        
        elif (client.cid in self.gamble_times) and (int(time.time())-self.gamble_times[client.cid] < 30 ):
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
        
            elif gam < 5000:
                client.message('^3You need to gamble at least 5000 coins!')
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
                            #self.update_location(client, None, True)

                        else:
                            # Add the money to the current money
                            cursor = self.console.storage.query('UPDATE money SET money = %s WHERE iduser = %s' % (money + reward, client.id))
                            cursor.close()
                
                            self.console.say('^3Congratulations to %s for winning a total of ^2%s coins!!' % (client.exactName, value2))
                            #self.update_location(client, reward, True)
    
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
                        #self.update_minus_location(client, minus_reward)
                else:
                    client.message('You dont have enough coins to do this gamble!')


    def cmd_gamblestats(self, data, client, cmd=None):
        db_currents = self.getGambleStats()
        currwins = db_currents[0]
        currlosses = db_currents[1]
        totals = db_currents[2]
        self.console.say("^3Gambling stats:")
        self.console.say("^5Total Gambles: ^3%s" % totals)
        self.console.say("^2Wins: ^3%s" % currwins)
        self.console.say("^1Losses: ^3%s" % currlosses)
