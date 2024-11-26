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
import b3.events
import b3.plugin
import random, string
import random as rand
from random import randint
from threading import Timer
import time

class MaprotatorPlugin(b3.plugin.Plugin):
    
    requiresConfigFile = False

    GAME_PATH = None

    global_nextmap = ""

    maps = {  #mapname + minbots
        'ut4_terrorism3_bots_d3mod' : 10,
        'ukraine' : 10,
        'ut4_maximus_v1_bots' : 10,
        'ut4_suburbs' : 10,
        'ut4_rip_release_gbots_d3mod' : 12,
        'ut4_crossing' : 10,
        'ut4_terrorism7_bots' : 10,
        'pm_zih_roof' : 12,
        'ut4_sparta_bots' : 10,
        'ut4_eagle' : 10,
        'mvdm08' : 8,
        'ut4_presidio_v8_d3bots' : 10,
        'ut4_metropolis_b2_bots' : 10,
        'ut4_dust2_v2' : 10,
        'ut4_purity_b4' : 10,
        'ut_laneway2_f43' : 10,
        'ut4_uptown' : 10,
        'ut4_terrorism8_bots' : 10,
        'ut4_hexagon_v1' : 10,
        'ut4_old_kingdom' : 10,
        'ut4_baku' : 10,
        'ut4_thingley' : 10,
        'ut4_granja_bots_d3mod' : 10,
        'ut4_unload_beta_d3bots' : 10,
        "wop_padship" : 10,
        "ut4_vypla" : 10,
        "ut4_nightmare_xmas" : 10,
        "Dangercity_f1" : 10,
        "ut_intermodal" : 16,
        "ut4_blitzkrieg2_bots_d3mod" : 10,
        "ut4_village_bots" : 10,
        "wop_padgarden_night_b4" : 10,
        "ut4_druglord_d3bots" : 10,
        "ut4_toys_release_d3mod" : 10,
        "q_1upxmas_bots" : 10,
        "ut4_wildwest_bots" : 10,
        "pom_bots_d3mod" : 10,
        "ut4_dtctribute_a5_bots" : 10,
        "ut4_reqbath_b1" : 10,
        "wop_padlibrary" : 10,
        "ut_forrest" : 10,
        "wop_padattic" : 10,
        "ut_laberinto_bots" : 10,
        "ut4_cathedral_bots" : 10,
        "ut4_gad_dom_d3mod" : 10,
        "ut4_alinosperch_a3_bots" : 10,
        "history_bots" : 10,
        "ut4_beijing_b3_bots" : 10,
        "ut4_casa_snow" : 10,
        "ut4_evil_circus_d3mod" : 10,
        "ut4_anikitown_v5" : 10,
        "ut4_guerrilla_bots" : 10,
        "ut4_sirkitbored_release_gbots" : 10,
        "ut4_treeway_bots_d3mod" : 10,
        "Cube01_d3bots" : 10,
        "ut4_horror" : 10,
        "ut4_skylift_release_dbots" : 10,
        "ut4_crazychristmas_bots" : 10,
        "ut4_battlefront_bots" : 10,
        "ut4_toxic" : 10,
        "ut4_corinthe_b2_bots" : 10,
        "wop_padkitchen" : 10,
        "ut4_aardtimes_www2" : 10,
        "ut4_warehouse_bots" : 10,
        "ut4_cambridge_fixed" : 10,
        "ut4_zement_b2_bots" : 10,
        'ut4_terrorism6_bots_d3mod' : 10,
        'ut4_venice_b7_bots' : 10,
        'ut4_suburbia_b9' : 10,
        'ut_castle' : 10,
        'ut4_turnpike' : 10,
        'ut4_oaks_b2_bots' : 10,
        'ut4_abbey' : 10,
        'ut4_streets_bots' : 10,
        'ut4_santorini_v9' : 10,
        'ut4_blitzkrieg_bots_d3mod' : 10,
        'ut4_cambodia_b6' : 10,
        'q_premiere_f43_bots' : 10,
        'chronic' : 10,
        'ut43_akroseum_r2' : 12,
        'ut4_terrorism4_bots' : 10,
        'ut4_swim' : 10,
        'ut4_subway' : 10,
        'ut4_village_classic_rc4_bots_d3mod' : 12,
        'ut4_paris_v2_bots' : 10,
        'simpsons_q3' : 10,
        'ut42_docks_bots' : 10
    }

    def onStartup(self):
        # Get admin plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # Something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return

        # Getting the current game path
        self.GAME_PATH = self.console.config.getpath('server', 'game_log').replace('games.log', "")

        # Register events
        self.registerEvent(self.console.getEventID('EVT_GAME_ROUND_START'), self.onRoundstart)
        self.registerEvent(self.console.getEventID('EVT_GAME_SCOREBOARD'), self.onRoundend) # This requires the updated iourt43 parser

        # Register commands
        self._adminPlugin.registerCommand(self, 'mapinfo', 0, self.cmd_mapinfo, 'nextmap')

    ####################################################################################################################
    #                                                                                                                  #
    #    Events                                                                                                        #
    #                                                                                                                  #
    ####################################################################################################################

    def onRoundstart(self, event):
        # Add a small wait here otherwise "status" from getCurrentMapname won't be available yet.
        time.sleep(3)

        currmap = self.getCurrentMapname()
        nextmap = random.choice(list(self.maps))

        self.global_nextmap = nextmap
        if nextmap in self.maps.keys():
          nextmap_botcount = self.maps[nextmap]
        else:
          nextmap_botcount = 10
        if currmap in self.maps.keys():
          botcount = self.maps[currmap]
        else:
          botcount = 10

        self.console.write('bot_minplayers %s' % botcount)
        self.setNextMap(nextmap)
        message = "^5Nextmap: ^6%s ^3with ^5[^6%s^5] ^2Bots" % (nextmap, nextmap_botcount)
        t = Timer(40, self.announceNextmap, (message, ))
        t.start()

    def onRoundend(self, event):
        nextmapname = self.console.getNextMap()
        message = "^5Nextmap: ^6%s ^3with ^5[^6%s^5] ^2Bots" % (nextmapname, self.maps[nextmapname])
        self.console.say(message)

    ####################################################################################################################
    #                                                                                                                  #
    #    Commands                                                                                                      #
    #                                                                                                                  #
    ####################################################################################################################

    def cmd_mapinfo(self, data, client, cmd=None):
        mapname = self.getCurrentMapname()
        self.console.say("^5Current map: ^6%s ^3with ^5[^6%s^5] ^2Bots" % (mapname, self.maps[mapname]))
        try:
            x = self.maps[self.global_nextmap]
        except:
            self.console.say("^5Nextmap ^1not available.")
        else:
            self.console.say("^5Nextmap: ^6%s ^3with ^5[^6%s^5] ^2Bots" % (self.global_nextmap, self.maps[self.global_nextmap]))

    ####################################################################################################################
    #                                                                                                                  #
    #    Functions                                                                                                     #
    #                                                                                                                  #
    ####################################################################################################################

    def getCurrentMapname(self):
        output = str(self.console.write('status'))
        return(output[output.find('map: ')+5:][:output[output.find('map: ')+5:].find('num')-1])

    def announceNextmap(self, message):
        self.console.say(message)

    def setNextMap(self,nextmap):
        self.console.write("g_nextmap %s"%nextmap)
        #fileloc = "%s/setnextmap_helper.txt" % self.GAME_PATH
        #with open(fileloc, "w") as file:
        #    file.write("g_nextmap %s" % self.global_nextmap)
        #self.console.write("exec setnextmap_helper.txt")
