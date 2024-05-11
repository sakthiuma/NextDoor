from geopy.geocoders import Nominatim

if __name__ == '__main__':
    # importing geopy library and Nominatim class

    # calling the Nominatim tool and create Nominatim class
    loc = Nominatim(user_agent="Geopy Library")

    # entering the location name
    getLoc = loc.geocode("162 85th street Brooklyn NY 11209")

    # printing address
    print(getLoc.address)

    # printing latitude and longitude
    print("Latitude = ", getLoc.latitude, "\n")
    print("Longitude = ", getLoc.longitude)