from contextlib import nullcontext
import numpy as np
import requests
from tkinter import *
import math
import json

####################################### Functions Begin #######################################

def getPStates(partition):
    match partition:
        case "arizona_newmexico":
            return ["Arizona","New Mexico"]
        case "california":
            return ["California"]
        case "carolinas":
            return ["North Carolina","South Carolina"]
        case "colorado":
            return ["Colorado"]
        case "conn_rhode_isl":
            return ["Connecticut","Rhode Island"]
        case "dakotas":
            return ["North Dakota","South Dakota"]
        case "florida":
            return ["Florida"]
        case "georgia_mississippi_alabama":
            return ["Georgia","Mississippi","Alabama"]
        case "idaho_montana_wyoming":
            return ["Idaho","Montana","Wyoming"]
        case "indiana_ohio":
            return ["Indiana","Ohio"]
        case "iowa_illinois":
            return ["Iowa","Illinois"]
        case "kentucky_tennessee":
            return ["Kentucky","Tennessee"]
        case "louisiana_arkansas_missouri":
            return ["Louisiana","Arkansas","Missouri"]
        case "maine":
            return ["Maine"]
        case "maryland_delaware":
            return ["Maryland","Delaware"]
        case "mass":
            return ["Massachusetts"]
        case "michigan":
            return ["Michigan"]
        case "minnisota_wisconsin":
            return ["Minnisota","Wisconsin"]
        case "nebraska_kansas_oklahoma":
            return ["Nebraska","Kansas","Oklahoma"]
        case "newjersey":
            return ["New Jersey"]
        case "newyork":
            return ["New York"]
        case "penn":
            return ["Pennsylvania"]
        case "texas":
            return ["Texas"]
        case "utah_nevada":
            return ["Utah","Nevada"]
        case "vermont_new_hamp":
            return ["Vermont","New Hampshire"]
        case "virginia_westvirginia":
            return ["Virginia","West Virginia"]
        case "washington_oregon":
            return ["Washington","Oregon"]
        case _:
            print("The given partition does not match any programmed states.")
            return None
# End of getPStates() function

def getValidCitiesFromState(state):
    cities, lats, lons = getCitiesFromState(state)

    validCities = []
    
    for i in range(len(cities)):
        city = cities[i]
        lat = lats[i]
        lon = lons[i]
        temp = getTemperature(lat,lon)      # city temp [K]
        temp = (temp - 273.15) * 9.0/5 + 32 # city temp [F]

        if temp >= 68.99 and temp <= 70:
            validCities = [*validCities,city]
    
    return validCities
# End of getValidCitiesFromState() function

def getCitiesFromState(state):
    # json file path
    rootpath = "C:\\Users\\Blake\\Documents\\TwitterBot\\top1000citiesInUSA\\"
    filename = "cities.json"

    fullFilePath = rootpath + filename

    # open json file
    with open(fullFilePath, 'r') as json_file:
        json_load = json.load(json_file)

    # obtain cities, lats, and lons
    cities = []
    lats = []
    lons = []
    for element in json_load:
        if element.get("state") == state:
            cities = [*cities, element.get("city")]
            lats = [*lats,element.get("latitude")]
            lons = [*lons,element.get("longitude")]
    
    return cities,lats,lons
# End of getCitiesFromState() function



def getTemperature(lat,lon):
    API_KEY = 'ee24082422a3df350c99cd67cd14619e' # for openWeather
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"

    response = requests.get(url).json()
    return response.get("main").get("temp")
# End of getTemperature() function

####################################### Functions End #######################################

####################################### Script Begins #######################################
# "Possible" Chances array
chances = np.array([ 9.25185608,  2.46797287,  0.        ,  4.92550927,  0.        ,\
        0.        ,  5.07030251,  0.        ,  0.        ,  0.        ,\
        0.        ,  0.        ,  0.10958904,  0.        ,  0.        ,\
        0.        ,  0.        ,  0.        ,  0.31055901,  0.        ,\
        0.        ,  0.        , 13.69548585,  3.3049226 ,  0.        ,\
        0.        ,  0.        ])

# Iterate through the partitions
rootPath = 'C:\\Users\\Blake\\Documents\\TwitterBot\\'
partitions = ["arizona_newmexico","california","carolinas","colorado","conn_rhode_isl","dakotas","florida",\
              "georgia_mississippi_alabama","idaho_montana_wyoming","indiana_ohio","iowa_illinois",\
              "kentucky_tennessee","louisiana_arkansas_missouri","maine","maryland_delaware","mass",\
              "michigan","minnisota_wisconsin","nebraska_kansas_oklahoma","newjersey","newyork","penn",\
              "texas","utah_nevada","vermont_new_hamp","virginia_westvirginia","washington_oregon"]


# Sort the chances in descending order
idx = np.argsort(chances) # idx to sort array

chances = chances[idx]        # sort in ascending order
partitions[:] = [partitions[i] for i in idx]

chances = chances[::-1]       # sort in descending order
partitions = partitions[::-1]

for partition in partitions[0:20]:
    states = getPStates(partition)

    for state in states:
        print("Current State being investigated: " + state)
        validCities = getValidCitiesFromState(state)

        print("Valid cities in " + state + ":")
        print(validCities)


