'''
------------------------------------------------------------------------------------------------------------
Changes Log  (current version: 2.0)
------------------------------------------------------------------------------------------------------------
Date     |   Changes
------------------------------------------------------------------------------------------------------------
11/9/14  | Added processfile2 and processfile3 to read amazon0302.txt and similar-network.txt respectively
11/9/14  | Added printtocsv function to allow printing a dictionary to a .csv file
11/9/14  | Added runfullcomparison to compare the two dictionaries ids_with_recom and ids_with_similar_file
         | and report the results
11/9/14  | Added do_runfullcomparison to allow access to runfullcomparison from cmd line
11/9/14  | Commented out the functions in main that built the nodes and ids_with_similar
11/9/14  | Upgraded to version 2.0 with changes made on 11/9/14
11/13/14 | Combined process_file2 and process_file3 into one function named process_graph_file(filename,dict,mytext)
         | where dict = the dictionary data structure to store in and mytext is the read variable
11/13/14 | Created a more generalized version of comparefulldicts into comparedicts(dict1,dict2)
11/13/14 | Created the dictionary ids_with_recom_rand1 to hold the first created random graph data
11/13/14 | Created a function: do_runcomparisonrand1  that will allow a user to use the command line
         | to compare the copurchased.txt and recom-rand1.txt
11/13/14 | Changed the names of these files:
         | amazon0302.txt --> recommended.txt
         | similar-network.txt --> copurchased.txt
         | 0302-random-graph.txt --> recom-rand1.txt
11/14/14 | (AL) Added function jaccardcompare with parameter 'type' that can be 'rec' for recommended or
         | 'rand' for random. Loops through the dictionary items of the given graph and performs a Jaccard
         | comparison with the co-purchased (similar) data. Results are stored in csv files.
11/14/14 | (AL) Added command line jaccardcompare to perform this action. no parameters are needed.
11/14/14 | (AL) Added this file to GitHub for version control.
11/18/14 | (EL) Created a second random recommendation graph named recom-rand2.txt
11/18/14 | (EL) Edited main function code to put recom-rand2.txt into a dictionary called ids_with_recom_rand2
11/18/14 | (EL) Edited the jaccardcompare and do_jaccardcompare to run jaccard compare on new random graph
11/18/14 | (EL) Added function for Cosine Similarity cosinesim and the cooresponding cmd line "do" function
11/21/14 | (EL) Edited Cosine Sim functionality to allow for it to work properly
11/22/14 | (EL) Imported SNAP into project
11/22/14 | (EL) Created graphs for each list: rec_graph, copur_graph, rec_rand1_graph, rec_rand2_graph
11/22/14 | (EL) Added Pagerank funciton for each graph
------------------------------------------------------------------------------------------------------------

Notes:  Make sure to have these files in your project directory:
(1) recommended.txt  (used to be amazon0302.txt)
(2) copurchased.txt (used to be similar-network.txt)
(3) recom-rand1.txt (used to be 0302-random-graph.txt)
(4) recom-rand2.txt

Both files need to be only numbers, no headers
'''

import sys
import re
import time
import cmd
import csv
import numpy as np
import snap

similaritynetworkfilename = 'similar-network.txt'
nodes = {}  # dictionary of nodes indexed by id. it holds objects of class Node
nodes_by_asin = {}  # dictionary of nodes indexed by asin. it holds objects of class Node
ids_with_similar = {}  # dictionary with key id and value of list of similar id's
ids_with_similar_file = {}  # dictionary with same data as ids_with_similar except read from a similar
ids_with_recom = {}  # dictionary with key id and value of list of recommended ids from amazon0302
ids_with_recom_rand1 = {}  # dictionary to store the first randomly generated recommended nodes graph
ids_with_recom_rand2 = {}  # dictionary to store the second randomly generated recommended nodes graph
toList = []
rec_graph = snap.LoadEdgeList(snap.PNGraph, "recommended.txt", 0, 1)
copur_graph = snap.LoadEdgeList(snap.PNGraph, "copurchased.txt", 0, 1)
rec_rand1_graph = snap.LoadEdgeList(snap.PNGraph, "recom-rand1.txt", 0, 1)
rec_rand2_graph = snap.LoadEdgeList(snap.PNGraph, "recom-rand2.txt", 0, 1)

