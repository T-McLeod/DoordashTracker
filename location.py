from pyicloud import PyiCloudService
import os
from dotenv import load_dotenv
import requests

# TODO Error handling for basically everything

load_dotenv()
TOMKEY = os.getenv("TOMKEY")
appleID = os.getenv("appleID")
password = os.getenv("password")

api = PyiCloudService(appleID, password)
if api.requires_2fa:
    print("Two-factor authentication required.")
    code = input("Enter the code you received of one of your approved devices: ")
    result = api.validate_2fa_code(code)
    print("Code validation result: %s" % result)

    if not result:
        print("Failed to verify security code")
        # sys.exit(1)

    if not api.is_trusted_session:
        print("Session is not trusted. Requesting trust...")
        result = api.trust_session()
        print("Session trust result %s" % result)

        if not result:
            print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")

device = api.devices[1]
phone = api.iphone

# TODO Handle errors


def routeRequest(locations):
    response = requests.get(f"https://api.tomtom.com/routing/1/calculateRoute/{locationsToRoute(locations)}/json?key={TOMKEY}")
    route = response.json()['routes'][0]
    totalTime = route['summary']['travelTimeInSeconds']
    legs = route['legs']
    legTime = [leg['summary']['travelTimeInSeconds'] for leg in legs]
    return [totalTime, legTime]


def locationsToRoute(locations):
    ret = toLocationObject(locations[0])
    for location in locations[1:]:
        ret += ":" + toLocationObject(location)
    return ret

def toLocationObject(location):
    return str(location[0]) + "," + str(location[1])

def getDeviceLocation():
    location = device.location()
    return (location['latitude'], location['longitude'])

def searchPlace(currentLocation, query):
    response = requests.get(f"https://api.tomtom.com/search/2/poiSearch/{query}.json?key={TOMKEY}&geobias=point:{toLocationObject(currentLocation)}")
    match = response.json()['results'][0]
    pos = match['position']
    return (pos['lat'], pos['lon'])

# https://api.tomtom.com/search/2/geocode/{address}.json?key={Your_API_Key}
def addressToLocation(address, geoBias):
    lat, lon = geoBias
    response = requests.get(f"https://api.tomtom.com/search/2/geocode/{address}.json?key={TOMKEY}&lat={lat}&lon={lon}").json()
    result = response['results'][0]
    pos = result['position']
    return (pos['lat'], pos['lon'])


# https://api.tomtom.com/search/2/poiSearch/eiffel.json?key={Your_API_Key}
# locations = [(52.50931,13.42936), (52.50274,13.43872), (52.50931,13.42936)]
# print(addressToLocation("125 Streamside Pl", getDeviceLocation()))
# response = routeRequest(locations)