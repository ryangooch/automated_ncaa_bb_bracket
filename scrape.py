# -*- coding: utf-8 -*-

"""
Scripts to download the various metrics
"""

import requests
import time
import re

import numpy as np
import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver

def principal_period(s):
    """
    This helps to remove the repeating strings in some team names in ESPN BPI
    """
    i = (s+s).find(s, 1, -1)
    return None if i == -1 else s[:i]

def download_kenpom():
    """
    utility to download kenpom metric data

    """
    URL = "https://kenpom.com/"
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'lxml')

    table = soup.find('table')
    rows = table.find_all('tr')

    ot_data = []
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        ot_data.append([ele for ele in cols if ele])

    ot_data = [x for x in ot_data if x]

    df_cols = ['Rk','Team','Conf','W-L','AdjEM','AdjO','AdjD','AdjT','Luck',
        'SOS']
    ot_data_cols_to_keep = [0,1,2,3,4,5,7,9,11,-2]

    ot_data = np.array(ot_data)

    kenpom_df = pd.DataFrame(
        ot_data[:,ot_data_cols_to_keep],
        columns = df_cols
    )

    cols_to_numeric = ['AdjEM','AdjEM','AdjO','AdjD','AdjT','Luck','SOS']
    
    for col in cols_to_numeric:
        kenpom_df[col] = kenpom_df[col].astype('float')
    
    kenpom_df.to_csv("csv_files/kenpom.csv")

def download_dokent():
    """
    utility to download dokter entropy metric data

    """
    URL = "http://www.timetravelsports.com/r2019.CBB"
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'lxml')

    data = []
    
    for row in soup.p.contents[0].split('\n'):
        current_line = row.split()
        if len(current_line) == 8:
            data.append(current_line)
        elif len(current_line) == 9:
            team_name = "%s %s" % (current_line[1],current_line[2])
            current_line.pop(1)
            current_line.pop(1)
            current_line.insert(1,team_name)
            data.append(current_line)
        elif len(current_line) == 10:
            team_name = "%s %s %s" % (\
                current_line[1],current_line[2],current_line[3])
            current_line.pop(1)
            current_line.pop(1)
            current_line.pop(1)
            current_line.insert(1,team_name)
            data.append(current_line)
        else:
            continue

    data_np = np.array(data[1:])

    # Get column names    
    columns = data[0]

    columns.pop(3)
    columns.insert(0, 'Rk')

    # Rename team to Team to match my convention throughout
    columns.pop(1)
    columns.insert(1, 'Team')

    dokent_df = pd.DataFrame(
        data_np,
        columns = columns
    )

    cols_to_numeric = ['Rk','w','l','power','sched','offen','defen']

    for col in cols_to_numeric:
        dokent_df[col] = dokent_df[col].astype('float')

    # this could end up being a problem
    dokent_df.to_csv("csv_files/dokent.csv")

def download_bpi():
    """
    utility to download BPI metric data

    """
    URL = "http://www.espn.com/mens-college-basketball/bpi/_/view/bpi"
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'lxml')

    table = soup.find_all('table')[1]
    rows = table.find_all('tr')

    data = []
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])

    data = [x for x in data if x]

    data_np = np.array(data)

    for page in range(2,9):
        URL = 'http://www.espn.com/mens-college-basketball/bpi/_/view/bpi/page/%d' % page
        r = requests.get(URL)
        soup = BeautifulSoup(r.text, 'lxml')

        table = soup.find_all('table')[1]
        rows = table.find_all('tr')

        data = []
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])

        data = [x for x in data if x]

        data_np_temp = np.array(data)
        
        data_np = np.append(data_np,data_np_temp,axis=0)
        
        # don't blitz the API
        time.sleep(3)

    # go through list, if you find a match, drop text after match
    data_non_repeats = [ principal_period(s) if principal_period(s) is not None else s for s in data_np[:,1] ]
    team_str = []

    lowerUPPER_str_pattern = re.compile('[a-z]{1}[A-Z]')

    # these correspond to Massey naming convention
    edge_cases = {
        'DePaulDEP':'DePaul',
        'Florida A&MFAMU':'Florida A&M',
        'Alabama A&MAAMU':'Alabama A&M',
        'IUPUIIUPU':'IUPUI',
        'Texas A&MTA&M':'Texas A&M',
        'Prairie View A&MPV':'Prairie View A&M',
        'Texas A&M-CCAMCC':'TAM C. Christi',
        'North Carolina A&TNCAT':'NC A&T',
        'Miami (OH)M-OH':'Miami OH',
        'St. Francis (PA)SFPA':'St Francis PA',
        'St. Francis (BKN)SFBK':'St Francis NY',
        'Loyola (MD)L-MD':'Loyola MD'
    }

    for team in data_non_repeats:
        # gonna have to do edge cases separately
        if team in edge_cases.keys():
            team_str.append(edge_cases[team])
            
        elif lowerUPPER_str_pattern.search(team) is not None:
            first_to_cut = lowerUPPER_str_pattern.search(team).span()[0] + 1
            team_str.append(team[:first_to_cut])
        
        else:
            team_str.append(team)
        
    data_np[:,1] = np.array(team_str)

    # add the columns and put in df. Drop rank change column
    df_cols = ['Rk','Team','Conf','W-L','BPI_OFF','BPI_DEF','BPI']
    data_cols_to_keep = list(range(7))

    bpi_df = pd.DataFrame(
        data_np[:,data_cols_to_keep],
        columns = df_cols
    )

    cols_to_numeric = ['Rk','BPI_OFF','BPI_DEF','BPI']

    for col in cols_to_numeric:
        bpi_df[col] = bpi_df[col].astype('float')

    bpi_df.to_csv("csv_files/bpi.csv") 
    
def download_massey():
    """
    Download raw ratings from https://www.masseyratings.com/cb/ncaa-d1/ratings
    """
    URL = "https://www.masseyratings.com/cb/ncaa-d1/ratings"

    browser = webdriver.Firefox()
    browser.get(URL)
    html = browser.page_source

    soup = BeautifulSoup(html, 'lxml')

    table = soup.find(id='mytable0')

    rows = table.find_all('tr')

    massey_data = []
    for row in rows[2:]:
        line = []
        if row and row.find_all('td'):
            line.append(row.find_all('td')[0].find('a').contents[0]) # Team
            line.append(row.find_all('td')[1].contents[0]) # Record
            line.append(row.find_all('td')[3].contents[1].contents[0]) # Rat
            line.append(row.find_all('td')[4].contents[1].contents[0])# Pwr
            line.append(row.find_all('td')[5].contents[1].contents[0])# Off
            line.append(row.find_all('td')[6].contents[1].contents[0])# Def
            line.append(row.find_all('td')[8].contents[1].contents[0])# SoS
            massey_data.append(line)
        else:
            continue

    df_cols = ['Team','W-L','Rat','Pwr','Off','Def','SoS']

    massey_data = np.array(massey_data)

    massey_df = pd.DataFrame(
        massey_data,
        columns = df_cols
    )

    cols_to_numeric = ['Rat','Pwr','Off','Def','SoS']

    for col in cols_to_numeric:
        massey_df[col] = massey_df[col].astype('float')

    massey_df.to_csv("csv_files/massey.csv")