class NodeItem(object):
    nodeid = -1
    asin = ""
    title = ""
    group = ""
    salesrank = 0
    similars = list()  # list of ASINs of nodes that are similar to this node
    categories = list()  # list of categories this node belongs to
    downloaded = 0
    avg_rating = 0
    reviews = {}  # dictionary of reviews indexed by customer

    def __init__(self, givenNodeId):
        self.nodeid = givenNodeId


class Review(object):
    reviewdate = ""
    customer = ""
    rating = 0
    votes = 0
    helpful = 0

    def __init__(self, givenreviewdate):
        self.reviewdate = givenreviewdate


def handleToList(last_pos, categoryCount):
    categorieslist = list()
    # print(my_text.tell())
    for i in range(0, categoryCount):
        catline = my_text.readline()
        catline = catline.strip()
        catlist = catline.split("|")
        catlist.pop(0)  # remove the first item which is blank
        categorieslist.append(catlist)
    return categorieslist


def handleSimilars(node_id, line):
    similarsasinlist = list()
    similarlist = line.split("  ")
    for similaritem in similarlist:
        if len(similaritem) > 3:
            similarsasinlist.append(similaritem.strip())
    return similarsasinlist


def handleCategories(last_pos, categoryCount):
    categorieslist = list()
    # print(my_text.tell())
    for i in range(0, categoryCount):
        catline = my_text.readline()
        catline = catline.strip()
        catlist = catline.split("|")
        catlist.pop(0)  # remove the first item which is blank
        categorieslist.append(catlist)
    return categorieslist


def handleReviewData(line, newNode):
    reviewListEntries = {}
    numOfreviews = 0
    node_downloaded = 0
    node_avg_rating = 0.0

    reviewList = line.split("  ")  # split by double spaces to breakdown the other data pieces
    for itm in reviewList:
        if len(itm) > 0:
            itmBreak = itm.split(":")
            if itmBreak[0] == "reviews":
                numOfreviews = int(itmBreak[2].strip())
            elif itmBreak[0] == "downloaded":
                node_downloaded = int(itmBreak[1].strip())
            elif itmBreak[0] == "avg rating":
                node_avg_rating = float(itmBreak[1].strip())

    newNode.downloaded = node_downloaded
    newNode.avg_rating = node_avg_rating
    # now handle the actual review entries
    for i in range(0, numOfreviews):
        reviewline = my_text.readline()
        try:
            # if newNode.title == "Danzig III: How the Gods Kill" and len(reviewListEntries) == 3:
            # a = 1
            reviewline = reviewline.strip()
            # get rid of all double spaces
            reviewline = re.sub('\s+', ' ', reviewline).strip()
            reviewlinelist = reviewline.split(' ')

            if len(reviewlinelist) > 1:
                newReview = Review(reviewlinelist[0].strip())
                newReview.customer = reviewlinelist[2].strip()
                newReview.rating = int(reviewlinelist[4].strip())
                newReview.votes = int(reviewlinelist[6].strip())
                newReview.helpful = int(reviewlinelist[8].strip())
                reviewListEntries[reviewlinelist[2].strip()] = newReview

            else:  # reviews have ended. exit out.
                break

        except:
            print("Error reading line. " + reviewline + " of node with title: '" +
                  newNode.title + "' and review counter: " + str(len(reviewListEntries)))
            # print("Error reading line. " + reviewline + " at pos: " + str(my_text.tell()) + " of node with title: '" +
            # newNode.title + "' and review counter: " + str(len(reviewListEntries)))

    return reviewListEntries

