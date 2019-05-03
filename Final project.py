import pandas as pd
import numpy as np
from datetime import datetime
from scipy.stats import chi2_contingency
import requests
import lxml.html
from time import sleep
from requests.exceptions import ConnectionError
from  geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from folium import plugins
import folium
import subprocess
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

# read file - shark_attacks.csv
df = pd.read_csv("D:/590-PR/final project/shark_attacks/attacks.csv",encoding = 'ISO-8859-1')
df = df[['Case Number', 'Date','Country', 'Area', 'Location','Activity','Sex ', 'Age', 'Injury', 'Fatal (Y/N)','Species ']]
df.rename(columns={'Case Number':'CaseNumber'}, inplace=True)

################################################  H1  #############################################
# H1: The temperature is related to the injury type(fatal or not)
print('*************** H1: The temperature is related to the injury type(fatal or not) ****************')
## data processing for hypothetical test
df['Date'] = df['Date'].fillna('***')
na_date_index = df[df.Date == '***'].index.tolist()
df = df.drop(na_date_index)
def date_prettify(date):
    '''
    >>> date_prettify("2018.06.03.b")
    '2018-06-03'
    '''
    date = str(date)
    if (len(date) == 10 and date[5:7]!='00' and date[8:10]!='00' and int(date[5:7])<=31 and int(date[5:7])>0 and int(date[8:10])<=31 and int(date[8:10])>0):
        if date[4] == '.' and date[7] == '.':
            return str(datetime.strptime(date,'%Y.%m.%d'))[0:10]
        elif date[4] == '-' and date[7] == '-':
            return str(datetime.strptime(date,'%Y-%m-%d'))[0:10]
        elif date[4] == '.' and date[7] == '-':
            return str(datetime.strptime(date,'%Y.%m-%d'))[0:10]
        elif date[4] == '-' and date[7] == '.':
            return str(datetime.strptime(date,'%Y-%m.%d'))[0:10]
    elif (len(date) == 12 and date[5:7]!='00' and date[8:10]!='00' and int(date[5:7])<=31 and int(date[5:7])>0 and int (date[8:10])<=31 and int(date[8:10])>0):
        date = date[0:10]
        if date[4] == '.' and date[7] == '.':
            return str(datetime.strptime(date,'%Y.%m.%d'))[0:10]
        elif date[4] == '-' and date[7] == '-':
            return str(datetime.strptime(date,'%Y-%m-%d'))[0:10]
        elif date[4] == '.' and date[7] == '-':
            return str(datetime.strptime(date,'%Y.%m-%d'))[0:10]
        elif date[4] == '-' and date[7] == '.':
            return str(datetime.strptime(date,'%Y-%m.%d'))[0:10]
    else:
        return np.nan
df['CaseNumber'] = df['CaseNumber'].apply(date_prettify)
df['CaseNumber'] = df['CaseNumber'].fillna('***')
na_CaseNumber_index = df[df.CaseNumber == '***'].index.tolist()
df = df.drop(na_CaseNumber_index)
df['Area'] = df['Area'].fillna('***')
na_Area_index = df[df.Area == '***'].index.tolist()
df = df.drop(na_Area_index)
def location_prettify(location):
    '''
    >>> location_prettify("Oceanside, San Diego County")
    'San Diego'
    '''
    temp_loc = str(location)
    if ',' in temp_loc:
        temp_loc = temp_loc.split(',')[-1].strip()
        if 'County' in temp_loc:
            temp_loc = temp_loc[:-7]
        return temp_loc.strip()
    elif ',' not in temp_loc:
        return temp_loc
df['Location'] = df['Location'].apply(location_prettify)
df_USA = df[df['Country'] == 'USA'][['CaseNumber','Country','Area','Location','Fatal (Y/N)']] # df_USA only contain the attacks in USA
df_USA.reset_index(drop=True, inplace=True)
def area_prettify(area):
    '''
    >>> area_prettify("Illinois")
    'IL'
    '''
    key = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','Florida','Georgia','Hawaii','Idaho',
           'Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi',
           'Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota',
           'Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont',
           'Virginia','Washington','West Virginia','Wisconsin','Wyoming']
    value = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS',
             'MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV',
             'WI','WY']
    dict_Area = dict(zip(key, value))
    temp_area = str(area).strip()
    if temp_area in dict_Area:
        temp_area = dict_Area[temp_area]
        return temp_area
    elif temp_area not in dict_Area:
        return np.nan
df_USA['Area'] = df_USA['Area'].apply(area_prettify)


