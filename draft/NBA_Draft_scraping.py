# Adapted form script used in ASTR 356 By Shane Fenske
#Adapted from: http://nyloncalculus.com/2015/09/07/nylon-calculus-101-data-scraping-with-python/
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

# url that we are scraping
url = "http://www.basketball-reference.com/draft/NBA_2014.html"

# this is the html from the given url
html = urlopen(url)

soup = BeautifulSoup(html, 'html5lib')

column_headers = [th.getText() for th in 
                  soup.findAll('tr', limit=2)[1].findAll('th')]

# # **NOTE** Some of the column headers (or names or labels) need to be renamed, but we won't be doing that until we scrape the date from 1966 and on.

# Scraping and cleaning the data from all previous drafts follows a similar procedure to the one we used for the 2014 draft. The main difference is that we have to to do it multiple times and then combine the data into one large `DataFrame` .
# 
# ###Scraping
# First lets create a URL template that will allow us to access the web page for each year.

url_template = "http://www.basketball-reference.com/draft/NBA_{year}.html"

# create an empty DataFrame
draft_df = pd.DataFrame()


for year in range(2002, 2016):  # for each year
    url = url_template.format(year=year)  # get the url
    
    html = urlopen(url)  # get the html
    soup = BeautifulSoup(html, 'html5lib') # create our BS object
    

    # get our player data
    data_rows = soup.findAll('tr')[2:] 
    player_data = [[td.getText() for td in data_rows[i].findAll('td')]
                for i in range(len(data_rows))]
    # Turn yearly data into a DatFrame
    year_df = pd.DataFrame(player_data, columns=column_headers)
    # create and insert the Draft_Yr column
    year_df.insert(0, 'Draft_Yr', year)
    
    # the id here which will be used for merging with other data sets is first letter of first name + Draft_Yr + pick number
    year_df['id'] = year_df['Player'].str[0] + year_df['Draft_Yr'].astype(str) + year_df['Pk'].astype(str)
    # Append to the big dataframe
    draft_df = draft_df.append(year_df, ignore_index=True)

# Convert data to proper data types
draft_df = draft_df.convert_objects(convert_numeric=True)

# Get rid of the rows full of null values
draft_df = draft_df[draft_df.Player.notnull()]

# Replace NaNs with 0s
draft_df = draft_df.fillna(0)

# Rename Columns
draft_df.rename(columns={'WS/48':'WS_per_48'}, inplace=True)
# Change % symbol
draft_df.columns = draft_df.columns.str.replace('%', '_Perc')
# Add per_G to per game stats
draft_df.columns.values[15:19] = [draft_df.columns.values[15:19][col] + 
                                  "_per_G" for col in range(4)]

# Changing the Data Types to int
draft_df.loc[:,'Yrs':'AST'] = draft_df.loc[:,'Yrs':'AST'].astype(int)

# Delete the 'Rk' column
draft_df.drop('Rk', axis='columns', inplace=True)

draft_df['Pk'] = draft_df['Pk'].astype(int) # change Pk to int

draft_df.isnull().sum() # No missing values in our DataFrame

draft_df.to_csv("draft_data_2002_to_2015.csv")
