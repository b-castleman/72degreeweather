import urllib.request
import numpy as np
import cv2
import matplotlib.pyplot as plt
from contextlib import nullcontext
import requests
from tkinter import *
import json
import random
import tweepy

########################### Step 1: Get the current weather map ###########################
def getWeatherMap():
    image_url = 'https://graphical.weather.gov/images/conus/T2_conus.png' #the image on the web
    save_name = 'temperatureMap.jpg' #local name to be saved
    urllib.request.urlretrieve(image_url, save_name)
    return save_name
###################################### End of Step 1 (current weather map) ##################################

################### Step 2: Partition the map, find chances of getting 72 degrees ###########################
def applyPartitionMasks(imFn):
    #### Locations Between 68-70 Degrees ####
    # Load Temperature Map
    tempMap = cv2.imread(imFn)

    # Create Potential 72 Value Mask
    pot72 = np.ndarray(tempMap[:,:,0].shape)
    for (x,y), value in np.ndenumerate(pot72):
        Rmask = tempMap[x,y,0] >= 0 and tempMap[x,y,0] <= 1     # red mask
        Gmask = tempMap[x,y,1] >= 245 and tempMap[x,y,1] <= 255 # green mask
        Bmask = tempMap[x,y,2] >= 250 and tempMap[x,y,2] <= 255 # blue mask
        pot72[x,y] = Rmask and Gmask and Bmask

    # Iterate through the partitions
    rootPath = r"" # got rid of ./ and root parts
    partitions = ["arizona_newmexico","california","carolinas","colorado","conn_rhode_isl","dakotas","florida",\
                "georgia_mississippi_alabama","idaho_montana_wyoming","indiana_ohio","iowa_illinois",\
                "kentucky_tennessee","louisiana_arkansas_missouri","maine","maryland_delaware","mass",\
                "michigan","minnisota_wisconsin","nebraska_kansas_oklahoma","newjersey","newyork","penn",\
                "texas","utah_nevada","vermont_new_hamp","virginia_westvirginia","washington_oregon"]

    # Instantiate percentChances vector
    percentChances = np.empty(len(partitions),dtype=float)

    # Populate the vector percentChances for finding 72 degrees
    i = 0
    for partitionStr in partitions:

        # Open Partition
        fullpath = rootPath + partitionStr + ".jpg"

        partitionImg = cv2.imread(fullpath)

        # See what percent there is
        pot72Count = 0   # potential 72 deg pixels
        totalPixels = 0  # total pixels in partition

        Rlayer = partitionImg[:,:,0]
        Glayer = partitionImg[:,:,1]
        Blayer = partitionImg[:,:,2]

        #plt.imshow(partitionImg)
        for (x,y), value in np.ndenumerate(pot72):
            if Rlayer[x,y] < 5 or Glayer[x,y] < 5 or Blayer[x,y] < 5:
                totalPixels += 1

                if pot72[x,y]:
                    pot72Count += 1

        # Record potential of finding 72 degrees
        chance = 100.0 * pot72Count / totalPixels
        print("Percent 72 deg for partition " + partitionStr + ": " + str(chance) + "%.")
        percentChances[i] = chance

        # Iteration Update
        i += 1
    # end of loop

    return percentChances, partitions
################### End of Step 2 (Partitioning & Percent Chance Finding) ###########################


