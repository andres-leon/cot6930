import sys
import re
import time

# read group dictionary into dictionary called groupdict
groupdict = {}
def loadgroupdictionary():
    groupdictfile = open("group-dictionary.txt", "r")
    with groupdictfile:
        line = groupdictfile.readline()
        while line != '':
            linedata = line.split('\t')
            groupdict[int(linedata[0])] = str(linedata[1]).strip()

            line = groupdictfile.readline()

    print("read " + str(len(groupdict)) + " items to group dictionary")

# read random graph
def randomgraph():
    rand_dvd_w = open("_recom-rand1-dvd.txt", 'w')
    rand_book_w = open("_recom-rand1-book.txt", 'w')
    rand_video_w = open("_recom-rand1-video.txt",'w')
    rand_music_w = open("_recom-rand1-music.txt",'w')
    recomgraphfile = open("recom-rand1.txt", "r")
    with recomgraphfile:
        line = recomgraphfile.readline()
        while line != '':
            linedata = line.split('\t')
            recommended_id = int(linedata[0])
            if recommended_id in groupdict:
                if groupdict[recommended_id] == "DVD":
                    rand_dvd_w.write(line)
                elif groupdict[recommended_id] == "Book":
                    rand_book_w.write(line)
                elif groupdict[recommended_id] == "Video":
                    rand_video_w.write(line)
                elif groupdict[recommended_id] == "Music":
                    rand_music_w.write(line)

                print("added id " + str(recommended_id) + " to group " + groupdict[recommended_id])

            line = recomgraphfile.readline()

    rand_dvd_w.close()
    rand_book_w.close()
    rand_video_w.close()
    rand_music_w.close()


def main():
    # process_metadata()
    # load_similar_list()
    # writesubgraph()
    loadgroupdictionary()
    randomgraph()


if __name__ == "__main__":
    main()
