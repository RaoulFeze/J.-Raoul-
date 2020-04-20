#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 00:52:36 2020

@author: Raoul
"""


from bs4 import BeautifulSoup
import requests
import pandas as pd
import requests_cache

#convert the postal codes into a csv format
Unformatted_postal_codes = pd.read_csv('postal_codes.txt')
Unformatted_postal_codes = Unformatted_postal_codes.transpose()
Unformatted_postal_codes.to_csv('formatted.csv', header = False)
formatted_postal_codes = pd.read_csv('formatted.csv')

#remove the whitespace 
postal_codes = []
for pc in formatted_postal_codes:
    postal_codes.append((pc.upper()).replace(' ', ''))

BASE_URL = 'https://www.whitepagescanada.ca/ab/edmonton/'

#Territory columns
territory_column_names = ['Name', 'Telephone','Telephone2', 'Street address', 'City', 'Region', 'Postal code']

#Tracking Sheet columns and rows
tracking_columns =['Postal Code', 'Number of House', 'Start Date', 'Completed Date', 'Publisher']
tracking_rows = []

#This function verifies that the current page is valid 
def validate_page(current_page):
    response = requests.get(current_page)
    postal_code_page = BeautifulSoup(response.content,'lxml')
    return postal_code_page.select_one('div.eleven.columns').select_one('tbody').select('tr')


for postal_code in postal_codes:
    requests_cache.install_cache('territory_cache',\
                                  backend='sqlite', expire_after=10)
        
    initial_page = BASE_URL + postal_code + '/'
    current_page = initial_page
    
    #valudates current page
    current_page_is_valid = validate_page(current_page)
    
    #initialises territory rows 
    territory_rows = []
    
    number_of_homes = 0
    page_number = 2
    while(current_page_is_valid):
        response = requests.get(current_page)
        page_content = BeautifulSoup(response.content, 'lxml')
        selected_content = page_content.select_one('div.eleven.columns').select_one('tbody').select('a.rsslink-m')
        
        for links in selected_content:
            data_row = []
            link = links.attrs['href']
            request_data = requests.get(link)
            retrieved_data = BeautifulSoup(request_data.content, 'lxml')
            selected_data = retrieved_data.select_one('div.eleven.columns').select('span')
            
            for data in selected_data:
               data_row.append(data.text)
              
            territory_rows.append((data_row))
            number_of_homes += 1
            
        current_page = initial_page + str(page_number) +'/'
        current_page_is_valid = validate_page(current_page)
        page_number += 1   
        
       
    tracking_rows.append((postal_code, number_of_homes, '', '',''))
    tracking_territories = pd.DataFrame(tracking_rows, columns = tracking_columns)
    tracking_territories.to_csv('Territoy Tracking.csv', encoding = 'utf-8', index = False)
    
    territories = pd.DataFrame(territory_rows, columns = territory_column_names)
    territories = territories.drop(['Telephone2'],axis=1)
    
    territories.to_csv('Territories/' + postal_code + '.csv', encoding = 'utf-8', index = False)
    