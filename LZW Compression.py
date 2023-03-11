#!/usr/bin/env python
# coding: utf-8

# Harjot Mangat
# EECS 258 - Multimedia Systems
# LZW Compression

#string_dict = {'a':1,'b':2,'c':3,'d':4} # use in case of a-d characters
string_dict = {'a':1,'b':2,'c':3}
#next_code = 5 # use in case of a-d characters
next_code = 4
input_string = input("Please input a string of characters (a-c)")
string_list = list(input_string.strip().lower())

# used to print the total LZW code after compression
final_code = []

# s = next input character
s = string_list[0]
string_list.pop(0)

# Looping through the given string
for i in range(len(string_list)):
    
    # c = next input character
    c = string_list[i]
    
    # tmp represents s + c
    tmp = s + c
    print("S: ", s, "C: ", c)
    
    # if s + c exists in the dictionary
    if tmp in string_dict.keys():
        
        # s = S + C
        s = tmp
        
    else:
        #print("code: ", string_dict.get(s)) # for debugging
        final_code.append(string_dict.get(s))
        
        # add string s + c to the dictionary with a new code
        string_dict[tmp] = next_code
        next_code += 1
        s = c
    
# output the code for S
print("S: ", s)       
#print(string_dict.get(s)) # for debugging

# Prints the final LZW code
final_code.append(string_dict.get(s))
        
print("Final dictionary ", string_dict)
print("Output code: ",final_code)
