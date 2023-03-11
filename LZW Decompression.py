#!/usr/bin/env python
# coding: utf-8


# Harjot Mangat
# EECS 258 - Multimedia Systems
# LZW Decompression

# function for getting key for a specific value in the dictionary
def get_key(val, dictionary):
    
    #print(val) # for debugging
    #print(dictionary.items()) # for debugging
    for key, value in dictionary.items():
        if val == str(value):
            return key
 
    return "key doesn't exist"

string_dict1 = {'a':1,'b':2,'c':3}
next_code = 4

input_code = input("Please enter the code from LZW Compression ")
code_list = list(input_code.strip())

# for printing the final decoded string
final_string = []
#print(code_list) # for debugging

# s = NIL
s = None

# Looping through the given code
for i in range(len(code_list)):
    
    # k = next input code
    k = code_list[i]
    print("code k: ", k)
    
    # entry = dictionary entry for k
    entry = get_key(k , string_dict1)
    print("entry is: ", entry)
    final_string.append(entry)
    
    if s != None:
        
        # add string s + entry[0] to dictionary with a new code
        string_dict1[s + entry[0]] = next_code
        next_code += 1
    
    s = entry

print(string_dict1)
print("Output String is: ", final_string)