# filename = "amazon-meta-large.txt"
# filename = "amazon-meta-sample.txt"
filename = "amazon-meta.txt"
#filename = "amazon-meta-short.txt"
filename2 = "recommended.txt"
filename3 = "copurchased.txt"
filename_rand1 = "recom-rand1.txt"
filename_rand2 = "recom-rand2.txt"
#my_text = open(filename, "r")
my_text2 = open(filename2, "r") #
my_text3 = open(filename3, "r")
my_text_rand1 = open(filename_rand1, "r")
my_text_rand2 = open(filename_rand2, "r");

# used to read data from the meta-data.txt and store it in a dictionary called nodes
def process_file(filename):
    # with open(filename, "r", encoding="utf8") as my_text:
    with my_text:

        last_pos = my_text.tell()
        line = my_text.readline()
        line = line.strip()
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

            elif not "  discontinued product" in line:  # Not a discontinued item.
                if "  title:" in line:
                    linelist1 = line.split("  title: ")
                    node_title = linelist1[1]
                    node_title = node_title.strip()
                    newNode.title = node_title

                elif "  group:" in line:
                    linelist1 = line.split("  group:")
                    node_group = linelist1[1]
                    node_group = node_group.strip()
                    newNode.group = node_group

                elif "  salesrank:" in line:
                    linelist1 = line.split("  salesrank:")
                    node_salesrank = linelist1[1]
                    node_salesrank = node_salesrank.strip()
                    newNode.salesrank = node_salesrank

                elif "  similar:" in line:
                    linelist1 = line.split("  similar:")
                    node_asin_similar_line = linelist1[1].strip()
                    newNode.similars = handleSimilars(node_id, node_asin_similar_line)

                elif "  categories:" in line:
                    linelist1 = line.split("  categories:")
                    numOfCategories = linelist1[1].strip()
                    newNode.categories = handleCategories(last_pos, int(numOfCategories))

                elif "reviews: total: " in line:
                    newNode.reviews = handleReviewData(line, newNode)

                    # print("nodeid {0} added.".format(node_id))
                    nodes[int(node_id)] = newNode  # add node to dict by id
                    nodes_by_asin[node_asin] = newNode  # add node to dict by asin

            else:  # it is a discontinued item
                # print("nodeid {0} added.".format(node_id))
                nodes[int(node_id)] = newNode  # add node to dict by id
                nodes_by_asin[node_asin] = newNode  # add node to dict by asin

            last_pos = my_text.tell()
            line = my_text.readline()

    # for node in nodes:
    # print("ID: " + str(node.nodeid) + " ASIN: " + node.asin + " Title: '" + node.title + "' Group: " + node.group +
    # " Salesrank: " + node.salesrank)

    print("Total Nodes Processed: " + str(len(nodes)))

def process_graph_file(filename, dict, mytext):
    prev_from_id = 0

    with mytext:
       line = mytext.readline()
       line = line.strip()
       while line != '':
            linelist = line.split('\t')
            curr_from_id = linelist[0]
            curr_to_id = int(linelist[1])

            if curr_from_id == prev_from_id:
                # same node
                toList.append(curr_to_id)

            else:
                # new node. save prev node data
                finlist = list()
                for eachitm in toList:  # deep list copy
                    finlist.append(eachitm)

                dict[prev_from_id] = finlist
                del toList[:]
                #print("node " + str(prev_from_id) + " has nodes " + str(ids_with_similar_file[prev_from_id]))
                toList.append(curr_to_id)  # add the current to item to the new node

            prev_from_id = curr_from_id
            line = mytext.readline()
            line = line.strip()

    print("Total Nodes Processed: " + str(len(ids_with_recom)))


