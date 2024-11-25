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
__version__ = '1.7'

import b3
import re
import b3.events
import b3.plugin
import random, string
import time
import random as rand
from random import randint

from b3.cron import PluginCronTab
from threading import Timer

class CustomgunmoneyPlugin(b3.plugin.Plugin):
    requiresConfigFile = False

    greeting_times = {}



    def onStartup(self):
        self.GAME_PATH = self.console.config.getpath('server', 'game_log').replace('games.log', "")
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # Can't start without the admin plugin
            self.error('Could not find admin plugin')
            return

        # Registering Events
        self.registerEvent(self.console.getEventID('EVT_GAME_ROUND_END'), self.onRoundend2)
        self.registerEvent(self.console.getEventID('EVT_CLIENT_JOIN'), self.onChange)

        # Registering commands
        self._adminPlugin.registerCommand(self, 'buylist', 0, self.cmd_buylist)
        self._adminPlugin.registerCommand(self, 'server', 0, self.cmd_servers, 'servers')
        self._adminPlugin.registerCommand(self, 'authme', 0, self.cmd_authme)
        self._adminPlugin.registerCommand(self, 'setcolour', 0, self.cmd_setcolour)
        self._adminPlugin.registerCommand(self, 'hi', 0, self.cmd_bhi, 'hello')
        self._adminPlugin.registerCommand(self, 'hiall', 0, self.cmd_bhiall, 'helloall')
        self._adminPlugin.registerCommand(self, 'funremove', 20, self.cmd_funremove, 'funfree')
        self._adminPlugin.registerCommand(self, 'helpme', 0, self.cmd_helpme)
        self._adminPlugin.registerCommand(self, 'help', 0, self.cmd_help)
        self._adminPlugin.registerCommand(self, 'setbots', 20, self.cmd_setbots, 'bots')
        self._adminPlugin.registerCommand(self, 'adminhelp', 20, self.cmd_adminhelp)
        #self._adminPlugin.registerCommand(self, 'callvote', 0, self.cmd_voting, 'cv')
        self._adminPlugin.registerCommand(self, 'like', 0, self.cmd_vote_1)
        self._adminPlugin.registerCommand(self, 'dislike', 0, self.cmd_vote_2)
        self._adminPlugin.registerCommand(self, 'stats', 0, self.mapstats, 'mapstats')
        self._adminPlugin.registerCommand(self, 'rename', 20, self.cmd_rename)
        self._adminPlugin.registerCommand(self, 'demo', 20, self.cmd_demo)
        self._adminPlugin.registerCommand(self, 'mute', 20, self.cmd_pamute)
        self._adminPlugin.registerCommand(self, 'spec', 20, self.cmd_spec)

    ####################################################################################################################
    #                                                                                                                  #
    #    Events                                                                                                        #
    #                                                                                                                  #
    ####################################################################################################################
    

    def onRoundend2(self, event):
        nextmapname = self.console.getNextMap()
        likes = self.getlikes2()
        dislikes = self.getdislikes2()
        self.console.say('^5Nextmap is: ^6%s' % nextmapname)
        self.console.say('^5%s^6: ^2%s Likes ^5- ^1%s Dislikes' % (nextmapname, likes, dislikes))

    def onChange(self, event):
        client = event.client
        if client.bot:
            self.debug('Bot')
        self.presetcolour(client)
        self.announcetoauth(client)
        if client.maxLevel == 100:
            self.console.write('setowner %s' % client.cid)
            self.console.write('setauthed %s' % client.cid)
        if client.maxLevel == 80:
            self.console.write('setadmin %s' % client.cid)
            if self.checkauthed(client) is True:
                self.console.write('setauthed %s' % client.cid)
        if client.maxLevel <= 15:
            self.console.write('setuser %s' % client.cid)
            if self.checkauthed(client) is True:
                self.console.write('setauthed %s' % client.cid)

    def announcetoauth(self, client):
        time.sleep(3)
        if self.checkauthed(client) is False:
            client.message('^3You are ^1NOT AUTHED^3, benefits from authing are ^21.2x the money income')
            client.message('^3and more. To auth yourself type ^6!authme')

    def presetcolour(self, client):
        cursor = self.console.storage.query('SELECT * FROM chatcolour WHERE iduser = %s' % client.id)
        if cursor.EOF:
            colour = 7
            cursor.close()
            self.console.write('setcolour %s %s' % (client.cid, colour))
        else:
            cursor.close()
            colours = self.returncolours(client)
            randcolour = random.choice(colours)
            self.console.write('setcolour %s %s' % (client.cid, randcolour))

    def cmd_setcolour(self, data, client, cmd=None):  
        colours = self.returncolours(client)
        if not colours:
            client.message('You dont have any colours available')
            return
        if not data:
            client.message('^3Your available colours are: %s' % colours)
            return
        else:
            handler = self._adminPlugin.parseUserCmd(data)
            wantscolour = int(handler[0])
            if wantscolour in colours:
                self.console.write('setcolour %s %s' % (client.cid, wantscolour))
            else:
                client.message('Colour not avaliable, your colours are: %s' % colours)

    def returncolours(self, client):
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
        return(colours)
        
    ####################################################################################################################
    #                                                                                                                  #
    #    Admin commands                                                                                                #
    #                                                                                                                  #
    ####################################################################################################################

    def cmd_pamute(self, data, client, cmd=None):        
        m = self._adminPlugin.parseUserCmd(data)
        if not m:
            client.message('^7!mute <player>')
            return

        sclient = self._adminPlugin.findClientPrompt(m[0], client)
        if not sclient:
            return
        else:
            self.console.write('mute %s' % sclient.name)
            client.message('Muted %s' % sclient.name)

    def cmd_spec(self, data, client, cmd=None):        
        m = self._adminPlugin.parseUserCmd(data)
        if not m:
            client.message('^7!spec <player>')
            return
        sclient = self._adminPlugin.findClientPrompt(m[0], client)
        if not sclient:
            return
        else:
            self.console.write('forceteam %s spec' % sclient.name)
            client.message('Forced %s to spectators' % sclient.name)

    def cmd_adminhelp(self, data, client, cmd=None):
        last = client.var(self, 'adminhelpdelay', 0).value
        if (self.console.time() - last) < 45:
            client.message('Please wait 45 seconds before you try again!')
        else:
            fin = open(self.GAME_PATH+"adminhelp.txt", "rt")
            data = fin.read()
            data = data.replace('XDATA1', client.name)
            fin.close()
            fin = open(self.GAME_PATH+"adminhelp.txt", "wt")
            fin.write(data)
            fin.close()
            self.console.write('exec adminhelp.txt')
            fin = open(self.GAME_PATH+"adminhelp.txt", "rt")
            data = fin.read()
            data = data.replace(client.name, 'XDATA1')
            fin.close()
            fin = open(self.GAME_PATH+"adminhelp.txt", "wt")
            fin.write(data)
            fin.close()
            client.setvar(self, 'adminhelpdelay', self.console.time())

    def cmd_rename(self, data, client, cmd=None):
        m = self._adminPlugin.parseUserCmd(data)
        handler = self._adminPlugin.parseUserCmd(data)
        newname = handler[1]
        sclient = self._adminPlugin.findClientPrompt(m[0], client)
        if not sclient:
            return
        self.console.write('forcecvar %s %s' % (sclient.cid, newname))
        client.message('Renamed %s' % sclient.name)

    def cmd_demo(self, data, client, cmd=None):
        m = self._adminPlugin.parseUserCmd(data)
        sclient = self._adminPlugin.findClientPrompt(m[0], client)
        if not sclient:
            return
        self.console.write('startserverdemo %s' % sclient.cid)
        client.message('%s is now being recorded - Contact donna30 in discord to get the demo!' % sclient.name)

    def cmd_setbots(self, data, client, cmd=None):
        handler = self._adminPlugin.parseUserCmd(data)
        if not handler:
            client.message('^7!setbots <amount>')
        else:
            value = int(handler[0])
            self.console.write('bot_minplayers %s' % value)
            client.message('Set minimum players/bots to: %s' % value)

    def cmd_funremove(self, data, client, cmd=None):
        last = client.var(self, 'delay_funremove', 0).value
        m = self._adminPlugin.parseUserCmd(data)
        if not m:
            client.message('^7!funremove <player>')
            return

        sclient = self._adminPlugin.findClientPrompt(m[0], client)
        if not sclient:
            return

        if (self.console.time() - last) < 10:
            client.message('^3You can only use this command every 10 seconds')
        else:
            self.console.write('forcecvar %s funfree none' % sclient.name)
            client.message('Removed funstuff from %s' % sclient.name)
            client.setvar(self, 'delay_funremove', self.console.time())


    ####################################################################################################################
    #                                                                                                                  #
    #    User commands                                                                                                 #
    #                                                                                                                  #
    ####################################################################################################################
    
    def cmd_help(self, data, client, cmd=None):
        last = client.var(self, 'helpdelay', 0).value
        if (self.console.time() - last) < 45:
            client.message('Please wait 45 seconds before you try again!')
        else:
            fin = open(self.GAME_PATH+"helpfile.txt", "rt")
            data = fin.read()
            data = data.replace('XDATA1', client.name)
            fin.close()
            fin = open(self.GAME_PATH+"helpfile.txt", "wt")
            fin.write(data)
            fin.close()
            self.console.write('exec helpfile.txt')
            fin = open(self.GAME_PATH+"helpfile.txt", "rt")
            data = fin.read()
            data = data.replace(client.name, 'XDATA1')
            fin.close()
            fin = open(self.GAME_PATH+"helpfile.txt", "wt")
            fin.write(data)
            fin.close()
            client.setvar(self, 'helpdelay', self.console.time())

    def cmd_helpme(self, data, client, cmd=None):
        last = client.var(self, 'delay_helpme', 0).value
        if (self.console.time() - last) < 60:
            client.message('^3You can only use this command every 60 seconds')
        else:
            fin = open(self.GAME_PATH+"helpen.txt", "rt")
            data = fin.read()
            data = data.replace('xdata1', client.name)
            fin.close()
            fin = open(self.GAME_PATH+"helpen.txt", "wt")
            fin.write(data)
            fin.close()
            self.console.write('exec helpen.txt')
            fin = open(self.GAME_PATH+"helpen.txt", "rt")
            data = fin.read()
            data = data.replace(client.name, 'xdata1')
            fin.close()
            fin = open(self.GAME_PATH+"helpen.txt", "wt")
            fin.write(data)
            fin.close()
            client.message('^2Helpfile ^3sent to your console!')
            client.setvar(self, 'delay_helpme', self.console.time())


    #def cmd_mapinfo(self, data, client, cmd=None):
    #    mapname = self.console.getMap()
    #    nextmapname = self.console.getNextMap()

    #    last = client.var(self, 'delay_mapinfo', 0).value
    #    if (self.console.time() - last) < 120:
    #        client.message('You can only use this command every 2 minutes')
    #    else:
    #        client.setvar(self, 'delay_mapinfo', self.console.time())
    #        fin = open(self.GAME_PATH+"/nmap.txt", "rt")
    #        data = fin.read()
    #        data = data.replace('xdata1', mapname)
    #        data = data.replace('xdata2', nextmapname)
    #        fin.close()
    #        fin = open(self.GAME_PATH+"/nmap.txt", "rt")
    #        fin.write(data)
    #        fin.close()
    #        self.console.write('exec nmap.txt')
    #        fin = open(self.GAME_PATH+"/nmap.txt", "rt")
    #        data = fin.read()
    #        data = data.replace(mapname, 'xdata1')
    #        data = data.replace(nextmapname, 'xdata2')
    #        fin.close()
    #        fin = open(self.GAME_PATH+"/nmap.txt", "rt")
    #        fin.write(data)
    #        fin.close()


    def cmd_buylist(self, data, client, cmd=None):
        client.message('^3Buylist sent to your console')
    #    last = client.var(self, 'buylistdelay', 0).value
    #    if (self.console.time() - last) < 45:
    #        client.message('Please wait 45 seconds before you try again!')
    #    else:
    #        fin = open(self.GAME_PATH+"/buylist2.txt", "wt")
    #        data = fin.read()
    #        data = data.replace('xdata1', client.name)
    #        fin.close()
    #        fin = open(self.GAME_PATH+"/buylist2.txt", "wt")
    #        fin.write(data)
    #        fin.close()
    #        self.console.write('exec buylist2.txt')
    #        fin = open(self.GAME_PATH+"/buylist2.txt", "wt")
    #        data = fin.read()
    #        data = data.replace(client.name, 'xdata1')
    #        fin.close()
    #        fin = open(self.GAME_PATH+"/buylist2.txt", "wt")
    #        fin.write(data)
    #        fin.close()
    #        client.setvar(self, 'buylistdelay', self.console.time())

    def cmd_servers(self, data, client, cmd=None):
        last = client.var(self, 'serverdelay', 0).value
        if (self.console.time() - last) < 45:
            client.message('Please wait 45 seconds before you try again!')
        else:
            self.console.write('exec servers.txt')
            client.setvar(self, 'serverdelay', self.console.time())

    def cmd_vote_1(self, data, client, cmd=None):
        mapname = self.console.getMap()
        cursor = self.console.storage.query('SELECT * FROM votedplayers WHERE iduser = %s AND mapname = "%s"' % (client.id, mapname))
        if cursor.rowcount == 0:
            cursor = self.console.storage.query('INSERT INTO votedplayers (iduser, mapname) VALUES (%s , "%s")' % (client.id, mapname))
            client.message('^3You ^2Liked ^3this map! Thanks for your feedback.')
            vt = "like"
            self.addvotes(vt, mapname)
            cursor.close()
        else:
            client.message('^3You already ^1VOTED ^3for this map.')
            cursor.close()
        cursor.close()

    def cmd_vote_2(self, data, client, cmd=None):
        mapname = self.console.getMap()
        cursor = self.console.storage.query('SELECT * FROM votedplayers WHERE iduser = %s AND mapname = "%s"' % (client.id, mapname))
        if cursor.rowcount == 0:
            cursor = self.console.storage.query('INSERT INTO votedplayers (iduser, mapname) VALUES (%s , "%s")' % (client.id, mapname))
            client.message('^3You ^2Disliked ^3this map! Thanks for your feedback.')
            vt = "dislike"
            self.addvotes(vt, mapname)
            cursor.close()
        else:
            client.message('^3You already ^1VOTED ^3for this map.')
            cursor.close()
        cursor.close()

    def randomword(self, length):
       letters = string.ascii_lowercase
       return ''.join(random.choice(letters) for i in range(length))

    def cmd_authme(self, data, client, cmd=None):
        cursor = self.console.storage.query('SELECT * FROM isauthed WHERE iduser = %s' % client.id)
        if cursor.EOF:
            cursor.close()
            # The client hasn't authed himself already so we check if he has a pending auth process
            cursor = self.console.storage.query('SELECT * FROM dauth WHERE iduser = %s' % client.id)
            if cursor.EOF:
                cursor.close()
                #client.message('^3Join the discord: ^5discord.gg/KMYkcdK')
                client.message('^3PM the ^5d3bot ^3in ^4discord ^3with the following password:')
                client.message('^3Your ^2Password ^3is: ^6AUTHME-%s' % client.id)
                cursor = self.console.storage.query('INSERT INTO dauth (iduser, password) VALUES ("%s", "AUTHME-%s")' % (client.id, client.id))
                t = Timer(300, self.del_discordauth, (client, ))
                t.start()
                cursor.close()
            else:
                client.message('You still have an authentication in process')
                client.message('Please follow the instructions that were given to you')
                cursor.close
        else:
            duser = str(cursor.getValue('discorduser'))
            client.message('You have been authed already as: ^6%s' % duser)
            client.message('If you think this was a mistake, please contact donna30')
            cursor.close()

    def del_discordauth(self, client):
        cursor = self.console.storage.query('DELETE FROM dauth WHERE iduser = %s' % client.id)
        cursor.close

    def addvotes(self, vt, mapname):
        cursor = self.console.storage.query('SELECT * FROM mapstats WHERE mapname = "%s"' % mapname)
        if cursor.rowcount == 0:
            self.debug('Adding map')
            cursor = self.console.storage.query('INSERT INTO mapstats (mapname, likes, dislikes) VALUES ("%s" , %s, %s)' % (mapname, 1, 1))
            cursor.close()
        else:
            self.debug('Updating map')
            if vt == "like":
                likes = int(cursor.getValue('likes'))
                cursor = self.console.storage.query('UPDATE mapstats SET likes = %s WHERE mapname = "%s"' % (likes + 1, mapname))
                cursor.close()
            else:
                dislikes = int(cursor.getValue('dislikes'))
                cursor = self.console.storage.query('UPDATE mapstats SET dislikes = %s WHERE mapname = "%s"' % (dislikes + 1, mapname))   
                cursor.close()        
    
    def getlikes(self):
        mapname = self.console.getMap()
        cursor = self.console.storage.query('SELECT * FROM mapstats WHERE mapname = "%s"' % mapname)
        if cursor.rowcount == 0:
            self.debug('No likes available')
            likes = 0
            cursor.close()
            return(likes)
        else:
            likes = int(cursor.getValue('likes'))
            cursor.close()
            return(likes)

    def getdislikes(self):
        mapname = self.console.getMap()
        cursor = self.console.storage.query('SELECT * FROM mapstats WHERE mapname = "%s"' % mapname)
        if cursor.rowcount == 0:
            self.debug('No dislikes available')
            dislikes = 0
            cursor.close()
            return(dislikes)            
        else:
            dislikes = int(cursor.getValue('dislikes'))
            cursor.close()
            return(dislikes)

    def mapstats(self, data, client, cmd=None):
        likes = self.getlikes()
        dislikes = self.getdislikes()
        mapname = self.console.getMap()
        self.console.say('^5%s^6: ^2%s Likes ^5- ^1%s Dislikes' % (mapname, likes, dislikes))

    def cmd_bhi(self, data, client, cmd=None):
        last = client.var(self, 'delay_hi', 0).value
        m = self._adminPlugin.parseUserCmd(data)
        if not m:
            client.message('^7!hi <player>')
            return

        sclient = self._adminPlugin.findClientPrompt(m[0], client)
        if not sclient:
            return
        
        if client.name == sclient.name:
            client.message('Can NOT say hi to yourself')
            return
     
        if (self.console.time() - last) < 120:
            client.message('^3You can only use this command every 2 Minutes')
        else:
            fin = open(self.GAME_PATH+"/hello2.txt", "rt")
            data = fin.read()
            data = data.replace('player1', client.name)
            data = data.replace('player2', sclient.name)
            fin.close()
            fin = open(self.GAME_PATH+"hello2.txt", "wt")
            fin.write(data)
            fin.close()
            self.console.write('exec hello2.txt')
            fin = open(self.GAME_PATH+"hello2.txt", "rt")
            data = fin.read()
            data = data.replace(client.name, 'player1')
            data = data.replace(sclient.name, 'player2')
            fin.close()
            fin = open(self.GAME_PATH+"hello2.txt", "wt")
            fin.write(data)
            fin.close()
            client.setvar(self, 'delay_bhi', self.console.time())


    def cmd_bhiall(self, data, client, cmd=None):
        last = client.var(self, 'delay_bhiall', 0).value
        if (self.console.time() - last) < 600:
            client.message('^3You can only use this command every 10 minutes')
        else:
            fin = open(self.GAME_PATH+"hello3.txt", "rt")
            data = fin.read()
            data = data.replace('player', client.name)
            fin.close()
            fin = open(self.GAME_PATH+"hello3.txt", "wt")
            fin.write(data)
            fin.close()
            self.console.write('exec hello3.txt')
            fin = open(self.GAME_PATH+"hello3.txt", "rt")
            data = fin.read()
            data = data.replace(client.name, 'player')
            fin.close()
            fin = open(self.GAME_PATH+"hello3.txt", "wt")
            fin.write(data)
            fin.close()
            client.setvar(self, 'delay_bhiall', self.console.time())


    def cmd_voting(self, data, client, cmd=None):
        handler = self._adminPlugin.parseUserCmd(data)
        votetype = handler[0]
        if "cyclemap" in votetype:
            self.console.write('spoof %s callvote cyclemap"' % client.name)
            self.console.write('bigtext "^7A ^2Vote ^7was called!"')
            self.console.say('%s ^3called a ^2vote to cycle the map!' % client.name)

    def getlikes2(self):
        mapname = self.console.getNextMap()
        cursor = self.console.storage.query('SELECT * FROM mapstats WHERE mapname = "%s"' % mapname)
        if cursor.rowcount == 0:
            self.debug('No likes available')
            likes = 0
            cursor.close()
            return(likes)
        else:
            likes = int(cursor.getValue('likes'))
            cursor.close()
            return(likes)

    def getdislikes2(self):
        mapname = self.console.getNextMap()
        cursor = self.console.storage.query('SELECT * FROM mapstats WHERE mapname = "%s"' % mapname)
        if cursor.rowcount == 0:
            self.debug('No dislikes available')
            dislikes = 0
            cursor.close()
            return(dislikes)            
        else:
            dislikes = int(cursor.getValue('dislikes'))
            cursor.close()
            return(dislikes)

    def checkauthed(self, client):
        cursor = self.console.storage.query('SELECT * FROM isauthed WHERE iduser = %s' % client.id)
        if cursor.EOF:
            cursor.close()
            return False
        else:
            cursor.close()
            return True
