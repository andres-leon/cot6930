import snap
import time
import statistics
import random


copurchasingfile = "copurchased.txt"
recommendedfile = "recommended.txt"

my_text = open(copurchasingfile, "r")

ids_with_recom = {}
toList = list()
prev_from_id = 0

with my_text:
   line = my_text.readline()
   line = line.strip()
   while line != '':
        linelist = line.split('\t')
        curr_from_id = int(linelist[0])
        curr_to_id = int(linelist[1])

        if curr_from_id == prev_from_id:
            # same node
            toList.append(curr_to_id)

        else:
            # new node. save prev node data
            finlist = list()
            for eachitm in toList:  # deep list copy
                finlist.append(eachitm)

            ids_with_recom[prev_from_id] = finlist
            del toList[:]
            # print("node " + str(prev_from_id) + " has nodes " + str(ids_with_recom[prev_from_id]))
            toList.append(curr_to_id)  # add the current to item to the new node

        prev_from_id = curr_from_id
        line = my_text.readline()
        line = line.strip()

idlist = list()
totlconnlst = list()
numofconnectionlist = list()
print("ids_with_recom has been loaded with " + str(len(ids_with_recom)) + " nodes.")
totalconnections = 0
maxnumofconnections = 0
prevnumofconnections = 0
currnumofconnections = 0
idwithmaxconnections = -1
for id, simlist in ids_with_recom.iteritems():
    idlist.append(id)
    totlconnlst.extend(simlist)
    currnumofconnections = len(simlist)
    numofconnectionlist.append(currnumofconnections)
    totalconnections = totalconnections + currnumofconnections
    if currnumofconnections >= maxnumofconnections:
        maxnumofconnections = currnumofconnections
        idwithmaxconnections = id
#
# print("average connections per node: " + str(float(totalconnections / len(ids_with_recom))))
# print("max connections: " + str(maxnumofconnections) + ". id is " + str(idwithmaxconnections))
# print("standard deviation of all number of connections: " + str(statistics.pstdev(numofconnectionlist)))
# print("median: " + str(statistics.median(numofconnectionlist)))
# print("mean: " + str(statistics.mean(numofconnectionlist)))
# print ("total: " + str(len(list(set(totlconnlst)))))
#
# count = 0
# while count < 11:
#     print("count of " + str(count) + ": " + str(numofconnectionlist.count(count)))
#     count += 1


# find if connected items are themselves connected to others
# currid = -1
# simidsnotconnected = list()
# for id, simlist in ids_with_recom.iteritems():
#     for recommid in simlist:
#         if recommid in ids_with_recom:
#             continue
#         else:
#             # not found
#             simidsnotconnected.append(recommid)
#
# print("recommended ids not linked to other items: ")
# for itm in  list(set(simidsnotconnected)):
#     print itm

#random graph
f = open("0302-random-graph2.txt", 'w')
allids = list()
allids = idlist
allids.extend(totlconnlst) # all the ids from the TO and FROM columns
allidsset = list()
allidsset = list(set(allids))

conncounter = 0
for id in allidsset:
    conncounter = 0
    randlen = random.randint(0,7)   # random number of connections
    while conncounter < randlen:
        randid = random.choice(allidsset)
        # print(str(id) + '\t' + str(randid))
        f.write(str(id) + '\t' + str(randid) + '\n')
        conncounter += 1

f.close()
print("new network file created.")