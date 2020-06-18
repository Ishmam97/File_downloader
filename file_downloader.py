# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 19:21:35 2020 by Ishmam 

@author: mynam
"""
import requests
import lxml.html as lh
import pandas as pd
import numpy as np
import PyPDF2
import tabula

def get_files_list(url):
    #Create a handle, page, to handle the contents of the website
    page = requests.get(url)
    #Store the contents of the website under doc
    doc = lh.fromstring(page.content)
    #look for links in the website
    tree = lh.fromstring(page.text)
    links = []
    for link_element in tree.xpath('//td//a')[1:]:
        links.append(link_element.get('href'))
    return links

def save_list(li):
    with open('FilesList.txt', 'w') as filehandle:
        for listitem in li:
            filehandle.write('%s\n' % listitem)
        print('List saved as FilesList.txt')

def load_list(): 
    lines = []
    with open('FilesList.txt', 'r') as filehandle:        
        lines = [line[:-1] for line in filehandle]
    return lines

def download_file(f):
    db_url = "https://www.iedcr.gov.bd/website/images/files/nCoV/"
    url = db_url + f
    response = requests.get(url)
    file_name = url.split('/')[-1:][0]
    with open(file_name, 'wb') as f:
        f.write(response.content)
        print(file_name +' saved!')

def get_new_files(url):
    links = get_files_list(url)
    #check for updates
    old = load_list()
    updates = []
    for item in links :    
        if item not in old:
            updates.append(item)
    #download new files in site
    for item in updates:
        download_file(item)
    #save current list
    save_list(links)
    print("new files from website saved")

def get_latest_dl(): #get file name from downloads list
    with open('FilesList.txt', 'r') as filehandle:        
        lines = [line for line in filehandle]
    return lines[0].split()[0]


def pdf_to_csv(file = get_latest_dl()): #input pdf name or by default uses latest file
    df = tabula.read_pdf(file, pages = [1, 2])#does not read first table
    final = df[1]
    final.columns = ['Location' , 'Total']
    for idx , dfa in enumerate(df[2:]):
        x = dfa[:].values
        x = np.append(x, [final.columns[0] , final.columns[1]])
        dataset = pd.DataFrame({final.columns[0]: x[0:-2:2], final.columns[1]: x[1:-2:2]})
        final = pd.concat([final , dataset])

    final = final.reset_index(drop = True)

    final.to_csv('corona.csv' , index = False)
    print('saved as corona.csv')

if __name__ == '__main__':
    url = 'enter url here'
    get_new_files(url)