################ Step 3: Find a valid city in the partitions where 72 degrees exists ###########################
def findValidCities(chances,partitions):
    ####################################### Functions Begin #######################################

    def getPStates(partition):
        if partition == "arizona_newmexico":
            return ["Arizona","New Mexico"]
        elif partition == "california":
            return ["California"]
        elif partition == "carolinas":
            return ["North Carolina","South Carolina"]
        elif partition ==  "colorado":
            return ["Colorado"]
        elif partition == "conn_rhode_isl":
            return ["Connecticut","Rhode Island"]
        elif partition == "dakotas":
            return ["North Dakota","South Dakota"]
        elif partition == "florida":
            return ["Florida"]
        elif partition == "georgia_mississippi_alabama":
            return ["Georgia","Mississippi","Alabama"]
        elif partition == "idaho_montana_wyoming":
            return ["Idaho","Montana","Wyoming"]
        elif partition == "indiana_ohio":
            return ["Indiana","Ohio"]
        elif partition == "iowa_illinois":
            return ["Iowa","Illinois"]
        elif partition == "kentucky_tennessee":
            return ["Kentucky","Tennessee"]
        elif partition == "louisiana_arkansas_missouri":
            return ["Louisiana","Arkansas","Missouri"]
        elif partition == "maine":
            return ["Maine"]
        elif partition == "maryland_delaware":
            return ["Maryland","Delaware"]
        elif partition == "mass":
            return ["Massachusetts"]
        elif partition == "michigan":
            return ["Michigan"]
        elif partition == "minnisota_wisconsin":
            return ["Minnisota","Wisconsin"]
        elif partition == "nebraska_kansas_oklahoma":
            return ["Nebraska","Kansas","Oklahoma"]
        elif partition == "newjersey":
            return ["New Jersey"]
        elif partition == "newyork":
            return ["New York"]
        elif partition == "penn":
            return ["Pennsylvania"]
        elif partition == "texas":
            return ["Texas"]
        elif partition == "utah_nevada":
            return ["Utah","Nevada"]
        elif partition == "vermont_new_hamp":
            return ["Vermont","New Hampshire"]
        elif partition == "virginia_westvirginia":
            return ["Virginia","West Virginia"]
        elif partition == "washington_oregon":
            return ["Washington","Oregon"]
        else:
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

            if temp >= 71.99 and temp <= 73:
                validCities = [*validCities,city]
        
        return validCities
    # End of getValidCitiesFromState() function

    def getCitiesFromState(state):
        # json file path
        rootpath = r"./top1000citiesInUSA/"
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
        API_KEY = '' # for openWeather          # <- FILL IN
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"

        response = requests.get(url).json()
        return response.get("main").get("temp")
    # End of getTemperature() function

    ### Step 3 Helper Functions End ###
    ### Step 3 Scripting Begins ###

    # Sort the chances in descending order
    idx = np.argsort(chances) # idx to sort array

    chances = chances[idx]        # sort in ascending order
    partitions[:] = [partitions[i] for i in idx]

    chances = chances[::-1]       # sort in descending order
    partitions = partitions[::-1]

    validCities = [] # Cities that meet this criteria
    corrStates = [] # The corresponding states for the following cities
    for i in range(len(partitions)):
        # Obtain partition
        partition = partitions[i]

        states = getPStates(partition)

        for state in states:
            print("Current State being investigated: " + state)
            currValidCities = getValidCitiesFromState(state) # current valid cities for this specific state
            print("Number of valid cities found: " + str(len(currValidCities)) + ".")
            validCities = [*validCities,*currValidCities]
            corrStates = [*corrStates,*([state] * len(currValidCities))]
        # end of state loop
        
        # Break statement: if past 4 iterations, break partition loop whenever we have valid elements
        if i >= 4 and len(validCities) > 0:
            break
    # end of partition loop

    if len(validCities) == 0:
        return None, None # No cities have a 72 degree [F] temperature
    else:
        idx = random.randint(0, len(validCities)-1) # pick a random city
        return validCities[idx], corrStates[idx] # return the city, state combo
################### End of Step 3 (finding a random city/state combo) ###########################


################### Step 4 (Post a tweet of the city/state combo) ###########################
def postTweet(city,state):
    # Keys
    CONSUMER_KEY= ''        # <- FILL IN
    CONSUMER_SECRET = ''    # <- FILL IN
    ACCESS_KEY = ''         # <- FILL IN
    ACCESS_SECRET = ''      # <- FILL IN
    print("Authorization Keys Loaded.")

    # Authorization
    auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY,ACCESS_SECRET)
    api = tweepy.API(auth)
    print("Authorization Successful.")

    # Write Post
    if city == None and state == None:
        api.update_state("It is not currently 72 degrees in any state within the U.S.")
    else:
        api.update_status("It is currently 72 degrees Fahrenheit in " + city + ", " + state + ".")
    print("Post Successful.")

    return None
################### End of step 4 (Posting tweet) ###########################


################### Main function ###########################
if __name__ == "__main__":
    # Step 1: Get weather map image downloaded
    weatherMapName = getWeatherMap()

    # Step 2: Partition the map and obtain the percent chances at finding 72 degrees in each
    chances, partitions = applyPartitionMasks(weatherMapName)

    # Step 3: Get a valid city withn the U.S. that the temperature is 72 degrees
    city, state = findValidCities(chances,partitions)

    # Step 4: Post a tweet of the results
    postTweet(city,state)
################ End of Main function #######################

