# IRCUFC
**WORK IN PROGRESS**

IRC Game to let chatters having UFC like fights.


Connect to #IRCUFC @ Efnet and type !fight to register to the next fight


once 2 fighters will be registered, you'll reveice a list of actions possible for you to do in the next turn. (kick high, punch middle, ...)

Once a fighter have no hp left, the fight is over.


### How to run:

```
python3 main.py
```

### General Commands:
* **!fight** -- Register for the next fight
* **!status** -- Get current status of the fight (If sent as PM to the bot, you'll get more information like your next move)
* **!action** -- Register your next action (ex: !action kick high, !action block middle, !action standup)

### Admin Commands:
* **!cancel** -- Cancel the current fight




### More Info:
If both fighters are attacking at the same time, then the one who will hit is random. There's still an slight advantage to the last player having hit. Also, some attacks have more chance to fail, but those ones are usually more powerful.

Using 'block' with the right level (high, middle, low) will give you a great chance to block the next hit. If so, you won't loose HP, and you'll take the advantage for the next round.. Be careful though, if for instance you block high and your opponent attacks you low or middle, you'll have 100% chance of taking the hit (Except if the strike fails). Blocking chance depend on your stance.

There's a chance for fighters to fall down. In this case, hits will be much less powerful, and your opponent will do huge damage. If both fighters are on the ground, then one of them will be above the other. (The second fighter to fall will be above. Then, the one with the advantage will be above.) You'll have to use the '**!action standup**' command in order to .. stand up :)


**Shoutout to arab for the epoll(2) idea, and for [araboly](https://github.com/lalbornoz/araboly) which remains the best IRC game out there!**
