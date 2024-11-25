__author__ = 'donna30'
__version__ = '1.5'

import b3
import re
import b3.events
import b3.plugin
import random
import time
from threading import Timer

class Active_vote(object):
    active = 'no'

class Vote_count(object):
    yes = 0
    no = 0

class Round_end_data(object):
    fraglimit = None
    timelimit = None

class Round_start_data(object):
    fraglimit = 80
    timelimit = 10

class Time1(object):
    time1 = 30

class CustomvotePlugin(b3.plugin.Plugin):
    requiresConfigFile = False

    def onStartup(self):
        self.active_vote = Active_vote()
        self.vote_count = Vote_count()
        self.end_data = Round_end_data()
        self.reset_data = Round_start_data()

        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            self.error('Could not find admin plugin')
            return

        self._adminPlugin.registerCommand(self, 'callvote', 0, self.cmd_vote, 'cv')

        self.registerEvent('EVT_CLIENT_SAY')
        self.registerEvent('EVT_CLIENT_TEAM_SAY')
        self.registerEvent('EVT_GAME_ROUND_START')
        self.registerEvent('EVT_GAME_ROUND_END')
        self.registerEvent(('EVT_CLIENT_JOIN'))

    def onEvent(self, event):
        if event.type == self.console.getEventID('EVT_CLIENT_SAY') or event.type == self.console.getEventID('EVT_CLIENT_TEAM_SAY'):
            self.onSay(event.data, event.client)
        elif event.type == self.console.getEventID('EVT_GAME_ROUND_START'):
            self.on_round_start()
        elif event.type == self.console.getEventID('EVT_GAME_ROUND_END'):
            self.on_round_end()
        elif event.type == self.console.getEventID('EVT_CLIENT_JOIN'):
            client = event.client
            self.checkauthed(client)

    def on_round_end(self):
        if Round_end_data.fraglimit is not None:
            if Round_end_data.timelimit is not None:
                self.console.write('fraglimit %s' % Round_end_data.fraglimit)
                self.console.write('timelimit %s' % Round_end_data.timelimit)
                Round_end_data.timelimit = None
                Round_end_data.fraglimit = None
        else:
            self.console.write('fraglimit %s' % Round_start_data.fraglimit)
            self.console.write('timelimit %s' % Round_start_data.timelimit)

    def on_round_start(self):
        self.console.write('g_gametype 0')

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

    def onSay(self, text, client):
        text2 = text
        text = ' ' + text + ' '
        if client.isvar(self, 'voted'):
            return
        if Active_vote.active == 'yes':
            if (text2 == "+") or (text2 == "yes"):
                client.setvar(self, 'voted')
                Vote_count.yes = Vote_count.yes + 1
                client.message('^5Voted ^2Yes')
                t = Timer(30, self.remove_vote_var, (client, ))
                t.start()
            elif (text2 == "-") or (text2 == "no"):
                client.setvar(self, 'voted')
                Vote_count.no = Vote_count.no + 1
                client.message('^5Voted ^1No')
                t = Timer(30, self.remove_vote_var, (client, ))
                t.start()
        else:
            return

    def remove_vote_var(self, client):
        client.delvar(self, 'voted')

    def announcetoclients(self):
        for client in self.console.clients.getList():
            if client.bot:
                return
            else:
                client.message("^3Type ^2+ ^3or ^2yes ^3in the chat to vote ^2YES")
                client.message("^3Type ^1- ^3or ^2no ^3in the chat to vote ^1NO")
        self.console.write("bigtext '^3A ^2VOTE ^3has been called!'")

    def cmd_vote(self, data, client, cmd=None):
        last = client.var(self, 'delay_callvote', 0).value
        if (self.console.time() - last) < 300:
            client.message('You can only use this command every 2 minutes')
            return
        isauthedstatus = client.var(self, 'isauthed').value
        if isauthedstatus is False:
            client.message('^3You need to be ^2authed ^3 in order to buy a ^6chatcolour')
            client.message('^3To auth yourself type ^2!authme')
            return
        handler = self._adminPlugin.parseUserCmd(data)
        votetype = handler[0]
        if not votetype:
            if client.maxLevel <= 15:
                client.message('^3Type ^2!cv cyclemap')
                return
            else:
                client.message('^3Type ^2!cv FFA/CTF/TDM/CYCLEMAP')
                return
        if Active_vote.active == 'yes':
            self.debug('Active vote - skipping')
        else:
            if (votetype == "FFA") or (votetype == "ffa"):
                if client.maxLevel <= 15:
                    return
                vote_type = 'ffa'
                Active_vote.active = 'yes'
                self.romve_time()
                self.bigtext_vote(vote_type)
                self.announcetoclients()
                client.setvar(self, 'delay_callvote', self.console.time())

            elif (votetype == "CTF") or (votetype == "ctf") or (votetype == "capture") or (votetype == "Capture"):
                if client.maxLevel <= 15:
                    return
                vote_type = 'ctf'
                Active_vote.active = 'yes'
                self.romve_time()
                self.bigtext_vote(vote_type)
                self.announcetoclients()
                self.console.say("^3Type: ^1- ^3or ^2no ^3in the chat to vote ^1NO")
                client.setvar(self, 'delay_callvote', self.console.time())

            elif (votetype == "TDM") or (votetype == "tdm"):
                if client.maxLevel <= 15:
                    return
                vote_type = 'tdm'
                Active_vote.active = 'yes'
                self.romve_time()
                self.bigtext_vote(vote_type)
                self.announcetoclients()
                client.setvar(self, 'delay_callvote', self.console.time())
            
            elif (votetype == 'cycle') or (votetype == "cyclemap"):
                vote_type = 'cycle'
                Active_vote.active = 'yes'
                self.romve_time()
                self.bigtext_vote(vote_type)
                self.announcetoclients()
                client.setvar(self, 'delay_callvote', self.console.time())
            else:
                client.message('^3Something went wrong!')

    def bigtext_vote(self, vote_type):
        if vote_type == 'ffa':
            self.console.write('bigtext "^3Change ^5gametype ^3to ^6FFA? ^2Yes: ^7[^2%s^7] ^1No: ^7[^1%s^7] (%s)"' % (Vote_count.yes, Vote_count.no, Time1.time1))
            self.display_vote(vote_type)
        elif vote_type == 'ctf':
            self.console.write('bigtext "^3Change ^5gametype ^3to ^6CTF? ^2Yes: ^7[^2%s^7] ^1No: ^7[^1%s^7] (%s)"' % (Vote_count.yes, Vote_count.no, Time1.time1))
            self.display_vote(vote_type)
        elif vote_type == 'tdm':
            self.console.write('bigtext "^3Change ^5gametype ^3to ^6TDM? ^2Yes: ^7[^2%s^7] ^1No: ^7[^1%s^7] (%s)"' % (Vote_count.yes, Vote_count.no, Time1.time1))
            self.display_vote(vote_type)
        elif vote_type == 'cycle':
            nextmap = self.console.getNextMap()
            self.console.write('bigtext "^1Cycle ^3map to ^5%s? ^2Yes: ^7[^2%s^7] ^1No: ^7[^1%s^7] (%s)"' % (nextmap, Vote_count.yes, Vote_count.no, Time1.time1))
            self.display_vote(vote_type)

    def bigtext_vote_display(self, vote_type):
        if vote_type == 'ffa':
            self.console.write('bigtext "^3Change ^5gametype ^3to ^6FFA? ^2Yes: ^7[^2%s^7] ^1No: ^7[^1%s^7] (%s)"' % (Vote_count.yes, Vote_count.no, Time1.time1))
        elif vote_type == 'ctf':
            self.console.write('bigtext "^3Change ^5gametype ^3to ^6CTF? ^2Yes: ^7[^2%s^7] ^1No: ^7[^1%s^7] (%s)"' % (Vote_count.yes, Vote_count.no, Time1.time1))
        elif vote_type == 'tdm':
            self.console.write('bigtext "^3Change ^5gametype ^3to ^6TDM? ^2Yes: ^7[^2%s^7] ^1No: ^7[^1%s^7] (%s)"' % (Vote_count.yes, Vote_count.no, Time1.time1))
        elif vote_type == 'cycle':
            nextmap = self.console.getNextMap()
            self.console.write('bigtext "^1Cycle ^3map to ^5%s? ^2Yes: ^7[^2%s^7] ^1No: ^7[^1%s^7] (%s)"' % (nextmap, Vote_count.yes, Vote_count.no, Time1.time1))

    def bigtext_vote_result(self, vote_type):
        if Vote_count.no <= Vote_count.yes:
            nextmapname = self.console.getNextMap()
            if vote_type == 'ffa':
                self.console.write('bigtext "^5Voting results: ^2Yes: ^7[^2%s^7] ^1No: ^7[^1%s^7]"' % (Vote_count.yes, Vote_count.no))
                self.console.write('g_gametype 0')
                self.console.write('say "^5Nextmap: ^2%s ^7- ^5Gametype: ^6FFA"' %  nextmapname)
                self.clear_data()
                Round_end_data.fraglimit = 80
                Round_end_data.timelimit = 10
            elif vote_type == 'ctf':
                self.console.write('bigtext "^5Voting results: ^2Yes: ^7[^2%s^7] ^1No: ^7[^1%s^7]"' % (Vote_count.yes, Vote_count.no))
                self.console.write('g_gametype 7')
                self.console.write('say "^5Nextmap: ^2%s ^7- ^5Gametype: ^6CTF"' %  nextmapname)
                self.clear_data()
                Round_end_data.fraglimit = 0
                Round_end_data.timelimit = 13
            elif vote_type == 'tdm':
                self.console.write('bigtext "^5Voting results: ^2Yes: ^7[^2%s^7] ^1No: ^7[^1%s^7]"' % (Vote_count.yes, Vote_count.no))
                self.console.write('g_gametype 3')
                self.console.write('say "^5Nextmap: ^2%s ^7- ^5Gametype: ^6TDM"' %  nextmapname)
                self.clear_data()
                Round_end_data.fraglimit = 130
                Round_end_data.timelimit = 10

        else:
            if vote_type == 'ffa':
                self.console.write('bigtext "^5Voting results: ^2Yes: ^7[^2%s^7] ^1No: ^7[^1%s^7]"' % (Vote_count.yes, Vote_count.no))
                self.console.say('^1Vote failed.')
                self.clear_data()
            elif vote_type == 'ctf':
                self.console.write('bigtext "^5Voting results: ^2Yes: ^7[^2%s^7] ^1No: ^7[^1%s^7]"' % (Vote_count.yes, Vote_count.no))
                self.console.say('^1Vote failed.')
                self.clear_data()
            elif vote_type == 'tdm':
                self.console.write('bigtext "^5Voting results: ^2Yes: ^7[^2%s^7] ^1No: ^7[^1%s^7]"' % (Vote_count.yes, Vote_count.no))
                self.console.say('^1Vote failed.')
                self.clear_data()

    def clear_data(self):
        Active_vote.active = 'no'
        Vote_count.yes = 0
        Vote_count.no = 0
        Time1.time1 = 30

    def romve_time(self):
        for delay in range(0, 30, 1):
            Timer(delay + 1, self.timer1).start()

    def timer1(self):
        if Time1.time1 == 0:
            return
        else:
            Time1.time1 = Time1.time1 - 1

    def display_vote(self, vote_type):
        timer_1 = Timer(2, self.bigtext_vote_display, (vote_type, ))
        timer_1.start()
        timer_2 = Timer(4, self.bigtext_vote_display, (vote_type, ))
        timer_2.start()
        timer_3 = Timer(6, self.bigtext_vote_display, (vote_type, ))
        timer_3.start()
        timer_4 = Timer(8, self.bigtext_vote_display, (vote_type, ))
        timer_4.start()
        timer_5 = Timer(10, self.bigtext_vote_display, (vote_type, ))
        timer_5.start()
        timer_6 = Timer(12, self.bigtext_vote_display, (vote_type, ))
        timer_6.start()
        timer_7 = Timer(14, self.bigtext_vote_display, (vote_type, ))
        timer_7.start()
        timer_8 = Timer(16, self.bigtext_vote_display, (vote_type, ))
        timer_8.start()
        timer_9 = Timer(18, self.bigtext_vote_display, (vote_type, ))
        timer_9.start()
        timer_10 = Timer(20, self.bigtext_vote_display, (vote_type, ))
        timer_10.start()
        timer_11 = Timer(22, self.bigtext_vote_display, (vote_type, ))
        timer_11.start()
        timer_12 = Timer(24, self.bigtext_vote_display, (vote_type, ))
        timer_12.start()
        timer_13 = Timer(26, self.bigtext_vote_display, (vote_type, ))
        timer_13.start()
        timer_14 = Timer(28, self.bigtext_vote_display, (vote_type, ))
        timer_14.start()
        timer_15 = Timer(30, self.bigtext_vote_result, (vote_type, ))
        timer_15.start()
