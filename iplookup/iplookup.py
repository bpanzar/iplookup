'''
Module performs batch country lookup of IP addresses.

To use:
import iplookup

df = pd.DataFrame({'IP': ['10.0.0.0', '107.1.0.0', '129.0.2.0', '127.0.0.1']})
iplookup = iplookup.iplookup()
df['Country'] = iplookup(df, 'IP Address)
'''

import datetime as dt
import io
import os
import requests

import netaddr
import pandas as pd
import zipfile

DOWNLOAD_TOKEN = 'xxxxxxxxxxxxxxxxxx' # Insert your API key here.
DATABASE_CODE = 'DB1LITEIPV6'
URL = f'http://www.ip2location.com/download/?token={DOWNLOAD_TOKEN}&file={DATABASE_CODE}'
PRIVATE_IPS = ['10.0.0.0', '172.16.0.0', '169.254.0.0', '192.168.0.0']

class iplookup(object):

    def __init__(self, db_path=None):
        '''
        If IP lookup database is expired (from last month) download the new database.
        Load the IP lookup database, calculate the IPv4 offset, set the private
        and local host IP ranges.


        Parameters
        ----------
        db_path : str
            Location where you want the database to be stored.  Actual database location
            will be db_path + /db

        Attributes
        ----------
        month : int
            Current month.
        last_month : int
            Last month.
        db_path : os.path
            Path to the database folder.
        db_month : int
            Month of the IP lookup database.
        offset : float
            An offset is needed to convert decimal values of IPv4 because this is an IPv6 database.
        '''

        self.month = dt.date.today().month 

        today = dt.date.today()
        self.last_month = (today.replace(day=1) - dt.timedelta(days=1)).month 

        if db_path:
            self.db_path = os.path.join(db_path, 'db')
        else:
            self.db_path = os.path.join(os.getcwd(), 'db')

        # Create db/ folder that stores IP address-country database
        if not os.path.exists(self.db_path):
            os.makedirs('db')

            with open(os.path.join(self.db_path, '.db_month'), 'w') as f:

                self.db_month = self.last_month
                f.write(str(self.db_month))

        # If db/ exists, load db month
        else:
            with open(os.path.join(self.db_path, '.db_month'), 'r') as f:
                self.db_month = int(f.readline())

        # If db month == last month, load new db data
        if self.last_month == self.db_month:
            print('Downloading new database.')

            resp = requests.get(URL, verify=False)
            z = zipfile.ZipFile(io.BytesIO(resp.content))
            z.extractall(path='db')

            with open(os.path.join(self.db_path, '.db_month'), 'w') as f:
                self.db_month = self.month
                f.write(str(self.db_month))

        # Open database
        with open('db/IP2LOCATION-LITE-DB1.IPV6.CSV') as f:
            self.ip_df = pd.read_csv(f, 
                                     names=['IP_Start_dec', 
                                            'IP_End_dec', 
                                            'Code', 
                                            'Country'], 
                                     dtype={'IP_Start_dec':float,
                                            'IP_End_dec':float, 
                                            'Code':str, 
                                            'Country':str})

        # Offset = (first decimal value of first US range) - (decimal value of 1.0.0.0 address)
        self.offset = (self.ip_df[self.ip_df['Code'] != '-'].iloc[0]['IP_Start_dec']
                  - int(netaddr.IPAddress('1.0.0.0')))

        # Set values for private IPs and local host
        for ip in PRIVATE_IPS:
            (self.ip_df.loc[self.ip_df.IP_Start_dec == (self.offset 
                                                        + int(netaddr.IPAddress(ip))), 'Country'] 
                                                        = 'Private/Internal')

        (self.ip_df.loc[self.ip_df.IP_Start_dec == (self.offset 
                                                   + int(netaddr.IPAddress('127.0.0.0'))), 'Country'] 
                                                   = 'Local Host')

    def get_countries(self, df, ipcolumn):
        ''' 
        Parameters
        ----------
        df : pandas DataFrame
        ipcolumn : str
            Column containing IP addresses

        Returns
        -------
        Country ('United States') : Matching country location of IP address.
        'Error' : Unable to calculate decimal value of IP address.
        'Unknown' : IP address not found in database.
        'Private/Internal' : IP address within private address block.
        'Local Host' : IP address within local host block.
        '-' : IP address not associated with a country or other known block.
        '''
        
        self.ipcolumn = ipcolumn

        return df.apply(self.get_country, axis=1)

    def get_country(self, row):
        ''' 
        Converts IP address to decimal and returns matching country from database.

        row : pandas Series, row of the original DataFrame 
        '''

        ip = row[self.ipcolumn]

        try:
            if '.' in ip:
                ip_dec = float(int(netaddr.IPAddress(ip))) + self.offset
            elif ':' in IP:
                ip_dec = float(int(netaddr.IPAddress(ip)))
            else:
                ip_dec = 0
        except Exception as e:
            print(e)
            return 'Error'

        temp_row = (self.ip_df[(self.ip_df['IP_Start_dec'] <= ip_dec) & (self.ip_df['IP_End_dec'] 
                                                                         >= ip_dec)])

        if len(temp_row) == 0:
            return 'Unknown'
            
        else:
            return temp_row.iloc[0]['Country']