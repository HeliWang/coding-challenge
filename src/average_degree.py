# Second Feature - average_degree.py
# Main idea: have a list 'tweet_edge_history' which is sorted by time. Pop out-dated tweets when new tweets get pushed
#            The tweet_edge_history is a list of edge tuples (timestamp, (sourceTag, destTag)). 
#            Each tuple stands for an directed edge from sourceTag -> destTag
#              Average Degree = directed_edge_number/total_tag_number
#            In order to keep track of total_tag_number in the graph,
#            we need to have a tags_hash, where keys in tags_hash are sourceTag,
#              and values are dict of {destTag: edgeNum}
#            When an old tweet gets removed, tags_hash should be updated.
#              When the edgeNum of edge sourceTag->destTag is, the destTag should be removed from tags_hash[sourceTag]
#              When a sourceTag has no outedge, we should del tags_hash[sourceTag]
#            Thus, directed_edge_number = Sum(the numbers of destTags of each sourceTag), total_tag_number = len(tags_hash.keys())
# Edge cases: 1. Tweets with only one hashtag should NOT create nodes.
#             2. All tweets could evict older tweets from the 60-second window that affects the graph
#             3. Hashtags are NOT case-sensitive

import sys
import re
import calendar
import numpy
from dateutil import parser

input_filepath  = sys.argv[1]
output_filepath = sys.argv[2]

def average_degree():
    """ Output the average degree of each graph as new tweets coming in. """
    tweet_edge_history = []
    tags_hash = {}
    out_file = open(output_filepath, 'w')
    
    try:
        with open(input_filepath) as input_file:
            content = input_file.readlines()
            for content_line in content:
                try:
                    time_stamp = re.search(r'timestamp: (.+)\)',content_line)
                    if time_stamp is None:
                        continue
                    time_stamp = time_stamp_str = time_stamp.group(1)
                    tag_list   = numpy.unique(map(lambda tag:tag.lower(), re.findall("#(\w*)", content_line)))
                    time_stamp = calendar.timegm(parser.parse(time_stamp).timetuple())
                    tweet_edge_history = remove_expired(time_stamp, tags_hash, tweet_edge_history)
                    if len(tag_list) > 1: # Tweets with only one hashtag should NOT create nodes
                        for sourceTag in tag_list:
                            for destTag in tag_list:
                                # tags_hash = {sourceTag1: {destTag1: edgeNum1, destTag2: edgeNum2, ...}, ...}
                                if sourceTag == destTag:
                                    continue
                                if sourceTag not in tags_hash:
                                    tags_hash[sourceTag] = {} 
                                    
                                tags_hash[sourceTag][destTag] = (1 if destTag not in tags_hash[sourceTag] else tags_hash[sourceTag][destTag] + 1)
                                tweet_edge_history.append((time_stamp, (sourceTag, destTag)))
                    
                    totalEdgeNumber = 0
                    for sourceTag in tags_hash.keys():
                        totalEdgeNumber += len(tags_hash[sourceTag].keys())
                    avg_degree = "%.2f\n" %0
                    if totalEdgeNumber != 0: 
                        avg_degree = "%.2f\n" %(float(totalEdgeNumber)/float(len(tags_hash.keys())))
                    out_file.write(avg_degree)
                    # print tags_hash # Uncomment when necessary
                    # print time_stamp_str + ": current average degree is " + avg_degree
                except KeyError:
                    pass
                
            out_file.close()
    except IOError:
        print "Invalid Input File Path"

def remove_expired(time_stamp, tags_hash, tweet_edge_history):
    """ Return new tweet_edge_history after out-dated edges get moved """
    edges_expired = []
    # First find all expired hashtags
    for edge in tweet_edge_history: # edge = (timestamp, (sourceTag, destTag))
        if (time_stamp - edge[0]) > 60:
            edges_expired.append(edge)
        else:
            break # since tweet_edge_history is sorted by timestamp
    
    for edge in edges_expired:
        sourceTag = edge[1][0]
        destTag   = edge[1][1]
        if tags_hash[sourceTag][destTag] > 1:
            tags_hash[sourceTag][destTag] -= 1
        else: # remove the tag if no other tag connects to this tag
            del tags_hash[sourceTag][destTag]
        if len(tags_hash[sourceTag]) == 0:
            del tags_hash[sourceTag]
            
    tweet_edge_history = tweet_edge_history[len(edges_expired):]
    return tweet_edge_history
        
average_degree()
print "Please check the result: " + output_filepath