def get_temperature(state, city, date):
    """
     based on state list, city list, and data list, generate url to get the temperature from the website
    :param state: list of state
    :param city: list of city
    :param date: list of date
    :return: nested list of temperatures
    >>> state=['IL','IL']
    >>> city=['Urbana','Chicago']
    >>> date=['2019-05-01','2019-04-29']
    >>> get_temperature(state,city,date)
    200
    IL Urbana ['54.8']
    200
    IL Chicago ['46.8']
    [['54.8'], ['46.8']]


    """
    temperature = []
    for i, j, n in zip(state, city, date):
        url_1 = "https://www.almanac.com/weather/history/"
        url = url_1 + i + '/' + j + '/' + n
        tree = None
        while tree is None:
            try:
                r = requests.get(url)
                print(r.status_code)
                if (r.status_code == 200):
                    tree = lxml.html.fromstring(r.content)
                    content = tree.xpath(
                        '//tr[@class="weatherhistory_results_datavalue temp"]/td/p/span[@class="value"]/text()')
                    temperature.append(content)
                    sleep(5)
                    break
                elif (r.status_code == 429):
                    tree = None
                    sleep(5)
                else:
                    content = ['NaN']
                    temperature.append(content)
                    break
            except(ConnectionError, ConnectionRefusedError) as e:
                print('Error retrieving web page.  Retrying in 10 seconds...')
                sleep(10)

        print(i, j, content)
    return temperature

list_date = list(df_USA.CaseNumber)
list_state = list(df_USA.Area)
list_city = list(df_USA.Location)
temp=get_temperature(list_state,list_city,list_date)

# because we need to request many url from the website which might crash sometimes, it's better to store the temperature
# in the file to avoid request again, we can use the temperature from the txt directly
with open('temperature.txt', 'w') as f:
    for item in temp:
        f.write("%s\n" % item)


def coordinate(list_city):
    """
    based on list of city, get the longitude and latitude
    :param list_city: a list of city
    :return: a dataframe has tree column city, latitude, and longitude
    >>> city= ['Urbana','Chicago']
    >>> coordinate(city)
    Urbana latitude is : 40.1117174 longtitude is: -88.207301
    Chicago latitude is : 41.8755616 longtitude is: -87.6244212
          city    latitude    longitude
    0   Urbana  40.1117174   -88.207301
    1  Chicago  41.8755616  -87.6244212

    """
    geolocator = Nominatim(timeout=10, user_agent="my-application")
    country = "US"

    coordinate = []
    for i in list_city:
        if i != 'nan' and i != '':
            try:
                loc = geolocator.geocode(i + ',' + country)
                if type(loc) != type(None):
                    coordinate.append(i)
                    coordinate.append(float(loc.latitude))
                    coordinate.append(float(loc.longitude))
                    print(i, "latitude is :", float(loc.latitude), "longtitude is:", float(loc.longitude))
                    sleep(1)
            except GeocoderTimedOut as e:
                print("Error: geocode failed on input %s with message %s" % (loc, e))
    df = pd.DataFrame(np.array(coordinate).reshape(-1, 3))
    df.columns = ["city", "latitude", "longitude"]
    return df

df=coordinate(list_city)
# the process of getting latitude and longitude might crash sometimes, so we need to store the data after we get all the
# latitude and longitude
tfile = open('coordinate.txt', 'a')
tfile.write(df.to_string())
tfile.close()

# we can use the coordinate directly from the text file
data = pd.read_fwf('coordinate.txt')

'''creat Map object'''
m = folium.Map([35.8781, -100.6298], zoom_start=5)

# mark each city as a point
for index, row in data.iterrows():
    folium.CircleMarker(location=[float(row['latitude']), float(row['longitude'])],
                        radius=3,
                        popup=row['city'],
                        fill_color='#ffe6e6', # divvy color
                       ).add_to(m)


# plot heatmap
m.add_children(plugins.HeatMap([[float(row["latitude"]),float(row["longitude"])]for name, row in data.iterrows()]))

PORT = 7000
HOST = '127.0.0.1'
SERVER_ADDRESS = '{host}:{port}'.format(host=HOST, port=PORT)
FULL_SERVER_ADDRESS = 'http://' + SERVER_ADDRESS