def cmdPrintAllNodeData(passednode):
    # nodeid = -1
    print("id: " + str(passednode.nodeid))
    # asin = ""
    print("asin: '" + passednode.asin + "'")
    # title = ""
    print("title: '" + passednode.title + "'")
    # group = ""
    print("group: '" + passednode.group + "'")
    # salesrank = 0
    print("salesrank: " + str(passednode.salesrank))
    # similars = list()
    print("similar: " + str(len(passednode.similars)))
    for itmsimilars in passednode.similars:
        print("  " + itmsimilars)
    # categories = list()
    print("categories: " + str(len(passednode.categories)))
    for itmcategorylines in passednode.categories:
        sys.stdout.write("  ")
        for itmcategory in itmcategorylines:
            sys.stdout.write(itmcategory + " - ")
        print("")
    # downloaded = 0
    print("downloaded: " + str(passednode.downloaded))
    # avg_rating = 0
    print("avg_rating: " + str(passednode.avg_rating))
    # reviews = list()
    print("reviews: " + str(len(passednode.reviews)))
    for key, value in passednode.reviews.items():
        givenReview = value
        print("  Customer: '" + key + "' review date: '" + givenReview.reviewdate +
              "' rating: " + str(givenReview.rating) + " votes: " + str(givenReview.votes) +
              " helpful: " + str(givenReview.helpful))


