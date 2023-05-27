import os
import iot_api_client as iot
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


CLIENT_ID = os.getenv("CLIENT_ID")  # get a valid one from your Arduino Create account
CLIENT_SECRET = os.getenv("CLIENT_SECRET")  # get a valid one from your Arduino Create account

THING_ID = 'e12224f1-8238-4060-bcbf-7c3d5f672576'  # phone
PROPERTY_ID = 'bbf57d34-a09b-4bb9-9beb-dd148795f6b8'  # X accelerometer


if __name__ == "__main__":
    # Setup the OAuth2 session that'll be used to request the server an access token
    oauth_client = BackendApplicationClient(client_id=CLIENT_ID)
    token_url = "https://api2.arduino.cc/iot/v1/clients/token"
    oauth = OAuth2Session(client=oauth_client)

    # This will fire an actual HTTP call to the server to exchange client_id and
    # client_secret with a fresh access token
    token = oauth.fetch_token(
        token_url=token_url,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        include_client_id=True,
        audience="https://api2.arduino.cc/iot",
    )

    # If we get here we got the token, print its expiration time
    print("Got a token, expires in {} seconds".format(token.get("expires_in")))

    # Now we setup the iot-api Python client, first of all create a
    # configuration object. The access token goes in the config object.
    client_config = iot.Configuration(host="https://api2.arduino.cc/iot")
    # client_config.debug = True
    client_config.access_token = token.get("access_token")

    # Create the iot-api Python client with the given configuration
    client = iot.ApiClient(client_config)

    #%% List devices and their properties

    # # Each API model has its own wrapper, here we want to interact with
    # # devices, so we create a DevicesV2Api object
    # devices = iot.DevicesV2Api(client)

    # # Get a list of devices, catching the specific exception
    # try:
    #     resp = devices.devices_v2_list()
    #     print("Response from server:")
    #     print(resp)
    # except iot.ApiException as e:
    #     print("An exception occurred: {}".format(e))


    #%% Read values from a property of a device

    properties = iot.PropertiesV2Api(client)

    try:
        # show properties_v2
        resp = properties.properties_v2_show(THING_ID, PROPERTY_ID)
        # This prints out the whole response
        print(resp)
        # This shows how to extract the last_value
        print("\nVariable {} = {}".format(resp.variable_name, resp.last_value))
    
    except Exception as e:
        print("Exception when calling PropertiesV2Api->propertiesV2Show: %s\n" % e)