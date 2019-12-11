# IP Lookup Module
### This module takes a dataframe with a column of IP addresses and returns a series containing the country locations of the addresses.  IPv4 and IPv6 are supported.
<br/>
This module uses the IP2Location service to download the database.  The user must have registered for a free API key through their website: https://www.ip2hocation.com
<br/><br/>
Once the user acquires an API key, copy and paste the key string in the DOWNLOAD_TOKEN constant within the iplookup.py file.
<br/><br/>
The user can provide a filepath where the database will be stored or the module will create the 'db' folder containing the database in the current working directory.  To quickly use this module simply place the iplookup.py and __init__.py files in the same folder with your script.
<br/><br/>
This is an example of using the module:
<br/><br/>

![example.png](attachment:example.png)