class cmdShell(cmd.Cmd):
    def do_quit(self, line):
        print("Thanks for playing! Good bye.")
        return True

    def do_getnodebyid(self, line):
        'brings data from given node id. parameters: id [field]'
        start_time = time.clock()
        cmdparams = line.split(' ')
        if len(cmdparams) == 1:  # show all node details
            try:
                calledNode = nodes[int(line)]
                cmdPrintAllNodeData(calledNode)
            except:
                print("Error loading this node or it doesn't exist.")
        else:  # other parameters beside the id have been passed
            try:
                calledNode = nodes[int(cmdparams[0])]
                if cmdparams[1] == "title":
                    print("'" + calledNode.title + "'")
                elif cmdparams[1] == "asin":
                    print("'" + calledNode.asin + "'")

            except:
                print("Error loading this node or it doesn't exist.")

        end_time = time.clock()
        total_time = end_time - start_time
        print("Execution Time: " + str(total_time) + " millisecs.")

    def do_getnodebyasin(self, line):
        'get node by its asin'
        start_time = time.clock()
        cmdparams = line.split(' ')

        if len(cmdparams) == 1:  # only retrieve title
            try:
                calledNode = nodes_by_asin[line]
                cmdPrintAllNodeData(calledNode)
            except:
                print("Error loading this node or it doesn't exist.")
        else:  # other parameters beside the id have been passed
            try:
                calledNode = nodes_by_asin[cmdparams[0]]
                if cmdparams[1] == "title":
                    print("'" + calledNode.title + "'")
                elif cmdparams[1] == "asin":
                    print("'" + calledNode.asin + "'")
                elif cmdparams[1] == "nodeid":
                    print("'" + calledNode.nodeid + "'")

            except:
                print("Error loading this node or it doesn't exist.")

        end_time = time.clock()
        total_time = end_time - start_time
        print("Execution Time: " + str(total_time) + " millisecs.")

    def do_getnodeidbyasin(self, line):
        'get the data about a node based on its ASIN'
        start_time = time.clock()
        cmdparams = line.split(' ')
        if len(cmdparams) == 1:
            try:
                print(getnodeidbyasin(line))
            except:
                print("Error loading this node or it doesn't exist.")

        end_time = time.clock()
        total_time = end_time - start_time
        print("Execution Time: " + str(total_time) + " millisecs.")

    def do_getsimilarpurchasedidsbyid(self, line):
        'lists the ids of items similar to the given item id'
        start_time = time.clock()
        cmdparams = line.split(' ')
        if len(cmdparams) == 1:
            listofids = getsimilarpurchasedids(int(line))
            for simitemnodeid in listofids:
                print(simitemnodeid)

            print(str(len(listofids)) + " similar items found.")

        end_time = time.clock()
        total_time = end_time - start_time
        print("Execution Time: " + str(total_time) + " millisecs.")

    def do_createsimilaritynetworkfile(self, line):
        'Creates the network graph file that connects product ids with their simiar items.'
        start_time = time.clock()
        print("Creating the network file for similar items. Please wait...")
        load_similar_network_file()
        end_time = time.clock()
        total_time = end_time - start_time
        print("Done creating file " + similaritynetworkfilename +
              ". Execution Time: " + str(total_time) + " millisecs.")

    def do_runcomparisonoriginal(self, line):
        'Runs a comparison on the original two datasets: recommended.txt and copurchased.txt'
        start_time = time.clock()
        print("Comparing the two dictionaries: ids_with_similar_file and ids_with_recom")
        comparedicts(ids_with_similar_file, ids_with_recom)
        print("Done comparing. Total items in amazon0302.txt = " + str(len(ids_with_recom)))
        print("Total items in similar-network.txt = " + str(len(ids_with_similar_file)))
        end_time = time.clock()
        total_time = end_time - start_time
        print("Done in " + str(total_time / 60) + " minute(s).")

    def do_runcomparisonrand1(self, line):
        'Runs a comparison on the original recommended data (recommended.txt) and the 1st randomly generated recom data'
        start_time = time.clock()
        print("Comparing the two dictionaries: ids_with_similar_file and ids_with_recom_rand1")
        comparedicts(ids_with_similar_file, ids_with_recom_rand1)
        print("Done comparing. Total items in recom-rand1.txt = " + str(len(ids_with_recom_rand1)))
        print("Total items in similar-network.txt = " + str(len(ids_with_similar_file)))
        end_time = time.clock()
        total_time = end_time - start_time
        print("Done in " + str(total_time / 60) + " minute(s).")

    def do_runcomparisonrand2(self, line):
        'Runs a comparison on the original recommended data (recommended.txt) and the 2nd randomly generated recom data'
        start_time = time.clock()
        print("Comparing the two dictionaries: ids_with_similar_file and ids_with_recom_rand2")
        comparedicts(ids_with_similar_file, ids_with_recom_rand2)
        print("Done comparing. Total items in recom-rand2.txt = " + str(len(ids_with_recom_rand2)))
        print("Total items in similar-network.txt = " + str(len(ids_with_similar_file)))
        end_time = time.clock()
        total_time = end_time - start_time
        print("Done in " + str(total_time / 60) + " minute(s).")

    def do_jaccardcompare(self, line):
        'Compares the items of the copurchasing data with the recommended and random data (Jaccard Sim). No parameters.'
        start_time = time.clock()
        print("START Performing Jaccard comparison with recommended file")
        jaccardcompare("rec")
        print("DONE Performing Jaccard comparison with recommended file")
        print("START Performing Jaccard comparison with first random file")
        jaccardcompare("ran")
        print("START Performing Jaccard comparison with second random file")
        jaccardcompare("ran2")
        end_time = time.clock()
        total_time = end_time - start_time
        print("DONE Performing Jaccard comparison with the files")
        print("Done. Execution Time: " + str(total_time) + " secs.")

    def do_cosinesim(self, line):
        'Compares the items of the copurchasing data with the recommended and random data (Cosine sim). No parameters.'
        start_time = time.clock()
        print("START Performing Cosine Similarity comparison with recommended file")
        cosinesim("rec")
        print("DONE Performing Cosine Similarity comparison with recommended file")
        print("START Performing Cosine Similarity comparison with first random file")
        cosinesim("ran")
        print("START Performing Cosine Similarity comparison with second random file")
        cosinesim("ran2")
        end_time = time.clock()
        total_time = end_time - start_time
        print("DONE Performing Cosine Similarity comparison with the files")
        print("Done. Execution Time: " + str(total_time) + " secs.")

    def do_getgraphsize(self,line):
        'Returns the size of a graph input: rec, copur, ran, or ran2'
        if line == 'rec':
            print "Recommendation Graph: Nodes %d, Edges %d" % (rec_graph.GetNodes(), rec_graph.GetEdges())
        elif line == 'copur':
            print "CoPurchased Graph: Nodes %d, Edges %d" % (copur_graph.GetNodes(), copur_graph.GetEdges())
        elif line == 'ran':
            print "Random Graph 1: Nodes %d, Edges %d" % (rec_rand1_graph.GetNodes(), rec_rand1_graph.GetEdges())
        elif line == 'ran2':
            print "Random Graph 2: Nodes %d, Edges %d" % (rec_rand2_graph.GetNodes(), rec_rand2_graph.GetEdges())

    def do_getpagerank(self,line):
        'Prints the pagerank of each node depending on input graph: rec, copur, ran, ran2'
        if line == 'rec':
            pagerank("rec")
        elif line == 'copur':
            pagerank("copur")
        elif line == 'ran':
            pagerank("ran")
        elif line == 'ran2':
            pagerank("ran2")



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

