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
# Fixing the issues titanmod causes to bots
# This is NOT the right way to do it and by far not the fastest way
# But it works

__author__ = 'donna30'   
__version__ = '1.0'

import b3
import re
import b3.events
import b3.plugin

class FixbotsPlugin(b3.plugin.Plugin):
    requiresConfigFile = False

    def onStartup(self):
        # Get admin plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # Something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return

        # Register events
        self.registerEvent(self.console.getEventID('EVT_CLIENT_AUTH'), self.onAuth)
        # Register commands

    def onAuth(self, event):
        client = event.client
        if client.bot:
            if client.cid == 1 or client.cid == "1":
                self.console.write("exec bot1.txt")
            elif client.cid == 2 or client.cid == "2":
                self.console.write("exec bot2.txt")
            elif client.cid == 3 or client.cid == "3":
                self.console.write("exec bot3.txt")
            elif client.cid == 4 or client.cid == "4":
                self.console.write("exec bot4.txt")
            elif client.cid == 5 or client.cid == "5":
                self.console.write("exec bot5.txt")
            elif client.cid == 6 or client.cid == "6":
                self.console.write("exec bot6.txt")
            elif client.cid == 7 or client.cid == "7":
                self.console.write("exec bot7.txt")
            elif client.cid == 8 or client.cid == "8":
                self.console.write("exec bot8.txt")
            elif client.cid == 9 or client.cid == "9":
                self.console.write("exec bot9.txt")
            elif client.cid == 10 or client.cid == "10":
                self.console.write("exec bot10.txt")
            elif client.cid == 11 or client.cid == "11":
                self.console.write("exec bot11.txt")
            elif client.cid == 12 or client.cid == "12":
                self.console.write("exec bot12.txt")
            elif client.cid == 13 or client.cid == "13":
                self.console.write("exec bot13.txt")
            elif client.cid == 14 or client.cid == "14":
                self.console.write("exec bot14.txt")
            elif client.cid == 15 or client.cid == "15":
                self.console.write("exec bot15.txt")
            elif client.cid == 16 or client.cid == "16":
                self.console.write("exec bot16.txt")
            elif client.cid == 17 or client.cid == "17": 
                self.console.write("exec bot17.txt")
            elif client.cid == 18 or client.cid == "18":
                self.console.write("exec bot18.txt")
            elif client.cid == 19 or client.cid == "19":
                self.console.write("exec bot19.txt")
            elif client.cid == 20 or client.cid == "20":
                self.console.write("exec bot20.txt")
        else:
            return