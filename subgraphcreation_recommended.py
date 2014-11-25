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

# read recommended graph
def recommgraph():
    rec_dvd_w = open("_recommendation-dvd.txt", 'w')
    rec_book_w = open("_recommendation-book.txt", 'w')
    rec_video_w = open("_recommendation-video.txt",'w')
    rec_music_w = open("_recommendation-music.txt",'w')
    recomgraphfile = open("recommended.txt", "r")
    with recomgraphfile:
        line = recomgraphfile.readline()
        while line != '':
            linedata = line.split('\t')
            recommended_id = int(linedata[0])
            if recommended_id in groupdict:
                if groupdict[recommended_id] == "DVD":
                    rec_dvd_w.write(line)
                elif groupdict[recommended_id] == "Book":
                    rec_book_w.write(line)
                elif groupdict[recommended_id] == "Video":
                    rec_video_w.write(line)
                elif groupdict[recommended_id] == "Music":
                    rec_music_w.write(line)

                print("added id " + str(recommended_id) + " to group " + groupdict[recommended_id])

            line = recomgraphfile.readline()

    rec_dvd_w.close()
    rec_book_w.close()
    rec_video_w.close()
    rec_music_w.close()


def main():
    # process_metadata()
    # load_similar_list()
    # writesubgraph()
    loadgroupdictionary()
    recommgraph()


if __name__ == "__main__":
    main()