def TemproraryHttpServer(page_content_type, raw_data):
    """
    A simpe, temprorary http web server on the pure Python 3.
    It has features for processing pages with a XML or HTML content.
    >>> page_content_type='html'
    >>> raw_data = ''' <!DOCTYPE html>\
        <html>\
        <head>\
        <title>Page Title</title>\
        </head>\
        <body>\
        <h1>This is a Heading</h1>\
        <p>This is a paragraph.</p>\
        </body>\
        </html>\
        '''

    >>> TemproraryHttpServer(page_content_type, raw_data)


    """

    class HTTPServerRequestHandler(BaseHTTPRequestHandler):
        """
        An handler of request for the server, hosting XML-pages.
        """

        def do_GET(self):
            """Handle GET requests"""

            # response from page
            self.send_response(200)

            # set up headers for pages
            content_type = 'text/{0}'.format(page_content_type)
            self.send_header('Content-type', content_type)
            self.end_headers()

            # writing data on a page
            self.wfile.write(bytes(raw_data, encoding='utf'))

            return

    if page_content_type not in ['html', 'xml']:
        raise ValueError('This server can serve only HTML or XML pages.')

    page_content_type = page_content_type

    # kill a process, hosted on a localhost:PORT
    subprocess.call(['fuser', '-k', '{0}/tcp'.format(PORT)])

    # Started creating a temprorary http server.
    httpd = HTTPServer((HOST, PORT), HTTPServerRequestHandler)

    # run a temprorary http server
    httpd.serve_forever()


def run_html_server(html_data=None):
    """
     run html server
    :param html_data: None value
    :return: open the html file in the browser
    >>> html_data=None
    >>> run_html_server(html_data)

    """

    if html_data is None:
        html_data = """
        <!DOCTYPE html>
        <html>
        <head>
        <title>Page Title</title>
        </head>
        <body>
        <h1>This is a Heading</h1>
        <p>This is a paragraph.</p>
        </body>
        </html>
        """

    # open in a browser URL and see a result
    webbrowser.open(FULL_SERVER_ADDRESS)

    # run server
    TemproraryHttpServer('html', html_data)

# ------------------------------------------------------------------------------------------------


# now let's save the visualization into the temp file and render it
from tempfile import NamedTemporaryFile
tmp = NamedTemporaryFile()
m.save(tmp.name)
with open(tmp.name) as f:
    folium_map_html = f.read()

run_html_server(folium_map_html)

# read file - temperature.txt
temp = pd.read_csv("D:/590-PR/final project/new_version/Final_Project-master/temperature.txt",header=None)
for i in range(len(temp[0])):
    if temp[0][i] == "['NaN']" or temp[0][i] == "[]":
        temp[0][i] = '***'
    else:
        temp[0][i] = float(temp[0][i].strip("['']"))
df_USA['temperature'] = temp
na_temperature_index = df_USA[df_USA.temperature == '***'].index.tolist()
df_USA = df_USA.drop(na_temperature_index)
df_USA['Fatal (Y/N)'] = df_USA['Fatal (Y/N)'].fillna('***')
na_fat_index = df_USA[df_USA['Fatal (Y/N)'] == '***'].index.tolist()
df_USA = df_USA.drop(na_fat_index)
df_USA.reset_index(drop=True, inplace=True)

d1 = pd.cut(df_USA.temperature, 5, labels = range(5))
    # discretization, each category is named as 0, 1, 2, 3, 4
    # [(11.82, 27.94] < (27.94, 43.98] < (43.98, 60.02] < (60.02, 76.06] < (76.06, 92.1]]
df_USA['Temp'] = d1
df_USA_temp_fatal = df_USA[['Temp','Fatal (Y/N)']]

## contigency table
ind = []
for i in range(len(df_USA_temp_fatal['Fatal (Y/N)'])):
    if df_USA_temp_fatal['Fatal (Y/N)'][i] == 'UNKNOWN':
        ind.append(i)
df_USA_temp_fatal = df_USA_temp_fatal.drop(ind)
df_USA_temp_fatal.reset_index(drop=True, inplace=True)
print("df_USA_temp_fatal(head()):")
print(df_USA_temp_fatal.head())
contingency_table = pd.crosstab(df_USA_temp_fatal['Temp'], df_USA_temp_fatal['Fatal (Y/N)'])
print("contigency table:")
print(contingency_table)
print("chi2-H1:")
print (chi2_contingency(contingency_table))

################################################  H2  #############################################
# H2: The activity people doing when they are attacked have a relationship with the injury type(fatal or not)
print('*************** H2: The activity people doing when they are attacked have a relationship with the injury type ****************')
df = pd.read_csv("D:/590-PR/final project/shark_attacks/attacks.csv",encoding = 'ISO-8859-1')
df = df[['Case Number', 'Date','Country', 'Area', 'Location','Activity','Sex ', 'Age', 'Injury', 'Fatal (Y/N)','Species ']]
df.rename(columns={'Case Number':'CaseNumber'}, inplace=True)
df_act_fatal = df
# delete None in Activity
df_act_fatal['Activity'] = df_act_fatal['Activity'].fillna('***')
na_Activity_index = df_act_fatal[df_act_fatal.Activity == '***'].index.tolist()
df_act_fatal = df_act_fatal.drop(na_Activity_index)
# delete None in fatal
df_act_fatal['Fatal (Y/N)'] = df_act_fatal['Fatal (Y/N)'].fillna('***')
na_fatal_index = df_act_fatal[df_act_fatal['Fatal (Y/N)'] == '***'].index.tolist()
df_act_fatal = df_act_fatal.drop(na_fatal_index)
def activity_lower_case(activity):
    '''
    >>> activity_lower_case("Surfing")
    'surfing'
    '''
    activity = str(activity)
    return activity.lower()
