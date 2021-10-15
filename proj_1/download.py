import os
import re
import io
import logging

from zipfile import ZipFile
from bs4 import BeautifulSoup
import requests
import gzip
import pickle
from pickle import load, dump
from numpy import array, arange, genfromtxt, concatenate

logger = logging.getLogger(__name__)


class DataDownloader():
    """
    This class is using to download and parse data about
    accidents on traffics in Czech Republic

    Args:
        url (str) - URL to website, where the data must be obtained
        folder (str) - a name of folder, where downloaded data will be saved
        cache_filename (str) - a template for filename,
                               where the parsed data will be saved
    """
    re_zip = re.compile(r'^.*datagis.*([0-1]\d-|-rok-)?(\d{4})\.zip')
    region_file = {
        'PHA': '00.csv',
        'STC': '01.csv',
        'JHC': '02.csv',
        'PLK': '03.csv',
        'ULK': '04.csv',
        'HHK': '05.csv',
        'JHM': '06.csv',
        'MSK': '07.csv',
        'OLK': '14.csv',
        'ZLK': '15.csv',
        'VYS': '16.csv',
        'PAK': '17.csv',
        'LBK': '18.csv',
        'KVK': '19.csv',
    }
    header = [
        'ID', 'Druh komunikace', 'Cislo komunikace',
        'Datum', 'Den', 'Cas', 'Druh nehody', 
        'Druh srazky', 'Druh prekazky', 'Charakter',
        'Zavineni', 'Alkohol pritomen', 'Hlavni priciny',
        'Usmrceno osob', 'Tezce zraneno osob', 'Lehce zraneno osob',
        'Celkova skoda', 'Druh povrchu', 'Stav povrchu', 'Stav komunikace',
        'Povetrnostni podminky', 'Viditelnost', 'Rozhledove pomery',
        'Deleni komunikace', 'Situovani', 'Rizeni provozu',
        'Mistni uprava', 'Specificka mista', 'Smerove pomery', 'Pocet vozidel',
        'Misto nehody', 'Druh krizujici komunikace', 'Druh vozidla',
        'Vyrobni znacka vozidla', 'Rok vyroby', 'Charakteristika vozidla', 
        'Smyk', 'Vozidlo po nehode', 'Unik hmot', 'Zpusob vyprosteni', 
        'Smer jizdy vozidla', 'Skoda na vozidle',
        'Kategorie ridice', 'Stav ridice', 'Vnejsi ovlivneni ridice',
        'a', 'b', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'n',
        'o', 'p', 'q', 'r', 's', 't', 'Lokalita', 'Region'
    ]
    types = [
        'U12', 'int8', 'U3', 'U10', 'int8', 'U5',
        'int8', 'int8', 'int8', 'int8', 'int8', 'int8',
        'int16', 'int8', 'int8', 'int8', 'int16', 'int8',
        'int8', 'int8', 'int8', 'int8', 'int8', 'int8', 
        'int8', 'int8', 'int8', 'int8', 'int8', 'int8',
        'int8', 'int8', 'int8', 'int8', 'int8', 'int8',  
        'int8', 'int8', 'int8', 'int8', 'int8', 'int16',
        'int8', 'int8', 'int8', 'U16', 'U16', 'U16', 'U16',
        'U16', 'U16', 'U50', 'U25', 'U16', 'U20', 'U16',
        'U16', 'U16', 'U20', 'U16', 'U6', 'U6', 'U20', 'U20', 
    ]

    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/",
                 folder="data", cache_filename="data_{}.pkl.gz"):
        
        self.__folder = os.path.join(os.getcwd(), folder)
        self.__url = url
        self.__cache = cache_filename
        self.__mem_data = dict()

    def __get_latest_zip_urls(self, links):
        """Get names of zip files with the most actual information

        Args:
            links (list) - a list of links with possible names of zip files

        Generates:
            str which contain zip name
        """       
        last_match = None

        for link in links:
            match = self.re_zip.search(link['href'])
            
            if not match:
                continue
            if not last_match:
                last_match = match
                continue

            # check if the current url's year has changed 
            if last_match.group(2) < match.group(2):
                # check if months (or 'rok') exists and compare them
                if (last_match.group(1) and match.group(1)
                        and last_match.group(1) > match.group(1)):
                    yield last_match.group(0)
                # else compare urls as a whole        
                elif last_match.group(0) > match.group(0):
                    yield last_match.group(0)
            last_match = match
        
        if last_match:
            yield last_match.group(0)

    def __parse_zip_file(self, zip_fname, region):
        """Function for parsing zip file

        Args:
            zip_fname (str) - name of a current zip file
            region (str) - name of region for parsing
        
        Returns:
            nd_array with parsed and converted data
        """
        def converter(idx):
            def wrap(data):
                data = data.replace('\"', '').replace(r',', r'.')

                if self.types[idx] == 'int8' and data == 'XX':
                    return '0'

                if data == '':
                    return '' if 'U' in self.types[idx] else '0'
                return data

            return wrap

        zip_fname = os.path.join(self.__folder, zip_fname)

        with ZipFile(zip_fname, 'r') as zip_file:
            csv_name = self.region_file[region]

            if csv_name not in zip_file.namelist():
                logger.warning('%s is not in %s', region, zip_file.filename)
                return tuple()
            
            converters = {idx: converter(idx) for idx in arange(0, 64)}

            kwargs = {
                'fname': zip_file.open(csv_name, 'r'),
                'delimiter': ';',
                'encoding': 'cp1250',
                'usecols': arange(0, 64),
                'dtype': 'U23',
                'converters': converters,
            }

            data = genfromtxt(**kwargs).T
            for idx, data_col in enumerate(data):
                data_col = data_col.astype(self.types[idx])

            return concatenate((data, array([[region]*data.shape[1]])), axis=0)

    def __get_region_data(self, region):
        """Function for getting and saving data

        If data were already read, they would be gotten from RAM,
        if data were cached, they would be gotten from cache file,
        otherwise it would parse it using parse_region_data function.

        Args:
            region (str) - name of region for parsing
        
        Returns:
            tuple (header, data) 
        """
        if region in self.__mem_data:
            return self.__mem_data['region']

        cache_path = os.path.join(self.__folder, self.__cache.format(region))
        if os.path.exists(cache_path):
            return load(gzip.open(cache_path, 'rb'))

        data = self.parse_region_data(region)
        with gzip.open(cache_path, 'wb') as cache:
            dump(data, cache)
        
        self.__mem_data[region] = data
            
        return data

    def download_data(self):
        """Function for downloading zip files with data"""
        if not os.path.exists(self.__folder):
            os.mkdir(self.__folder)

        headers = {"User-Agent": "Chrome/70.0.3538.77"}
        respond = requests.get(url=self.__url, headers=headers)

        soup = BeautifulSoup(respond.text, 'html.parser')
        zip_urls = self.__get_latest_zip_urls(soup.find_all('a'))

        for zip_url in zip_urls:
            zip_file = requests.get(self.__url + zip_url, stream=True)

            # get the last pathname of a zip file and save it in the folder
            zip_fname = os.path.split(zip_url)[-1]
            zip_fname = os.path.join(self.__folder, zip_fname)

            with open(zip_fname, 'wb') as f:
                f.write(zip_file.content)

    def parse_region_data(self, region):
        """Function for getting and saving data

        Firstly, function will check if data were downloaded,
        thereafter it'll get data from downloaded zip files using
        function parse_zip_file

        Args:
            region (str) - name of region for parsing
        
        Returns:
            tuple (header, data) 
        """
        def folder_contains_zip():
            for fname in os.listdir(self.__folder):
                if self.re_zip.match(fname):
                    return True
                
                return False

        if not (os.path.exists(self.__folder) and folder_contains_zip()):
            self.download_data()

        if region not in self.region_file:
            logger.warning('%s is not in region list', region)
            return        

        return self.header, concatenate([
            self.__parse_zip_file(zip_fname, region)
            for zip_fname in os.listdir(self.__folder)
            if self.re_zip.search(zip_fname)
        ], axis=1)


    def get_list(self, regions=None):        
        if not regions:
            regions = [
                'PHA', 'STC', 'JHC', 'PLK', 'ULK', 
                'HHK', 'JHM', 'MSK', 'OLK', 'ZLK', 
                'VYS', 'PAK', 'LBK', 'KVK',
            ]

        return self.header, concatenate([
            self.__get_region_data(region)[1]
            for region in regions
        ], axis=1)

if __name__ == "__main__":
    data = DataDownloader().get_list(['PHA', 'STC', 'HHK'])