def load_similar_network_file():
    # creates the network graph text file that connects product ids
    # with their similar items from the metadata file.
    numofnodes = 0
    numofedges = 0
    f = open(similaritynetworkfilename, 'w')
    f.write('# Nodes:  Edges: \n')
    f.write('# FromNodeId\tToNodeId\n')
    for key, val in ids_with_similar.iteritems():
        numofnodes += 1
        for eachid in val:
            f.write(str(key) + '\t' + str(eachid) + '\n')
            numofedges += 1

    f.close()
    print("nodes: " + str(numofnodes) + " edges: " + str(numofedges))

def getsimilarpurchasedids(nodeid):
    returnlist = list()
    try:
        # print("Finding similar items for node id: " + str(nodeid))
        returnlist = ids_with_similar[nodeid]
        # print("found  " + str(len(returnlist)) + " similar items for node id " + str(nodeid))

        return returnlist
    except:
        return returnlist

def getnodeidbyasin(givenasin):
    try:
        givennode = nodes_by_asin[givenasin]
        return givennode.nodeid
    except:
        # probably didn't find it in the dictionary...
        return -1

def printtocsv(dict1, dict_filename):
    writer = csv.writer(open(dict_filename, 'wb'))
    for key, value in dict1.items():
        writer.writerow([key, value])

def jaccardcompare(file_type):
    jaccard_scores = {}
    # loop through the dictionaries and do comparison
    for key in range(1, 361567):
        new_key = str(key)
        # reassign the list in value of each item to a new one so they can be compared
        a = ids_with_similar_file.get(new_key, 'none')
        if file_type == "rec":
            b = ids_with_recom.get(new_key, 'none')
            csv_file_name = "jaccardscore01RECOMMENDED.csv"
        elif file_type == "ran":
            b = ids_with_recom_rand1.get(new_key, 'none')
            csv_file_name = "jaccardscore01RANDOM.csv"
        else:
            b = ids_with_recom_rand2.get(new_key, 'none')
            csv_file_name = "jaccardscore01RANDOM2.csv"
        # the dict.get(x, y): x = key of dictionary (with single quotes around it),
        # y = if no key that is passed is found, return THIS ('none') instead
        if (a or b) <> 'none':
            cnt_union = len(list(set(a).union(set(b))))
            if cnt_union > 0:
                cnt_intersection = len(set(a).intersection(b))
                jaccard_scores[key] = float(cnt_intersection) / float(cnt_union)
            else:
                jaccard_scores[key] = 0.0

            if float(jaccard_scores[key]) > 0:
                print(new_key + " = " + str(jaccard_scores[key]))

    printtocsv(jaccard_scores, csv_file_name)

