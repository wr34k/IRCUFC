#!/usr/bin/env python3

from fighter import Fighter
import random, json

CONFIG_FILE = "assets/config.json"

class Fight(object):
    def __init__(self, IRC):
        self.IRC = IRC
        self.state = 'inactive'
        self.fighters = []

        self.get_config()

    def get_config(self):
        with open(CONFIG_FILE, "r") as f:
            self.config = json.loads(f.read())

    def addFighter(self, nick):
        self.state = 'waiting_fighter'
        if nick in self.fighters:
            self.IRC.privmsg(self.IRC.channel, "Hey {} you're already registered!".format(nick))
            return
        else:
            self.fighters += [nick]

        if len(self.fighters) == 2:
            self.IRC.privmsg(self.IRC.channel, "Alright. {}, {}, let's fight!".format(self.fighters[0], self.fighters[1]))
            self.state = 'fighters_ready'
        else:
            self.IRC.privmsg(self.IRC.channel, "Waiting for 2nd fighter...")


    def startFight(self):
        self.state = 'starting_fight'

        self.fighters[0] = Fighter(self.fighters[0], self.IRC.mirc.colors.RED)
        self.fighters[1] = Fighter(self.fighters[1], self.IRC.mirc.colors.BLUE)


        # who start?
        roll1 = roll2 = 0
        while roll1 == roll2:
            roll1 = random.random()
            roll2 = random.random()


        if roll1 > roll2:
            self.fighters[0].advantage = True
        else:
            self.fighters[1].advantage = True

        self.print_fighters_action()


    def print_fighters_action(self):
        self.state = 'waiting_fighters_action'

        for f in self.fighters:
            self.IRC.privmsg(f.nick, "What is your next move?")
            self.IRC.privmsg(f.nick, "Actions available: '{}'".format("', '".join(self.get_next_avail_action(f.nick))))


    def get_next_avail_action(self, nick): # TODO: fix this mess.
        f = self.fighters[0] if self.fighters[0].nick == nick else self.fighters[1]
        e = self.fighters[0] if self.fighters[1].nick == nick else self.fighters[1]
        cmds = []
        for i in self.config['moves'][f.stance]:
            if i == 'standup':
                cmds += [i]
            elif i == 'punch' and e.stance == 'ground':
                pass
            else:
                for j in self.config['moves'][f.stance][i]:
                    cmds += ["{} {}".format(i, j)]

        return cmds

    def set_next_action(self, nick, action):
        for f in self.fighters:
            if f.nick == nick:
                if f.nextAction is not None:
                    self.IRC.privmsg(nick, "You already chose your next move!")
                    return

                if " ".join(action) in self.get_next_avail_action(nick):
                    f.nextAction = action
                    self.IRC.privmsg(nick, "Next move set!")
                else:
                    self.IRC.privmsg(nick, "Move not recognized")

        done = True
        for f in self.fighters:
            if f.nextAction is None:
                done = False

        if done:
            self.performNextTurn()


    def getStatus(self, nick):
        if self.state == 'inactive':
            self.IRC.privmsg(nick, "Standby, waiting for a fight to start...")
        elif self.state == 'waiting_fighter':
            self.IRC.privmsg(nick, "Waiting for 2nd opponent, type {}fight to register for the next fight!".format(self.IRC.optkey))
        else:
            for f in self.fighters:
                if f.nick == nick:
                    self.IRC.privmsg(nick, "Status for {} -> Current health: {} | Current stance: {} | Next action: {}".format(f.nick, f.hp, f.stance, f.nextAction))
                else:
                    self.IRC.privmsg(nick, "Status for {} -> Current health: {} | Current stance: {}".format(f.nick, f.hp, f.stance))


    def fightOver(self):
        winner = self.fighters[0] if self.fighters[1].hp <= 0 else self.fighters[1]
        looser = self.fighters[0] if self.fighters[0].hp <= 0 else self.fighters[1]

        winner.wins += 1
        looser.looses += 1

        self.shout("\x02\x0315Fight is over.")
        self.shout("\x02\x03{}{}\x0f won the fight against \x02\x03{}{}\x0f with \x02\x0303{}\x0f hp left.".format(winner.colour, winner.nick, looser.colour, looser.nick, int(winner.hp)))

        self.state = 'inactive'
        self.fighters = []

    def performNextTurn(self):
        self.state = 'processing_turn'

        self.attack()

        if self.state == 'fight_over':
            self.fightOver()
            return

        for f in self.fighters:
            f.nextAction = None

        self.print_fighters_action()



    def get_next_move_data(self, f, e):
        dmg         = self.config['moves'][f.stance][f.nextAction[0]][f.nextAction[1]][e.stance]['dmgidx']
        mindmg      = self.config['moves'][f.stance][f.nextAction[0]][f.nextAction[1]][e.stance]['mindmg']
        blockidx    = self.config['moves'][f.stance][f.nextAction[0]][f.nextAction[1]][e.stance]['blockidx']
        fallchance  = self.config['moves'][f.stance][f.nextAction[0]][f.nextAction[1]][e.stance]['fallchance']  \
            if 'fallchance' in self.config['moves'][f.stance][f.nextAction[0]][f.nextAction[1]][e.stance] \
                else 0
        standchance  = self.config['moves'][f.stance][f.nextAction[0]][f.nextAction[1]][e.stance]['standchance']  \
            if 'standchance' in self.config['moves'][f.stance][f.nextAction[0]][f.nextAction[1]][e.stance] \
                else 0

        texts    = self.config['moves'][f.stance][f.nextAction[0]][f.nextAction[1]][e.stance]['text']

        return dmg, mindmg, blockidx, fallchance, standchance, texts

    def attack(self):

        roll1 = roll2 = 0
        while roll1 == roll2:
            roll1 = random.random()
            roll2 = random.random()


        if self.fighters[0].advantage:
            roll1 += 0.15
        else:
            roll2 += 0.15

        if roll1 > roll2:
            attacker = self.fighters[0]
            defender = self.fighters[1]
        else:
            attacker = self.fighters[1]
            defender = self.fighters[0]

        if attacker.nextAction[0] == 'block' and defender.nextAction[0] != 'block':
            tmp = attacker
            attacker = defender
            defender = tmp
        elif attacker.nextAction[0] == 'block' and defender.nextAction[0] == 'block':
            self.shout("Both fighters are trying to block at the same time, resulting in a completely retarded action...")
            return

        attacker.advantage = True
        defender.advantage = False

        if attacker.nextAction[0] == 'standup':
            standchance = self.config['moves'][attacker.stance]['standup'][defender.stance]['chance']
        else:
            dmg, mindmg, blockidx, fallchance, standchance, texts = self.get_next_move_data(attacker, defender)

            txt = self.prettyTxt(attacker, defender, texts)
            self.shout("{}".format(txt))

            blockchance = 0
            if defender.nextAction[0] == 'block':
                if defender.nextAction[1] == attacker.nextAction[1]:
                    blockchance     = self.config["moves"][defender.stance][defender.nextAction[0]][defender.nextAction[1]]["chance"]
                    blocktxts       = self.config["moves"][defender.stance][defender.nextAction[0]][defender.nextAction[1]]["text"]


            if  (random.random() * 100) < blockchance * (blockidx / 100):
                blocktxt = self.prettyTxt(attacker, defender, blocktxts)
                self.shout("{}".format(blocktxt))
            else:
                if defender.nextAction[0] == 'block':
                    self.shout("{} Tryed to block {} but failed miserably!".format(defender.nick, defender.nextAction[1]))


                realdmg = (random.random() * dmg) + mindmg

                defender.hp -= realdmg

                if (random.random() * 100) < fallchance: # defender falls down?
                    defender.stance = 'ground'
                    falltxt = self.prettyTxt(attacker, defender, self.config['info']['stand2ground'])
                    self.shout("{}".format(falltxt))


        if defender.hp <= 0:
            self.IRC.privmsg(self.IRC.channel, "\x02\x0305{} passed out.\x0f".format(defender.nick))
            self.state = "fight_over"
            return

        if defender.hp < 25 and defender.first_time_lowhp:
            defender.first_time_lowhp=False
            lowhptxt = self.prettyTxt(attacker, defender, self.config['info']['lowhp'])
            self.shout("{}".format(lowhptxt))


        if attacker.nextAction[0] == 'standup': # attacker gets up?
            if (random.random() * 100) < standchance: # DO you get up?
                attacker.stance = 'stand'
                standtxt = self.prettyTxt(attacker, defender, self.config['info']['ground2stand'])
                self.shout("{}".format(standtxt))



    def prettyTxt(self, attacker, defender, txtlist):
        txt = txtlist[random.randint(0, len(txtlist)-1)]
        txt = txt.replace("%attacker%", "\x02\x03{}{}\x0f".format(attacker.colour, attacker.nick))
        txt = txt.replace("%defender%", "\x02\x03{}{}\x0f".format(defender.colour, defender.nick))
        return txt

    def shout(self, msg):
        for f in self.fighters:
            self.IRC.privmsg(f.nick, msg)
        self.IRC.privmsg(self.IRC.channel, msg)
