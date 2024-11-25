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
__version__ = '1.0'

import b3
import re
import b3.events
import b3.plugin
import urllib
import ipinfo

class BetterwelcomePlugin(b3.plugin.Plugin):
    requiresConfigFile = False

    #Getting Plugin admin (cannot register commands without it)
    def onStartup(self):
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            self.error('Could not find admin plugin')
            return

        # Registering events
        self.registerEvent(self.console.getEventID('EVT_CLIENT_CONNECT'), self.onConnect)

    ####################################################################################################################
    #                                                                                                                  #
    #    Events                                                                                                        #
    #                                                                                                                  #
    ####################################################################################################################

    def onConnect(self, event):
        client = event.client

        if client.bot:
            # Do not welcome bots
            return

        if client.pbid == "WORLD":
            # Do not welcome WORLD
            return

        # Client auth status
        authStatus = self.checkAuthedStatus(client)
        if authStatus:
            auth = "^2[Authed]"
        else:
            auth = ""

        # Client clan tag
        if client.pbid:
            authTag = self.getAuthTag(client)
        else:
            authTag = ""

        # Client Country Name
        CountryName = self.getCountryName(client)

        # Client connections
        connections = client.connections

        # Client unique ID
        uniqueId = client.id

        # Levels
        if client.maxLevel == 1 or client.maxLevel == 0:
            level = "^7[User]"
        if client.maxLevel == 2:
            level = "^7[Common]"
        if client.maxLevel == 80:
            level = "^3[Admin]"
        if client.maxLevel == 100:
            level = "^1[Owner]"
        
        # Now send our messages
        self.console.write("say \"%s%s^6%s^3%s^4(@%s) ^2(%s connections) ^3connected from ^8%s\"" % (level, auth, authTag, client.exactName, uniqueId, connections, CountryName))

    ####################################################################################################################
    #                                                                                                                  #
    #    Functions                                                                                                     #
    #                                                                                                                  #
    ####################################################################################################################

    def checkAuthedStatus(self, client):
        cursor = self.console.storage.query('SELECT * FROM isauthed WHERE iduser = %s' % client.id)
        if cursor.EOF:
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def getAuthTag(self, client):
        if not client.pbid:
            return
        else:
            urbanterror_url=urllib.urlopen("https://www.urbanterror.info/members/profile/%s/" % client.pbid)
            player_page=urbanterror_url.read()
            try:
                auth = player_page.split('<h2><span class="userTag start">')[1].lstrip().split('</span><span class="userName">')[0]
            except:
                auth = " "
                return(auth)
            else:
                return(auth)

    def getCountryName(self, client):
        ip = str(client.ip)
        access_token = "get ur own from ipinfo"
        handler = ipinfo.getHandler(access_token)
        details = handler.getDetails(ip)
        country = details.country
        return(country)
