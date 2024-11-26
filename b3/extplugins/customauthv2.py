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
__version__ = '1.6'

import b3
import re
import b3.events
import b3.plugin
import requests
#import ipinfo

class Customauthv2Plugin(b3.plugin.Plugin):
    requiresConfigFile = False

    #Getting Plugin admin (cannot register commands without it)
    def onStartup(self):
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            self.error('Could not find admin plugin')
            return

        # Registering events
        self.registerEvent(self.console.getEventID('EVT_CLIENT_CONNECT'), self.onConnect)
        self.registerEvent(self.console.getEventID('EVT_CLIENT_JOIN'), self.onChange)
        # Registering commands
        self._adminPlugin.registerCommand(self, 'auth', 0, self.cmd_cauth)
        self._adminPlugin.registerCommand(self, 'forceauthupdate', 100, self.cmd_forceauthupdate)

    def onConnect(self, event):
        client = event.client
        self.check_data(client)
        self.checkifauthed(client)

    def onChange(self, event):
        client = event.client
        self.check_data(client)
        self.checkifauthed(client)

    def checkifauthed(self, client):
        if self.checkauthed(client) is False:
            client.setvar(self, 'isauthed', False)
        else:
            client.setvar(self, 'isauthed', True)

    def checkauthed(self, client):
        cursor = self.console.storage.query('SELECT * FROM isauthed WHERE iduser = %s' % client.id)
        if cursor.EOF:
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def get_auth_tag(self, client):
        if not client.pbid:
            return
        else:
            player_page=requests.get("https://www.urbanterror.info/members/profile/%s/" % client.pbid).content
            try:
                auth = player_page.split('<h2><span class="userTag start">')[1].lstrip().split('</span><span class="userName">')[0]
            except:
                auth = " "
                return(auth)
            else:
                return(auth)

    def get_ip_information(self, ip):
        #access_token = 'get ur own from ipinfo'
        #handler = ipinfo.getHandler(access_token)
        #ip_address = '%s' % ip
        #details = handler.getDetails(ip_address)
        #country = details.country
        country = 'XXX'
        return(country)

    def get_client_ip(self, client):
        data = self.console.write('forcecvar %s something something' % client.cid)
        ip2 = data.split("ip\\")[1].lstrip().split('\\something\\something')[0]
        ip = ip2.split(':')[0]
        return(ip)

    def check_data(self, client):
        if client.bot:
            self.debug('Bot')
        else:
            self.debug('Checking if client has an auth')
            if not client.pbid:
                self.debug('Client does not have an auth, setting default auth with country tag')
                ip = self.get_client_ip(client)
                country_short = self.get_ip_information(ip)
                self.console.write('changeauth %s "^7--- ^9(%s)"' % (client.cid, country_short))
            else:
                cursor = self.console.storage.query('SELECT * FROM customauth WHERE iduser = %s' % client.id)
                if cursor.EOF:
                    ip = self.get_client_ip(client)
                    country_short = self.get_ip_information(ip)
                    clan_tag = self.get_auth_tag(client)
                    cursor = self.console.storage.query('INSERT INTO customauth (iduser, country_short, clan_tag, counter) VALUES (%s , "%s", "%s", %s)' % (client.id, country_short, clan_tag, 10))
                    cursor.close()
                    if client.maxLevel >= 100:
                        self.update_auth_admin(client)
                    elif client.maxLevel == 80:
                        self.update_auth_mod(client)
                    else:
                        self.update_auth(client)
                else:
                    try: counter = int(cursor.getValue('counter'))
                    except: counter = 0 
                    if counter == 1:
                        cursor = self.console.storage.query('DELETE FROM customauth WHERE iduser = %s' % client.id)
                        cursor.close()
                        self.check_data(client)
                    else:
                        cursor = self.console.storage.query('UPDATE customauth SET counter = %s WHERE iduser = %s' % (counter - 1, client.id))
                        cursor.close()
                        if client.maxLevel >= 100:
                            self.update_auth_admin(client)
                        elif client.maxLevel == 80:
                            self.update_auth_mod(client)
                        else:
                            self.update_auth(client)
                cursor.close()

    def update_auth(self, client):
        cursor = self.console.storage.query('SELECT * FROM customauth WHERE iduser = %s' % client.id)
        country_short = str(cursor.getValue('country_short'))
        clan_tag = str(cursor.getValue('clan_tag'))
        cursor.close()
        isauthedstatus = client.var(self, 'isauthed').value
        if client.maxLevel == 80:
            self.update_auth_mod(client)
            return
        if isauthedstatus is True:
            self.console.write('changeauth %s "^3%s^7%s ^2Auth^9(%s)"' % (client.cid, clan_tag, client.pbid, country_short))
        else:
            self.console.write('changeauth %s "^3%s^7%s ^9(%s)"' % (client.cid, clan_tag, client.pbid, country_short))

    def update_auth_admin(self, client):
        isauthedstatus = client.var(self, 'isauthed').value
        cursor = self.console.storage.query('SELECT * FROM customauth WHERE iduser = %s' % client.id)
        country_short = str(cursor.getValue('country_short'))
        clan_tag = str(cursor.getValue('clan_tag'))
        cursor.close()
        self.console.write('changeauth %s "^3%s^7%s^1(Owner)^9(%s)"' % (client.cid, clan_tag, client.pbid, country_short))

    def update_auth_mod(self, client):
        cursor = self.console.storage.query('SELECT * FROM customauth WHERE iduser = %s' % client.id)
        clan_tag = str(cursor.getValue('clan_tag'))
        country_short = str(cursor.getValue('country_short'))
        cursor.close()
        self.console.write('changeauth %s "^3%s^7%s^3(Admin)^9(%s)"' % (client.cid, clan_tag, client.pbid, country_short))
    
    def cmd_forceauthupdate(self, data, client, cmd=None):
        for client in self.console.clients.getList():
            self.checkifauthed(client)
            self.check_data(client)

    def cmd_cauth(self, data, client, cmd=None):
        isauthedstatus = client.var(self, 'isauthed').value
        last = client.var(self, 'delay_auth', 0).value
        if (self.console.time() - last) < 120:
            client.message('^3You can only use this command every 2 minutes')
        else:
            ip = self.get_client_ip(client)
            country_short = self.get_ip_information(ip)
            if isauthedstatus is True:
                self.console.write('changeauth %s "^7%s ^2Authed^9(%s)"' % (client.cid, client.name, country_short))
                client.message('^5Auth ^3changed successfully')
                client.setvar(self, 'delay_auth', self.console.time())
            else:
                self.console.write('changeauth %s "^7%s ^9(%s)"' % (client.cid, client.name, country_short))
                client.message('^5Auth ^3changed successfully')
                client.setvar(self, 'delay_auth', self.console.time())
