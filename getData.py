from pymongo import MongoClient
from random import randint

client = MongoClient('mongodb://localhost:27017/')
db = client.test
collection = db.zak
count = collection.find().count()

# generate small db
# db.zakupki.find({}).limit(228113).forEach(function(x){db.zak.insert(x)})


def GetOrderNames(amount=None):
    if amount is None:
        amount = count
    results = collection.find({}, {"orderName": 1})

    for _ in range(amount):
        n = results.next()
        yield n['orderName'].encode('utf-8')

def GetLots(amount=None):
    if amount is None:
        amount = count
    results = collection.find({}, {"lots.lot.subject": 1})
    for _ in range(amount):
        n = results.next()
        yield n["lots"]["lot"]["subject"].encode("utf-8")


def GetOrderNamesRandom(amount):
    for _ in range(amount):
        randInt = randint(1, amount)
        n = collection.find({}, {"orderName": 1}).limit(-1).skip(randInt).next()
        yield n['orderName'].encode('utf-8')


def GetLotsRandom(amount):
    for _ in range(amount):
        randInt = randint(1, count)
        n = collection.find({}, {"lots.lot.subject": 1}).limit(-1).skip(randInt).next()
        yield n["lots"]["lot"]["subject"].encode("utf-8")

def GetRandomItem():
    randInt = randint(1, count)
    result = collection.find().limit(-1).skip(randInt).next()
    return result

#f = open("OrderNames.txt", "w")
#results = collection.find({}, {"orderName": 1, "id": 1})
#for _ in range(count):
#    n = results.next()
#    idQ = str(n["id"])
#    s = n["orderName"].encode("utf-8").strip().replace("""
#""", "</br>")
#    f.write(idQ+"\t"+s+"\n")
#
#f = open("Lots.txt", "w")
#
#results = collection.find({}, {"lots.lot.subject": 1, "id": 1})
#for _ in range(count):
#    n = results.next()
#    idQ = str(n["id"])
#    s = n["lots"]["lot"]["subject"].encode("utf-8").strip().replace("""
#""", "</br>")
#    f.write(idQ+"\t"+s+"\n")








