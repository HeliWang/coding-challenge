# First Feature - tweets_cleaned.py
# Main idea: Read each line from input data;
#            Filter out non-ascii chars;
#            Calculate the number of tweets containing unicode

import sys
import json

input_filepath  = sys.argv[1]
output_filepath = sys.argv[2]

def tweets_cleaned():
    out_file = open(output_filepath, 'w')
    
    try:
        with open(input_filepath) as input_file:
            content = input_file.readlines()
            unicode_count = 0
            for json_line in content:
                # Parse each json line
                raw_json = json.loads(json_line.rstrip())
                try:
                    time_stamp = raw_json['created_at']
                    text       = raw_json['text']
                    textAscii  = "".join(filter(lambda x: ord(x)<128, text)) # Filter out non-ascii chars
                    if (len(textAscii) != len(text)): 
                        unicode_count += 1
                    textAscii = textAscii.replace("\n"," ").strip() # Replace newline char in the text
                    out_file.write(textAscii + " " + "(timestamp: " + time_stamp + ")" + "\n")
                except KeyError:
                    pass # could be whitespace
                    
            out_file.write("\n")
            out_file.write("%d tweets contained unicode." %(unicode_count))
            out_file.close()
            
    except IOError:
        print "Invalid Input File Path"

tweets_cleaned()