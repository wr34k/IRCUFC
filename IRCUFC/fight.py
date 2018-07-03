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
            self.IRC.privmsg(self.IRC.channel, "[{}] Hey {} you're already registered!".format( \
                self.IRC.mirc.color("!", self.IRC.mirc.colors.YELLOW), \
                self.IRC.mirc.color(nick, self.IRC.mirc.colors.YELLOW)) \
            )
            return
        else:
            self.fighters += [nick]

        if len(self.fighters) == 2:
            self.IRC.privmsg(self.IRC.channel, "[{}] Alright. {}, {}, let's fight!".format( \
                self.IRC.mirc.color("*", self.IRC.mirc.colors.GREEN), \
                self.IRC.mirc.color(self.fighters[0], self.IRC.mirc.colors.RED), \
                self.IRC.mirc.color(self.fighters[1], self.IRC.mirc.colors.BLUE)) \
            )
            self.state = 'fighters_ready'
        else:
            self.IRC.privmsg(self.IRC.channel, "[{}] Waiting for 2nd fighter...".format( \
                self.IRC.mirc.color("*", self.IRC.mirc.colors.GREEN)) \
            )


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
            self.IRC.privmsg(f.nick, "[{}] What is your next move? (Use {}action <action> to set your next move)".format(self.IRC.mirc.color("~", self.IRC.mirc.colors.BLUE), self.IRC.optkey))
            self.IRC.privmsg(f.nick, "[{}] Actions available: '{}'".format(self.IRC.mirc.color("*", self.IRC.mirc.colors.GREEN), "', '".join(self.get_next_avail_action(f.nick))))


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
                    self.IRC.privmsg(nick, "[{}] You already chose your next move!".format(self.IRC.mirc.color("!", self.IRC.mirc.colors.YELLOW)))
                    return

                if " ".join(action) in self.get_next_avail_action(nick):
                    f.nextAction = action
                    self.IRC.privmsg(nick, "[{}] Next move set!".format(self.IRC.mirc.color("*", self.IRC.mirc.colors.GREEN)))
                else:
                    self.IRC.privmsg(nick, "[{}] Move not recognized".format(self.IRC.mirc.color("!", self.IRC.mirc.colors.YELLOW)))

        done = True
        for f in self.fighters:
            if f.nextAction is None:
                done = False

        if done:
            self.performNextTurn()


    def getStatus(self, nick):
        if self.state == 'inactive':
            self.IRC.privmsg(nick, "[{}] Standby, waiting for a fight to start...".format(self.IRC.mirc.color("*", self.IRC.mirc.colors.GREEN)))
        elif self.state == 'waiting_fighter':
            self.IRC.privmsg(nick, "[{}] Waiting for 2nd opponent, type {}fight to register for the next fight!".format(self.IRC.mirc.color("*", self.IRC.mirc.colors.GREEN), self.IRC.optkey))
        else:
            for f in self.fighters:
                if f.nick == nick:
                    self.IRC.privmsg(nick, "[{}] Status for {} -> Current health: {} | Current stance: {} | Next action: {}".format(self.IRC.mirc.color("*", self.IRC.mirc.colors.GREEN), f.nick, int(f.hp), f.stance, f.nextAction))
                else:
                    self.IRC.privmsg(nick, "[{}] Status for {} -> Current health: {} | Current stance: {}".format(self.IRC.mirc.color("*", self.IRC.mirc.colors.GREEN), f.nick, int(f.hp), f.stance))


    def fightOver(self):
        winner = self.fighters[0] if self.fighters[1].hp <= 0 else self.fighters[1]
        looser = self.fighters[0] if self.fighters[0].hp <= 0 else self.fighters[1]

        winner.wins += 1
        looser.looses += 1

        self.shout("{}{}".format(self.IRC.mirc.BOLD, self.IRC.mirc.color("Fight is over.", self.IRC.mirc.colors.LIGHTGREY)))
        self.shout("{}{} won the fight against {} with {} hp left.".format( \
            self.IRC.mirc.BOLD,
            self.IRC.mirc.color(winner.nick, winner.colour), \
            self.IRC.mirc.color(looser.nick, looser.colour), \
            self.IRC.mirc.color(int(winner.hp), self.IRC.mirc.colors.GREEN) ) \
        )

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
            roll1 += 0.08
        else:
            roll2 += 0.08

        if roll1 > roll2:
            attacker = self.fighters[0]
            defender = self.fighters[1]
        else:
            attacker = self.fighters[1]
            defender = self.fighters[0]

        # self.IRC.log.info("{} rolled {} and {} rolled {}".format(self.fighters[0].nick, roll1, self.fighters[1].nick, roll2))

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
                    self.shout("{} Tryed to block {} but failed miserably!".format(self.IRC.mirc.color(defender.nick, defender.colour), defender.nextAction[1]))


                realdmg = (random.random() * dmg) + mindmg

                defender.hp -= realdmg

                if (random.random() * 100) < fallchance: # defender falls down?
                    defender.stance = 'ground'
                    falltxt = self.prettyTxt(attacker, defender, self.config['info']['stand2ground'])
                    self.shout("{}".format(falltxt))


        if defender.hp <= 0:
            self.shout("{}{} passed out.".format(self.IRC.mirc.BOLD, self.IRC.mirc.color(defender.nick, self.IRC.mirc.colors.YELLOW)))
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
        txt = txt.replace("%attacker%", "{}{}".format(self.IRC.mirc.BOLD, self.IRC.mirc.color(attacker.nick, attacker.colour)))
        txt = txt.replace("%defender%", "{}{}".format(self.IRC.mirc.BOLD, self.IRC.mirc.color(defender.nick, defender.colour)))
        return txt

    def shout(self, msg):
        for f in self.fighters:
            self.IRC.privmsg(f.nick, msg)
        self.IRC.privmsg(self.IRC.channel, msg)
