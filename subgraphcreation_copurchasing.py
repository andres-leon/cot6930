import sys
import re
import time

nodes = {}              # dictionary of nodes indexed by id. it holds objects of class Node
nodes_by_asin = {}      # dictionary of nodes indexed by asin. it holds objects of class Node
ids_with_similar = {}   # dictionary with key id and value of list of similar id's
group_names = {}        # dictionary of group name and total count

class NodeItem(object):
    nodeid = -1
    group = ""
    similars = list()  # list of ASINs of nodes that are similar to this node

    def __init__(self, givenNodeId):
        self.nodeid = givenNodeId


def handleSimilars(node_id, line):
    similarsasinlist = list()
    similarlist = line.split("  ")
    for similaritem in similarlist:
        if len(similaritem) > 3:
            similarsasinlist.append(similaritem.strip())
    return similarsasinlist


# group_dictionary = "group-dictionary.txt"
# dictionarywrite = open(group_dictionary, 'w')


def process_metadata():
    meta_text = open("amazon-meta-large.txt", "r")
    with meta_text:
        line = meta_text.readline()
        while line != '':
            if "Id:   " in line:  # ================ begin new node ==================
                    linelist1 = line.split("   ")
                    node_id = linelist1[1]
                    node_id = node_id.strip()
                    newNode = NodeItem(node_id)  # crete new node object and give it it's id

            elif "ASIN:" in line:
                    linelist1 = line.split()
                    node_asin = linelist1[1]
                    newNode.asin = node_asin

            elif "  group:" in line:
                linelist1 = line.split("  group:")
                node_group = linelist1[1]
                node_group = node_group.strip()
                newNode.group = node_group

            elif "  similar:" in line:
                linelist1 = line.split("  similar:")
                node_asin_similar_line = linelist1[1].strip()
                newNode.similars = handleSimilars(node_id, node_asin_similar_line)

                nodes[int(node_id)] = newNode  # add node to dict by id
                print("adding node " + str(node_id) + " with group " + str(newNode.group))
                nodes_by_asin[node_asin] = newNode  # add node to dict by asin

            line = meta_text.readline()

    print("Total Nodes Processed: " + str(len(nodes)))


def getnodeidbyasin(givenasin):
    try:
        givennode = nodes_by_asin[givenasin]
        return givennode.nodeid
    except:
        # probably didn't find it in the dictionary...
        return -1


def load_similar_list():
    for key, val in nodes.iteritems():
        similaridlist = list()
        simasinlist = val.similars
        for simasinitem in simasinlist:
            simitemnodeid = getnodeidbyasin(simasinitem)
            if simitemnodeid > -1:
                # print("adding similar node id " + str(simitemnodeid) + " to node id " + str(key))
                similaridlist.append(simitemnodeid)

        ids_with_similar[key] = similaridlist

    # now check how many items have similar items...
    itmsWithSimsCounter = 0
    for itmkey, itmval in ids_with_similar.iteritems():
        if len(itmval) > 0:
            itmsWithSimsCounter += 1
    print("ids_with_similar wih similar items: " + str(itmsWithSimsCounter))


def writesubgraph():
    # rec_dvd_w = open("recommendation-dvd.txt", 'w')
    # rec_book_w = open("recommendation-book.txt", 'w')
    # rec_video_w = open("recommendation-video.txt",'w')
    # rec_music_w = open("recommendation-music.txt",'w')
    cop_dvd_w = open("_copurchase-dvd.txt",'w')
    cop_book_w = open("_copurchase-book.txt",'w')
    cop_video_w = open("_copurchase-video.txt",'w')
    cop_music_w = open("_copurchase-music.txt",'w')
    # ran_dvd_w = open("random-dvd.txt",'w')
    # ran_book_w = open("random-book.txt",'w')
    # ran_video_w = open("random-video.txt",'w')
    # ran_music_w = open("random-music.txt",'w')

    for id, val in nodes.iteritems():
        copurchaselist = list()
        copurchaselist  = ids_with_similar[id]

        if val.group == "DVD":
            for copid in copurchaselist:
                linetowrite = str(id) + '\t' + str(copid)
                cop_dvd_w.write(linetowrite  + '\n')
                print("Writing to dvd: " + linetowrite)
        elif val.group == "Book":
            for copid in copurchaselist:
                linetowrite = str(id) + '\t' + str(copid)
                cop_book_w.write(linetowrite  + '\n')
                print("Writing to book: " + linetowrite)
        elif val.group == "Video":
            for copid in copurchaselist:
                linetowrite = str(id) + '\t' + str(copid)
                cop_video_w.write(linetowrite  + '\n')
                print("Writing to video: " + linetowrite)
        elif val.group == "Music":
            for copid in copurchaselist:
                linetowrite = str(id) + '\t' + str(copid)
                cop_music_w.write(linetowrite  + '\n')
                print("Writing to music: " + linetowrite)

    cop_dvd_w.close()
    cop_book_w.close()
    cop_music_w.close()
    cop_video_w.close()



def main():
    process_metadata()
    load_similar_list()
    writesubgraph()

if __name__ == "__main__":
    main()
