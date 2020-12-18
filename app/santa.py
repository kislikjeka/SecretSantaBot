import random
import datetime


class Person:
    def __init__(self, name, wish, invalid_matches):
        self.name = name
        self.wish = wish
        self.invalid_matches = invalid_matches

    def __str__(self):
        return "%s <%s>" % (self.name, self.email)


class Pair:
    def __init__(self, giver, reciever):
        self.giver = giver
        self.reciever = reciever

    def __str__(self):
        return "%s ---> %s" % (self.giver.name, self.reciever.name)


class Santa:
    def choose_reciever(giver, recievers):
        choice = random.choice(recievers)
        if choice.name in giver.invalid_matches or giver.name == choice.name:
            if len(recievers) is 1:
                raise Exception("Only one reciever left, try again")
            return choose_reciever(giver, recievers)
        else:
            return choice

    def create_pairs(g, r):
        givers = g[:]
        recievers = r[:]
        pairs = []
        for giver in givers:
            try:
                reciever = self.choose_reciever(giver, recievers)
                recievers.remove(reciever)
                pairs.append(Pair(giver, reciever))
            except:
                return create_pairs(g, r)
        return pairs
