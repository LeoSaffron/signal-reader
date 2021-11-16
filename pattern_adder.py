# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 01:30:20 2021

@author: jonsnow
"""

from selenium import webdriver
import time
from binance.client import Client
import re
from glob import glob
import pickle
from datetime import datetime
import os
import re
import os.path
from time import sleep

#driver = webdriver.Firefox()
#driver.maximize_window()


#cookies = pickle.load(open("cookies.pkl", "rb"))
#for cookie in cookies:
#    driver.add_cookie(cookie)
#driver.get("https://web.telegram.org")
#
#time.sleep(20)
#driver.find_elements_by_class_name("nav-stacked")[0].find_element_by_xpath('//span[text()="testgroup"]').click()

pattern_whitelist_path = "patterns_whitelist/"
path_unidentified_pattern_messages = "unknown_patterns/"
path_output_signal_file = "sample_log_folder/sample_log.txt"
pattern_list = []
last_message_text = ''

signal_list = []
emoji_V = '✅'

emoji_cool_face = '😎'

list_emojis_blacklist = {
        emoji_V,
        
        emoji_cool_face
        }
#Message message-list-item first-in-group last-in-group last-in-list
#Message message-list-item last-in-group last-in-list open shown

patterns_blacklist_single_lines = {
        'TRADING TIP OF THE DAY',
        'trading tip of the day',
        'Book half gain here and move stop loss to breakeven',
        }

pattern_test = [
 '#[A-Z]*\w\/[A-Z]*\w',
 'Exchanges: [A-Za-z ]*',
 'Signal Type: [A-Za-z]*\w \([A-Za-z]*\w\)',
 'Leverage: [A-Za-z]*\w \([A-Za-z0-9.]*\w\)',
 'Entry Targets:',
 'OFF_THE_RECORD_REGEX_MULTIPLE_LINES_FOR_NEXT_PATTERN',
 '[0-9]+\) [0-9]+(\.([0-9]+))?',
 'Take-Profit Targets:',
 'OFF_THE_RECORD_REGEX_MULTIPLE_LINES_FOR_NEXT_PATTERN',
 '[0-9]+\) [0-9]+(\.([0-9]+))?',
 'Stop Targets:',
 'OFF_THE_RECORD_REGEX_MULTIPLE_LINES_FOR_NEXT_PATTERN',
 '[0-9]+\) [0-9]+(\.([0-9]+))?',
 ]

parse_insstruction_pattern_test = [
         'OFF_THE_RECORD_PROPERTY_NAME_CONSTANT',
         'coin1',
         'OFF_THE_RECORD_PROPERTY_VALUE_FIRST_OCCURANCE_NO_NEW_LINE',
         '[A-Z]*\\w',
         'OFF_THE_RECORD_PROPERTY_NAME_CONSTANT',
         'coin2',
         'OFF_THE_RECORD_PROPERTY_VALUE_AFTER_SPECIFIC_PREFIX',
         '#[A-Z]*\\w/',
         'OFF_THE_RECORD_PROPERTY_NAME_CONSTANT',
         'exchange_list',
         'OFF_THE_RECORD_PROPERTY_VALUE_AFTER_SPECIFIC_PREFIX',
         'Exchanges: ',
         'OFF_THE_RECORD_PROPERTY_NAME_CONSTANT',
         'signal_direction',
         'OFF_THE_RECORD_PROPERTY_VALUE_BETWEEN_PREFIX_AND_SUFFIX',
         'Signal Type: [A-Za-z]*\\w \\(',
         '\\)',
         'OFF_THE_RECORD_PROPERTY_NAME_CONSTANT',
         'leverage',
         'OFF_THE_RECORD_PROPERTY_VALUE_BETWEEN_PREFIX_AND_SUFFIX',
         'Leverage: [A-Za-z]*\\w \\(',
         'X\\)',
         'OFF_THE_RECORD_PROPERTY_NAME_CONSTANT',
         'amount',
         'OFF_THE_RECORD_PROPERTY_VALUE_FIRST_OCCURANCE',
         '[0-9]+(\.([0-9]+))',
         'OFF_THE_RECORD_SKIP_LINE',
         'OFF_THE_RECORD_PROPERTY_NAME_CONSTANT',
         'entry',
         'OFF_THE_RECORD_PROPERTY_VALUE_AFTER_SPECIFIC_PREFIX_FIRST_OCCURANCE_OUT_OF_MANY_LINES',
         '[0-9]+\\)',
         'OFF_THE_RECORD_SKIP_LINE',
         'OFF_THE_RECORD_PROPERTY_NAME_CONSTANT',
         'take_profit',
         'OFF_THE_RECORD_PROPERTY_VALUE_AFTER_SPECIFIC_PREFIX_FIRST_OCCURANCE_OUT_OF_MANY_LINES',
         '[0-9]+\\) ',
         'OFF_THE_RECORD_SKIP_LINE',
         'OFF_THE_RECORD_PROPERTY_NAME_CONSTANT',
         'stop_loss',
         'OFF_THE_RECORD_PROPERTY_VALUE_AFTER_SPECIFIC_PREFIX_FIRST_OCCURANCE_OUT_OF_MANY_LINES',
         '[0-9]+\\) '
 ]


off_the_record_cusom_regex = [
        'OFF_THE_RECORD_REGEX_MULTIPLE_LINES_FOR_NEXT_PATTERN'
        ]


def check_if_str_regex_pattern(pattern_to_check):
    try:
        re.compile(pattern_to_check)
    except re.error:
        return False
    return True

#find_elements_by_class_name
#def get_last_message_from_opened_chat_full_element(driver):
##    div_tag = driver.find_element_by_xpath("//div[@class='Message message-list-item last-in-group last-in-list']")
##    message_full_text = driver.find_elements_by_class_name("message-list-item")[-1].text
#    messages_elements = driver.find_elements_by_class_name("Message")
#    if (len(messages_elements) == 0):
#        messages_elements = driver.find_elements_by_class_name("message")
#    result_element = messages_elements[-1]
##    message_full_text.split('\n',maxsplit=2)[2].rsplit('\n', maxsplit=1)[0]
##    result = message_full_text.split('\n',maxsplit=2)[2].rsplit('\n', maxsplit=1)[0]
#    return result_element


#def get_last_message_from_opened_chat_text_only(driver):
#    message_full_text = get_last_message_from_opened_chat_full_element(driver).text
#    result = message_full_text.rsplit('\n', maxsplit=2)[0]
#    return result


def get_last_message_text_from_element(element):
    message_full_text = element.text
    result = message_full_text.rsplit('\n', maxsplit=2)[0]
    return result

def read_single_pattern_identifier_by_file_path(filepath):
    result_pattern = []
    with open(filepath, "r") as pattern_file:
        lines = pattern_file.readlines()
        for l in lines:
            result_pattern.append(l.replace('\n',''))
    return result_pattern

def read_single_pattern_folder_path(folder_name):
    filepath_pattern = pattern_whitelist_path + folder_name + "/skeleton.txt"
    pattern_identifier = read_single_pattern_identifier_by_file_path(filepath_pattern)
    result = {"name" : folder_name,
     "pattern" : pattern_identifier,
     }
    filepath_parser = pattern_whitelist_path + folder_name + "/parser_instruction.txt"
    if(os.path.isfile(filepath_parser)):
        result['parse_instruction'] = read_single_pattern_identifier_by_file_path(filepath_parser)
    return result

def init_pattern_list(path):
    result_list = []
    folder_list = [x[0] for x in os.walk(path)][1:]
    folder_names_list = []
    for folder_item in folder_list:
        folder_names_list.append(folder_item.replace(path,''))
    for folder_name in folder_names_list:
        result_list.append(read_single_pattern_folder_path(folder_name))
    return result_list

def scan_message_for_emoji_V_from_element(element_to_scan):
    emoji_in_question_found_flag = False
    images_in_message = element_to_scan.find_elements_by_tag_name("img")
    for img_element in images_in_message:
        try:
            if(img_element.get_attribute('alt') == emoji_V):
                emoji_in_question_found_flag = True
        except:
            pass
    return emoji_in_question_found_flag

def message_replace_emojis_by_text(element):
    pass

def message_scan_text_for_blacklisted_patterns(element):
    message_has_blacklisted_pattern = False
    for line_to_check in element.text.split('\n'):
        for blacklist_line_element in patterns_blacklist_single_lines:
            if(re.search(blacklist_line_element, line_to_check) != None):
                message_has_blacklisted_pattern = True
    return message_has_blacklisted_pattern

def scan_message_for_V_X_etc_emojis(element):
    found_blacklisted_emoji_flag = False
    for sub_tag_after_open in element.get_attribute("innerHTML").split('<'):
        sub_tag = sub_tag_after_open.split('>')[0]
        for emoji_to_filter_out in list_emojis_blacklist:
            if(sub_tag.find(emoji_to_filter_out) >= 0):
                found_blacklisted_emoji_flag = True
    return found_blacklisted_emoji_flag

def filter_message_for_useless_info(element):
    meggase_not_useless = True
    meggase_not_useless = False if (message_scan_text_for_blacklisted_patterns(element)) else meggase_not_useless
    meggase_not_useless = False if (scan_message_for_V_X_etc_emojis(element)) else meggase_not_useless
    return meggase_not_useless

def message_check_fits_regex_specific_pattern(element, pattern):
    lines_relevant = []
    element_text_arr = element.text.split('\n')
    if(element_text_arr[-1] == 'Follow Signal'):
        element_text_arr = element_text_arr[:-1]
    if(element_text_arr[-1] == 'One Click Follow'):
        element_text_arr = element_text_arr[:-1]
    for line_to_copy in element_text_arr[:-2]:
        if (line_to_copy == ''):
            continue
        lines_relevant.append(line_to_copy.strip())
    
    flag_pattern_fits = True
    index_in_lines_list = 0
    index_in_pattern_list = 0
    while index_in_pattern_list < len(pattern):
        flag_line_custom_pattern_work = False
        flag_read_multiple_lines = False
#        print(index_in_lines_list, index_in_pattern_list) 
        if (pattern[index_in_pattern_list] in off_the_record_cusom_regex):
            flag_line_custom_pattern_work = True
            if(pattern[index_in_pattern_list] == 'OFF_THE_RECORD_REGEX_MULTIPLE_LINES_FOR_NEXT_PATTERN'):
                flag_read_multiple_lines = True
        if (index_in_lines_list >= len(lines_relevant)):
            flag_pattern_fits = False
            break
        if (flag_line_custom_pattern_work == False):
            if(re.match(pattern[index_in_pattern_list], lines_relevant[index_in_lines_list]) == None):
                flag_pattern_fits = False
            print(flag_pattern_fits)
            print(pattern[index_in_pattern_list])
            index_in_lines_list += 1
            index_in_pattern_list += 1
        elif (flag_read_multiple_lines):
            flag_at_least_one_line_matched = False
            index_in_pattern_list += 1
            while index_in_lines_list < len(lines_relevant):
                if(re.match(pattern[index_in_pattern_list], lines_relevant[index_in_lines_list]) != None):
                    flag_at_least_one_line_matched = True
                else:
    #                index_in_lines_list += 1
                    break
                index_in_lines_list += 1
            flag_pattern_fits = False if (not flag_at_least_one_line_matched) else flag_pattern_fits
            index_in_pattern_list += 1
#        print(flag_pattern_fits)
    return flag_pattern_fits

def message_check_fits_regex_specific_pattern_by_text_lines(lines, pattern):
    lines_relevant = lines
    
    flag_pattern_fits = True
    index_in_lines_list = 0
    index_in_pattern_list = 0
    while index_in_pattern_list < len(pattern):
        flag_line_custom_pattern_work = False
        flag_read_multiple_lines = False
#        print(index_in_lines_list, index_in_pattern_list) 
        if (pattern[index_in_pattern_list] in off_the_record_cusom_regex):
            flag_line_custom_pattern_work = True
            if(pattern[index_in_pattern_list] == 'OFF_THE_RECORD_REGEX_MULTIPLE_LINES_FOR_NEXT_PATTERN'):
                flag_read_multiple_lines = True
        if (index_in_lines_list >= len(lines_relevant)):
            flag_pattern_fits = False
            break
        if (flag_line_custom_pattern_work == False):
            if(re.match(pattern[index_in_pattern_list], lines_relevant[index_in_lines_list]) == None):
                flag_pattern_fits = False
            print(flag_pattern_fits)
            print(pattern[index_in_pattern_list])
            index_in_lines_list += 1
            index_in_pattern_list += 1
        elif (flag_read_multiple_lines):
            flag_at_least_one_line_matched = False
            index_in_pattern_list += 1
            while index_in_lines_list < len(lines_relevant):
                if(re.match(pattern[index_in_pattern_list], lines_relevant[index_in_lines_list]) != None):
                    flag_at_least_one_line_matched = True
                else:
    #                index_in_lines_list += 1
                    break
                index_in_lines_list += 1
            flag_pattern_fits = False if (not flag_at_least_one_line_matched) else flag_pattern_fits
            index_in_pattern_list += 1
#        print(flag_pattern_fits)
    return flag_pattern_fits

def message_check_fits_any_regex_pattern(element):
    pattern_found_flag = False
    pattern_name_identified = ''
    for pattern_list_item in pattern_list:
        if(message_check_fits_regex_specific_pattern(element, pattern_list_item['pattern'])):
            pattern_found_flag = True
            pattern_name_identified = pattern_list_item['name']
    return pattern_name_identified

def message_check_fits_any_regex_pattern_by_text_lines(lines):
    pattern_found_flag = False
    pattern_name_identified = ''
    for pattern_list_item in pattern_list:
        if(message_check_fits_regex_specific_pattern_by_text_lines(lines, pattern_list_item['pattern'])):
            pattern_found_flag = True
            pattern_name_identified = pattern_list_item['name']
    return pattern_name_identified

def get_patterns_dict_item_by_name(name):
    pattern_found_flag = False
    result = None
    for pattern_list_item in pattern_list:
        if(name == pattern_list_item['name']):
            pattern_found_flag = True
            result = pattern_list_item
    return result

    

def message_parse_by_identified_pattern(element, pattern):
    lines_message_relevant = []
    for line_to_copy in element.text.split('\n')[:-1]:
        if (line_to_copy == ''):
            continue
        lines_message_relevant.append(line_to_copy.strip())
    
    lines_parse_pattern = pattern
    
    read_parse_state = 0
    index_line_in_pattern = 0
    index_line_in_message = 0
    item_parsed_name = None
    item_parsed_value = None
    parse_instruction_for_current_regex = None
    result_dict = {}
    
    
    while ((index_line_in_pattern < len(lines_parse_pattern)) and (index_line_in_message < len(lines_message_relevant))):
        line_in_pattern = lines_parse_pattern[index_line_in_pattern]
        line_in_message = lines_message_relevant[index_line_in_message]
#        print(index_line_in_pattern, index_line_in_message)
#        print(line_in_pattern)
#        print(line_in_message)
        
        if (read_parse_state == 0):
            if(line_in_pattern == 'OFF_THE_RECORD_PROPERTY_NAME_CONSTANT'):
                read_parse_state = 1
                index_line_in_pattern += 1
                item_parsed_name = None
                item_parsed_value = None
                parse_instruction_for_current_regex = None
            elif(line_in_pattern == 'OFF_THE_RECORD_SKIP_LINE'):
                index_line_in_pattern += 1
                index_line_in_message += 1
            else:
                print("Error: code expects declaration of property in parser pattern")
        elif (read_parse_state == 1):
            read_parse_state = 2
            index_line_in_pattern += 1
            item_parsed_name = line_in_pattern
        elif (read_parse_state == 2):
            if(line_in_pattern == 'OFF_THE_RECORD_PROPERTY_VALUE_FIRST_OCCURANCE'):
                read_parse_state = 3
                index_line_in_pattern += 1
                parse_instruction_for_current_regex = line_in_pattern
            elif(line_in_pattern == 'OFF_THE_RECORD_PROPERTY_VALUE_FIRST_OCCURANCE_NO_NEW_LINE'):
                read_parse_state = 3
                index_line_in_pattern += 1
                parse_instruction_for_current_regex = line_in_pattern
            elif(line_in_pattern == 'OFF_THE_RECORD_PROPERTY_VALUE_AFTER_SPECIFIC_PREFIX'):
                read_parse_state = 3
                index_line_in_pattern += 1
                parse_instruction_for_current_regex = line_in_pattern
            elif(line_in_pattern == 'OFF_THE_RECORD_PROPERTY_VALUE_AFTER_SPECIFIC_PREFIX_FIRST_OCCURANCE_OUT_OF_MANY_LINES'):
                read_parse_state = 3
                index_line_in_pattern += 1
                parse_instruction_for_current_regex = line_in_pattern
            elif(line_in_pattern == 'OFF_THE_RECORD_PROPERTY_VALUE_BETWEEN_PREFIX_AND_SUFFIX'):
                read_parse_state = 3
                index_line_in_pattern += 1
                parse_instruction_for_current_regex = line_in_pattern
            elif(line_in_pattern == 'OFF_THE_RECORD_PROPERTY_VALUE_BETWEEN_PREFIX_AND_SUFFIX_NO_NEW_LINE'):
                read_parse_state = 3
                index_line_in_pattern += 1
                parse_instruction_for_current_regex = line_in_pattern
            else:
                print("Error: code expects in further instruction in parser")
        elif (read_parse_state == 3):
            flag_error_in_parse = False
            if(check_if_str_regex_pattern(line_in_pattern)):
                if(parse_instruction_for_current_regex == 'OFF_THE_RECORD_PROPERTY_VALUE_FIRST_OCCURANCE'):
                    read_parse_state = 0
                    index_line_in_pattern += 1
                    index_line_in_message += 1
                    item_parsed_value = re.search(line_in_pattern, line_in_message).group()
                elif(parse_instruction_for_current_regex == 'OFF_THE_RECORD_PROPERTY_VALUE_FIRST_OCCURANCE_NO_NEW_LINE'):
                    read_parse_state = 0
                    index_line_in_pattern += 1
                    item_parsed_value = re.search(line_in_pattern, line_in_message).group()
                elif(parse_instruction_for_current_regex == 'OFF_THE_RECORD_PROPERTY_VALUE_AFTER_SPECIFIC_PREFIX_FIRST_OCCURANCE_OUT_OF_MANY_LINES'):
                    read_parse_state = 0
                    index_line_in_pattern += 1
                    item_parsed_value = line_in_message.replace(re.search(line_in_pattern, line_in_message).group(),'')
                    while (re.match(line_in_pattern, lines_message_relevant[index_line_in_message]) != None):
                        index_line_in_message += 1
                elif(parse_instruction_for_current_regex == 'OFF_THE_RECORD_PROPERTY_VALUE_AFTER_SPECIFIC_PREFIX'):
                    read_parse_state = 0
                    index_line_in_pattern += 1
                    index_line_in_message += 1
                    item_parsed_value = line_in_message.replace(re.search(line_in_pattern, line_in_message).group(),'')
                elif(parse_instruction_for_current_regex == 'OFF_THE_RECORD_PROPERTY_VALUE_BETWEEN_PREFIX_AND_SUFFIX'):
                    read_parse_state = 0
                    index_line_in_pattern += 1
                    index_line_in_message += 1
                    item_parsed_value = line_in_message.replace(re.search(line_in_pattern, line_in_message).group(),'')
                    line_in_pattern = lines_parse_pattern[index_line_in_pattern]
                    item_parsed_value = item_parsed_value.replace(re.search(line_in_pattern, item_parsed_value).group(),'')
                    
                    index_line_in_pattern += 1
                elif(parse_instruction_for_current_regex == 'OFF_THE_RECORD_PROPERTY_VALUE_BETWEEN_PREFIX_AND_SUFFIX_NO_NEW_LINE'):
                    read_parse_state = 0
                    index_line_in_pattern += 1
                    item_parsed_value = line_in_message.replace(re.search(line_in_pattern, line_in_message).group(),'')
                    line_in_pattern = lines_parse_pattern[index_line_in_pattern]
                    item_parsed_value = item_parsed_value.replace(re.search(line_in_pattern, item_parsed_value).group(),'')
                    index_line_in_pattern += 1
                if (not flag_error_in_parse):
                    result_dict[item_parsed_name] = item_parsed_value
    #                print(result_dict)
            else:
                print("Error: code expects regex pattern")
    return result_dict

def message_parse_by_identified_pattern_by_text_lines(lines, pattern):
    lines_message_relevant = lines
    lines_parse_pattern = pattern
    
    read_parse_state = 0
    index_line_in_pattern = 0
    index_line_in_message = 0
    item_parsed_name = None
    item_parsed_value = None
    parse_instruction_for_current_regex = None
    result_dict = {}
    
    
    while ((index_line_in_pattern < 2001) and (index_line_in_pattern < len(lines_parse_pattern)) and (index_line_in_message < len(lines_message_relevant))):
        line_in_pattern = lines_parse_pattern[index_line_in_pattern]
        line_in_message = lines_message_relevant[index_line_in_message]
        print(index_line_in_pattern, index_line_in_message)
        print(line_in_pattern)
        print(line_in_message)
        print(result_dict)
        
        if (read_parse_state == 0):
            if(line_in_pattern == 'OFF_THE_RECORD_PROPERTY_NAME_CONSTANT'):
                read_parse_state = 1
                index_line_in_pattern += 1
                item_parsed_name = None
                item_parsed_value = None
                parse_instruction_for_current_regex = None
            elif(line_in_pattern == 'OFF_THE_RECORD_SKIP_LINE'):
                index_line_in_pattern += 1
                index_line_in_message += 1
            else:
                print("Error: code expects declaration of property in parser pattern")
        elif (read_parse_state == 1):
            read_parse_state = 2
            index_line_in_pattern += 1
            item_parsed_name = line_in_pattern
        elif (read_parse_state == 2):
            if(line_in_pattern == 'OFF_THE_RECORD_PROPERTY_VALUE_FIRST_OCCURANCE'):
                read_parse_state = 3
                index_line_in_pattern += 1
                parse_instruction_for_current_regex = line_in_pattern
            elif(line_in_pattern == 'OFF_THE_RECORD_PROPERTY_VALUE_FIRST_OCCURANCE_NO_NEW_LINE'):
                read_parse_state = 3
                index_line_in_pattern += 1
                parse_instruction_for_current_regex = line_in_pattern
            elif(line_in_pattern == 'OFF_THE_RECORD_PROPERTY_VALUE_AFTER_SPECIFIC_PREFIX'):
                read_parse_state = 3
                index_line_in_pattern += 1
                parse_instruction_for_current_regex = line_in_pattern
            elif(line_in_pattern == 'OFF_THE_RECORD_PROPERTY_VALUE_AFTER_SPECIFIC_PREFIX_FIRST_OCCURANCE_OUT_OF_MANY_LINES'):
                read_parse_state = 3
                index_line_in_pattern += 1
                parse_instruction_for_current_regex = line_in_pattern
            elif(line_in_pattern == 'OFF_THE_RECORD_PROPERTY_VALUE_BETWEEN_PREFIX_AND_SUFFIX'):
                read_parse_state = 3
                index_line_in_pattern += 1
                parse_instruction_for_current_regex = line_in_pattern
            elif(line_in_pattern == 'OFF_THE_RECORD_PROPERTY_VALUE_BETWEEN_PREFIX_AND_SUFFIX_OUT_OF_MANY_LINES'):
                read_parse_state = 3
                index_line_in_pattern += 1
                parse_instruction_for_current_regex = line_in_pattern
            elif(line_in_pattern == 'OFF_THE_RECORD_PROPERTY_VALUE_BETWEEN_PREFIX_AND_SUFFIX_NO_NEW_LINE'):
                read_parse_state = 3
                index_line_in_pattern += 1
                parse_instruction_for_current_regex = line_in_pattern
            elif(line_in_pattern == 'OFF_THE_RECORD_PROPERTY_VALUE_AFTER_SPECIFIC_PREFIX_FIRST_OCCURANCE'):
                read_parse_state = 3
                index_line_in_pattern += 1
                parse_instruction_for_current_regex = line_in_pattern
            elif(line_in_pattern == 'OFF_THE_RECORD_PROPERTY_VALUE_AFTER_SPECIFIC_PREFIX_FIRST_OCCURANCE_NO_NEW_LINE'):
                read_parse_state = 3
                index_line_in_pattern += 1
                parse_instruction_for_current_regex = line_in_pattern
            else:
                print("Error: code expects in further instruction in parser")
        elif (read_parse_state == 3):
            flag_error_in_parse = False
            if(check_if_str_regex_pattern(line_in_pattern)):
                if(parse_instruction_for_current_regex == 'OFF_THE_RECORD_PROPERTY_VALUE_FIRST_OCCURANCE'):
                    read_parse_state = 0
                    index_line_in_pattern += 1
                    index_line_in_message += 1
                    item_parsed_value = re.search(line_in_pattern, line_in_message).group()
                elif(parse_instruction_for_current_regex == 'OFF_THE_RECORD_PROPERTY_VALUE_FIRST_OCCURANCE_NO_NEW_LINE'):
                    read_parse_state = 0
                    index_line_in_pattern += 1
                    item_parsed_value = re.search(line_in_pattern, line_in_message).group()
                elif(parse_instruction_for_current_regex == 'OFF_THE_RECORD_PROPERTY_VALUE_AFTER_SPECIFIC_PREFIX_FIRST_OCCURANCE_OUT_OF_MANY_LINES'):
                    read_parse_state = 0
                    index_line_in_pattern += 1
                    item_parsed_value = line_in_message.replace(re.search(line_in_pattern, line_in_message).group(),'')
                    while (re.match(line_in_pattern, lines_message_relevant[index_line_in_message]) != None):
                        index_line_in_message += 1
                elif(parse_instruction_for_current_regex == 'OFF_THE_RECORD_PROPERTY_VALUE_AFTER_SPECIFIC_PREFIX'):
                    read_parse_state = 0
                    index_line_in_pattern += 1
                    index_line_in_message += 1
                    item_parsed_value = line_in_message.replace(re.search(line_in_pattern, line_in_message).group(),'')
                elif(parse_instruction_for_current_regex == 'OFF_THE_RECORD_PROPERTY_VALUE_BETWEEN_PREFIX_AND_SUFFIX'):
                    read_parse_state = 0
                    index_line_in_pattern += 1
                    index_line_in_message += 1
                    item_parsed_value = line_in_message.replace(re.search(line_in_pattern, line_in_message).group(),'')
                    line_in_pattern = lines_parse_pattern[index_line_in_pattern]
                    item_parsed_value = item_parsed_value.replace(re.search(line_in_pattern, item_parsed_value).group(),'')
                    index_line_in_pattern += 1
                elif(parse_instruction_for_current_regex == 'OFF_THE_RECORD_PROPERTY_VALUE_BETWEEN_PREFIX_AND_SUFFIX_OUT_OF_MANY_LINES'):
                    read_parse_state = 0
                    index_line_in_pattern += 1
                    item_parsed_value = line_in_message.replace(re.search(line_in_pattern, line_in_message).group(),'')
                    line_in_pattern_temp = line_in_pattern
                    line_in_pattern = lines_parse_pattern[index_line_in_pattern]
                    item_parsed_value = item_parsed_value.replace(re.search(line_in_pattern, item_parsed_value).group(),'')
                    temp_item_parsed_value = item_parsed_value
                    while (temp_item_parsed_value != None):
                        try:
                            temp_item_parsed_value = lines_message_relevant[index_line_in_message].replace(re.search(line_in_pattern_temp, lines_message_relevant[index_line_in_message]).group(),'')
                            temp_item_parsed_value = temp_item_parsed_value.replace(re.search(line_in_pattern, temp_item_parsed_value).group(),'')
                            index_line_in_message += 1
                        except:
                            temp_item_parsed_value = None
                    index_line_in_pattern += 1
                elif(parse_instruction_for_current_regex == 'OFF_THE_RECORD_PROPERTY_VALUE_BETWEEN_PREFIX_AND_SUFFIX_NO_NEW_LINE'):
                    read_parse_state = 0
                    index_line_in_pattern += 1
                    item_parsed_value = line_in_message.replace(re.search(line_in_pattern, line_in_message).group(),'')
                    line_in_pattern = lines_parse_pattern[index_line_in_pattern]
                    item_parsed_value = item_parsed_value.replace(re.search(line_in_pattern, item_parsed_value).group(),'')
                    index_line_in_pattern += 1
                elif(parse_instruction_for_current_regex == 'OFF_THE_RECORD_PROPERTY_VALUE_AFTER_SPECIFIC_PREFIX_FIRST_OCCURANCE'):
                    read_parse_state = 0
                    index_line_in_pattern += 1
                    index_line_in_message += 1
                    item_parsed_value = line_in_message.replace(re.search(line_in_pattern, line_in_message).group(),'')
                    line_in_pattern = lines_parse_pattern[index_line_in_pattern]
                    re.search(line_in_pattern, item_parsed_value).group()
                    item_parsed_value = re.search(line_in_pattern, item_parsed_value).group()
                    index_line_in_pattern += 1
                elif(parse_instruction_for_current_regex == 'OFF_THE_RECORD_PROPERTY_VALUE_AFTER_SPECIFIC_PREFIX_FIRST_OCCURANCE_NO_NEW_LINE'):
                    read_parse_state = 0
                    index_line_in_pattern += 1
                    item_parsed_value = line_in_message.replace(re.search(line_in_pattern, line_in_message).group(),'')
                    line_in_pattern = lines_parse_pattern[index_line_in_pattern]
                    re.search(line_in_pattern, item_parsed_value).group()
                    item_parsed_value = re.search(line_in_pattern, item_parsed_value).group()
                    index_line_in_pattern += 1
                if (not flag_error_in_parse):
                    result_dict[item_parsed_name] = item_parsed_value
    #                print(result_dict)
            else:
                print("Error: code expects regex pattern")
    return result_dict

def save_signal_to_log_file(signal, path_logfile):
    if (not (signal == '')):
        time_now = datetime.now()
        time_now_date = time_now.strftime("%Y-%m-%d")
        time_now_time = time_now.strftime("%H-%M-%S")
        file_object = open(path_logfile, 'a')
        file_object.write(str([time_now_date, time_now_time]) + '\n')
        file_object.write(str(signal) + '\n')
        file_object.close()

def process_parsed_signal(signal):
    save_signal_to_log_file(signal, path_output_signal_file)

def process_message_element(element, verbose = 0):
    ###
    ###  0 - useless info
    ###  1 - identified pattern
    ###  2 - unindentified pattern
    ###
    result = 0 if not filter_message_for_useless_info(element) else None
    if (result == 0):
        if (verbose >= 1):
            print('useless message')
        return result
    identified_pattern_name = message_check_fits_any_regex_pattern(element)
    result = 2 if identified_pattern_name == '' else 1
    if (result == 1):
        if (verbose >= 1):
            print('Identified pattern: {}'.format(identified_pattern_name))
        pattern_dict_item = get_patterns_dict_item_by_name(identified_pattern_name)
        result_parsed_message = None
        if ('parse_instruction' in pattern_dict_item):
            result_parsed_message = message_parse_by_identified_pattern(element, pattern_dict_item['parse_instruction'])
            process_parsed_signal(result_parsed_message)
            if (verbose >= 1):
                print('Parsed message:')
                print(result_parsed_message)
        else:
            if (verbose >= 1):
                print('No parsing instruction for this pattern')
        return result
    if (result == 2):
        if (verbose >= 1):
            print('undentified pattern')
        unidentified_message = element.text.split('\n')[:-2]
        filepath_unidentified = path_unidentified_pattern_messages + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.txt'
        file=open(filepath_unidentified,'w')
        for message_items in unidentified_message:
            file.writelines(message_items+'\n')
        file.close()
        return result
    pass

def process_message_element_text_lines(lines, verbose = 0):
    ###
    ###  0 - useless info
    ###  1 - identified pattern
    ###  2 - unindentified pattern
    ###
    
    #### TO BE WRITTEN
#    result = 0 if not filter_message_for_useless_info(element) else None
#    if (result == 0):
#        if (verbose >= 1):
#            print('useless message')
#        return result
#    identified_pattern_name = message_check_fits_any_regex_pattern(element)
#    result = 2 if identified_pattern_name == '' else 1
    print(1)
    identified_pattern_name = message_check_fits_any_regex_pattern_by_text_lines(lines)
    print(2)
    result = 1
    if (result == 1):
        if (verbose >= 1):
            print('Identified pattern: {}'.format(identified_pattern_name))
        pattern_dict_item = get_patterns_dict_item_by_name(identified_pattern_name)
        result_parsed_message = None
        if ('parse_instruction' in pattern_dict_item):
#            result_parsed_message = message_check_fits_regex_specific_pattern_by_text_lines(lines, pattern_dict_item['parse_instruction'])
            result_parsed_message = message_parse_by_identified_pattern_by_text_lines(lines, pattern_dict_item['parse_instruction'])
            process_parsed_signal(result_parsed_message)
            if (verbose >= 1):
                print('Parsed message:')
                print(result_parsed_message)
        else:
            if (verbose >= 1):
                print('No parsing instruction for this pattern')
        return result
    if (result == 2):
        if (verbose >= 1):
            print('undentified pattern')
        unidentified_message = element.text.split('\n')[:-2]
        filepath_unidentified = path_unidentified_pattern_messages + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.txt'
        file=open(filepath_unidentified,'w')
        for message_items in unidentified_message:
            file.writelines(message_items+'\n')
        file.close()
        return result
    pass

def load_message_with_unidentified_pattern_from_filename(path):
    txt_file = open(path, "r")
    content_list = txt_file.readlines()
    for i in range(len(content_list)):
        content_list[i] = content_list[i].split('\n')[0].strip()
    return content_list

pattern_list = init_pattern_list(pattern_whitelist_path)
#driver.find_element_by_xpath("//div[@class='Message message-list-item last-in-group last-in-list own open shown']")
lastmessage = get_last_message_from_opened_chat_text_only(driver)
message_last_element = get_last_message_from_opened_chat_full_element(driver)
while (True):
    message_new_element = get_last_message_from_opened_chat_full_element(driver)
    if (not (message_last_element.text == message_new_element.text)):
        process_message_element(message_new_element, verbose = 1)
        message_last_element = message_new_element
    sleep(1)



pattern_list = init_pattern_list(pattern_whitelist_path)
path = "unknown_patterns/" + "2021-09-16-12-57-44.txt"
message_to_parse = load_message_with_unidentified_pattern_from_filename(path)
pattern_name = message_check_fits_any_regex_pattern_by_text_lines(message_to_parse)


pattern_list = init_pattern_list(pattern_whitelist_path)
pattern = pattern_list[-2]['parse_instruction']
message_parse_by_identified_pattern_by_text_lines(lines, pattern)