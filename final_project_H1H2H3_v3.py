import pandas as pd
import numpy as np
from datetime import datetime
from scipy.stats import chi2_contingency

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