def cosinesim(file_type):
    cosine_scores = {}
    # loop through the dictionaries and do comparison by cosine similiarity
    highestall = 0
    for key in range(1, 361567):
        new_key = str(key)
        # reassign the list in value of each item to a new one so they can be compared
        a = ids_with_similar_file.get(new_key, 'none')
        if file_type == "rec":
            b = ids_with_recom.get(new_key, 'none')
            csv_file_name2 = "cosinescore01RECOMMENDED.csv"
        elif file_type == "ran":
            b = ids_with_recom_rand1.get(new_key, 'none')
            csv_file_name2 = "cosinescore01RANDOM.csv"
        else:
            b = ids_with_recom_rand2.get(new_key, 'none')
            csv_file_name2 = "cosinescore01RANDOM2.csv"
        '''if (a or b) <> 'none':
            a = np.array(a, np.float)
            b = np.array(b, np.float) '''

        # this is used to make the vectors the same size by adding extra zeros
        # dictionaries will be unusable after this for other calculations

        if a <> 'none':
            if b <> 'none':
                if(len(a) <> len(b)):
                    toaddA = 7 - len(a)
                    toaddB = 7 - len(b)
                    counterA = toaddA
                    counterB = toaddB
                    for x in range(0, toaddA):
                        a.insert(counterA, 0)
                        ++counterA
                    for y in range(0, toaddB):
                        b.insert(counterB, 0)
                        ++counterB


        # the dict.get(x, y): x = key of dictionary (with single quotes around it),
        # y = if no key that is passed is found, return THIS ('none') instead
        #if len(a) == len(b):
        if a <> 'none':
            if b <> 'none':
                # arrays must be converted to floats to have np.linalg used on them

                a = np.array(a, np.float)
                b = np.array(b, np.float)

                cosinesim = np.dot(a,b.T)/np.linalg.norm(a)/np.linalg.norm(b)
                # cosine sim done here
                #ab = np.linalg.norm(a) / np.linalg.norm(b)
                #print ab

                #abdot = np.vdot(a,b)
                #print abdot

                #cosinesim = abdot / ab

                if cosinesim > 0:
                    cosine_scores[key] = cosinesim
                else:
                    cosine_scores[key] = 0.0

                if float(cosine_scores[key]) > 0:
                    print(new_key + " = " + str(cosine_scores[key]))

    printtocsv(cosine_scores, csv_file_name2)

def pagerank(file_type):
    if(file_type == "rec"):
        PRankH = snap.TIntFltH()
        snap.GetPageRank(rec_graph, PRankH)
        for item in PRankH:
            print item, PRankH[item]
    elif(file_type == "copur"):
        PRankH = snap.TIntFltH()
        snap.GetPageRank(copur_graph, PRankH)
        for item in PRankH:
            print item, PRankH[item]
    elif(file_type == "ran"):
        PRankH = snap.TIntFltH()
        snap.GetPageRank(rec_rand1_graph, PRankH)
        for item in PRankH:
            print item, PRankH[item]
    elif(file_type == "ran2"):
        PRankH = snap.TIntFltH()
        snap.GetPageRank(rec_rand2_graph, PRankH)
        for item in PRankH:
            print item, PRankH[item]




def comparedicts(dict1, dict2):
    # initialze counters
    count = count1 = count2 = count3 = count4 = 0

    # loop through the dictionaries and do comparison
    for key in range(1, 361567):
        # key here has to be formatted to be used with dict.get.  Needs
        # to be in format of '1' instead of just 1
        new_key = key
        new_key = '%d' % new_key

        # reassign the list in value of each item to a new one so they can be compared
        a = dict1.get(new_key, 'none')
        b = dict2.get(new_key, 'none')

        # the dict.get(x, y): x = key of dictionary (with single quotes around it),
        # y = if no key that is passed is found, return THIS ('none') instead
        if (a or b) <> 'none':

            # We are testing here to only return nodes with 1+ similarities
            if len(set(a).intersection(b)) > 0:
                if(len(set(a).intersection(b)) == 1):
                    count1 = count1 + 1
                elif(len(set(a).intersection(b)) == 2):
                    count2 = count2 + 1
                elif(len(set(a).intersection(b)) == 3):
                    count3 = count3 + 1
                elif(len(set(a).intersection(b)) == 4):
                    count4 = count4 + 1

                print a
                print b
                print "key: %s" % new_key
                print set(a).intersection(b)
                print len(set(a).intersection(b))
                print '------------------------'
                count = count + 1

    print "Count of 1: %d " % count1
    print "Count of 2: %d " % count2
    print "Count of 3: %d " % count3
    print "Count of 4: %d " % count4