df_act_fatal['Activity'] = df_act_fatal['Activity'].apply(activity_lower_case)
def activity_process(activity):
    '''
    >>> activity_process("surfing")
    'surfing'
    '''
    activity = str(activity)
    if activity in df_act_fatal.Activity.value_counts()[list(df_act_fatal.Activity.value_counts()>50)].index:
        return activity
    else:
        return '***'
def fatal_process(fatal):
    '''
    >>> fatal_process("UNKNOWN")
    '***'
    '''
    fatal = str(fatal)
    if fatal in ['N','Y']:
        return fatal
    else:
        return '***'
df_act_fatal['Activity'] = df_act_fatal['Activity'].apply(activity_process)
df_act_fatal['Fatal (Y/N)'] = df_act_fatal['Fatal (Y/N)'].apply(fatal_process)
na_Activity_index = df_act_fatal[df_act_fatal.Activity == '***'].index.tolist()
df_act_fatal = df_act_fatal.drop(na_Activity_index)
na_fatal_index = df_act_fatal[df_act_fatal['Fatal (Y/N)'] == '***'].index.tolist()
df_act_fatal = df_act_fatal.drop(na_fatal_index)
df_act_fatal.reset_index(drop=True, inplace=True)
contingency_table1 = pd.crosstab(df_act_fatal['Activity'],df_act_fatal['Fatal (Y/N)'])
print("contigency table:")
print(contingency_table1)
print("chi2-H2:")
print (chi2_contingency(contingency_table1))

################################################  H3  #############################################
# H3: The species of shark have a relationship with the injury type (fatal or not)
print('*************** H3: The species of shark have a relationship with the injury type ****************')
df_species_fatal = df
df_species_fatal["Species "] = df_species_fatal["Species "].fillna('***')
na_species_index = df_species_fatal[df_species_fatal["Species "] == '***'].index.tolist()
df_species_fatal = df_species_fatal.drop(na_species_index)
df_species_fatal["Fatal (Y/N)"] = df_species_fatal["Fatal (Y/N)"].fillna('***')
na_fatal_index = df_species_fatal[df_species_fatal["Fatal (Y/N)"] == '***'].index.tolist()
df_species_fatal = df_species_fatal.drop(na_fatal_index)
def species_process(species):
    '''
    >>> species_process("White shark")
    'white shark'
    >>> species_process("Bull shark, 6' ")
    'bull shark'
    >>> species_process("3 m [10'] white shark ")
    'white shark'
    '''
    if species.lower() in ["white shark","tiger shark","bull shark","wobbegong shark","blacktip shark","blue shark","mako shark",
                           "raggedtooth shark","bronze whaler shark","nurse shark","grey nurse shark","zambesi shark",
                           "hammerhead shark","sandtiger shark","lemon shark","basking shark"]:
        return species.lower()
    elif "bull shark" in species.lower():
        return "bull shark"
    elif "white shark" in species.lower():
        return "white shark"
    elif "nurse shark" in species.lower():
        return "nurse shark"
    else:
        return "***"
def fatal_process(fatal):
    '''
    >>> fatal_process('UNKNOWN')
    '***'
    >>> fatal_process('N')
    'N'
    '''
    if fatal in ['N','Y']:
        return fatal
    else:
        return('***')
df_species_fatal["Species "] = df_species_fatal["Species "].apply(species_process)
df_species_fatal["Fatal (Y/N)"] = df_species_fatal["Fatal (Y/N)"].apply(fatal_process)
wrong_species_index = df_species_fatal[df_species_fatal["Species "] == '***'].index.tolist()
df_species_fatal = df_species_fatal.drop(wrong_species_index)
wrong_fatal_index = df_species_fatal[df_species_fatal["Fatal (Y/N)"] == '***'].index.tolist()
df_species_fatal = df_species_fatal.drop(wrong_fatal_index)
contingency_table2 = pd.crosstab(df_species_fatal['Species '], df_species_fatal['Fatal (Y/N)'])
print("contigency table:")
print(contingency_table2)
print("chi2_H3:")
print(chi2_contingency(contingency_table2))