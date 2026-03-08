class Statistics:
    def __init__(self,highestbalance:int=0,transactions:int=0,spent:int=0,totalearned:int=0,
                 lostgambling:int=0,gainedgambling:int=0,heads:int=0,tails:int=0) -> None:
        self.highestbalance:int  = highestbalance if highestbalance else 0 
        self.transactions:int    = transactions if transactions else 0
        self.spent:int           = spent if spent else 0
        self.totalearned:int     = totalearned if totalearned else 0
        self.lostgambling:int    = lostgambling  if lostgambling else 0
        self.gainedgambling:int  = gainedgambling if gainedgambling else 0
        self.heads:int           = heads  if heads else 0
        self.tails:int           = tails if tails else 0

    def __repr__(self):
        return f"(Statistics highestbalance = '{self.highestbalance}', transactions = {self.transactions}\
, spent = {self.spent}, totalearned = {self.totalearned}, lostgambling = {self.lostgambling}, gainedgambling =\
 {self.gainedgambling}, heads = {self.heads}, tails = {self.tails})"
    def __eq__(self, other):
        return self.highestbalance == other.higherbalance and self.transactions == other.transactions and \
            self.spent == other.spent and self.totalearned == other.totalearned and self.lostgambling == other.lostgambling and \
            self.gainedgambling == other.gainedgambling and self.heads == other.heads and self.tails == other.tails


class User:
    def __init__(self, uid: int = 0, balance: int = 0, statistics: Statistics = Statistics()) -> None:
        self.uid: int                 = uid
        self.balance: int             = balance
        self.statistics: Statistics   = statistics
    
    def __repr__(self):
        return f'(User uid = {self.uid}, balance = {self.balance}, statistics = {self.statistics})'
    def __eq__(self, other):
        return self.uid == other.uid
    