def main():
    # These two functions below are commented out because we are now using the actual
    # files, amazon0302.txt and similar-network.txt instead of generating it again

    '''start_time = time.clock()
    print("Loading metadata from text file. This will take a few minutes...")
    process_file(filename)
    end_time = time.clock()
    total_time = end_time - start_time
    print("Data has been loaded into memory in " + str(total_time / 60) + " minute(s).")

    start_time = time.clock()
    print("Connecting items purchased together (similar) with each other...")
    # this needs to be done AFTER all the data has been loaded because each item's similar
    # list is made up of items that can be anywhere on the file.
    load_similar_list()
    print("Done connecting. total items = " + str(len(ids_with_similar)))
    end_time = time.clock()
    total_time = end_time - start_time
    print("Done in " + str(total_time / 60) + " minute(s).")'''

    # Creating ids_with_recom from amazon0302.txt
    start_time = time.clock()
    print("Creating recommendation list from recommended.txt")
    process_graph_file(filename2, ids_with_recom, my_text2)
    print("Done connecting. total items = " + str(len(ids_with_recom)))
    end_time = time.clock()
    total_time = end_time - start_time
    print("Done in " + str(total_time / 60) + " minute(s).")
    #printtocsv(ids_with_recom, "dict3.csv")

    # Creating ids_with_similar_file from similar-network.txt
    start_time = time.clock()
    print("Creating similar list from copurchased.txt")
    process_graph_file(filename3, ids_with_similar_file, my_text3)
    print("Done connecting. total items = " + str(len(ids_with_similar_file)))
    end_time = time.clock()
    total_time = end_time - start_time
    print("Done in " + str(total_time / 60) + " minute(s).")
    #printtocsv(ids_with_similar_file, "dict4.csv")

    # the below will be part of the cmd shell
    # Compare the two dictionaries
    '''start_time = time.clock()
    print("Comparing the two dictionaries: ids_with_similar_file and ids_with_recom")
    #comparefulldicts()
    print("Done comparing. Total items in amazon0302.txt = " + str(len(ids_with_recom)))
    print("Total items in similar-network.txt = " + str(len(ids_with_similar_file)))
    end_time = time.clock()
    total_time = end_time - start_time
    print("Done in " + str(total_time / 60) + " minute(s).")'''

    # Creating ids_with_recom_rand1 from recom-rand1.txt
    start_time = time.clock()
    print("Creating random recommendation list from recom-rand1.txt")
    process_graph_file(filename_rand1, ids_with_recom_rand1, my_text_rand1)
    print("Done connecting. total items = " + str(len(ids_with_recom_rand1)))
    end_time = time.clock()
    total_time = end_time - start_time
    print("Done in " + str(total_time / 60) + " minute(s).")

    # Creating ids_with_recom_rand2 from recom-rand2.txt
    start_time = time.clock()
    print("Creating random recommendation list from recom-rand2.txt")
    process_graph_file(filename_rand2, ids_with_recom_rand2, my_text_rand2)
    print("Done connecting. total items = " + str(len(ids_with_recom_rand2)))
    end_time = time.clock()
    total_time = end_time - start_time
    print("Done in " + str(total_time / 60) + " minute(s).")




if __name__ == "__main__":
    main()
    cmdShell().cmdloop("Hello. Enter 'help' for list of commands.")


