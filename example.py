// #include <ESP8266WiFi.h>        // Source: https://arduino-esp8266.readthedocs.io/en/latest/esp8266wifi/readme.html
// #include <WiFiClientSecure.h>   // Source: https://github.com/esp8266/Arduino/blob/master/libraries/ESP8266WiFi/src/WiFiClientSecure.h (comes from <ESP8266WiFi.h>)
// #include <PubSubClient.h>       // Source: https://pubsubclient.knolleary.net/
// #include <ArduinoJson.h>        // Source: https://github.com/bblanchon/ArduinoJson
// //#include "WiFi.h"
// #include "secrets.h"

// // defines pins numbers
// const int trigPin = 14;
// const int echoPin = 12;

// // defines variables
// long duration;
// int distance;
// unsigned long lastMillis = 0;
// //uint32_t t1;

// #define AWS_IOT_PUBLISH_TOPIC   "feather/pub"

// // Configuration of NTP
// // See https://werner.rothschopf.net/202011_arduino_esp8266_ntp_en.htm
// #define MY_NTP_SERVER     "pool.ntp.org"             // Source: https://www.pool.ntp.org/zone/us
// #define MY_TZ             "CST6CDT,M3.2.0,M11.1.0"   // Source: https://github.com/nayarsystems/posix_tz_db/blob/master/zones.csv
 
// WiFiClientSecure wifi_client;
 
// BearSSL::X509List cert(cacert);
// BearSSL::X509List client_crt(client_cert);
// BearSSL::PrivateKey key(privkey);
 
// PubSubClient mqtt_client(wifi_client);

// void connectAWS()
// {
//   // Begin WiFi in station mode
//   WiFi.mode(WIFI_STA); 
//   WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

//   Serial.println("Connecting to Wi-Fi");

//   // Wait for WiFi connection
//   while (WiFi.status() != WL_CONNECTED){
//     delay(500);
//     Serial.print(".");
//   }
//   Serial.println();

//   // Set time to allow for certificate validation
//   Serial.print("Setting time using SNTP");
//   configTime(MY_TZ, MY_NTP_SERVER);
//   Serial.println();

//   Serial.print("Connecting to AWS IOT");

//   wifi_client.setTrustAnchors(&cert);
//   wifi_client.setClientRSACert(&client_crt, &key);
//   mqtt_client.setServer(MQTT_HOST, 8883);

//   // Wait for connection to AWS IoT
//   while (!mqtt_client.connect(THINGNAME)) {
//     delay(500);
//     Serial.print(".");
//   }
//   Serial.println();

//   if(!mqtt_client.connected()){
//     Serial.println("AWS IoT Timeout!");
//     return;
//   }

//   Serial.println("AWS IoT Connected!");
// }

// void publishMessage()
// {
//   //Create a JSON document of size 200 bytes, and populate it
//   //See https://arduinojson.org/
//   StaticJsonDocument<200> doc;
//   doc["time"] = millis();
//   doc["distance"] = distance;
//   char jsonBuffer[512];
//   serializeJson(doc, jsonBuffer); // print to client
 
//   mqtt_client.publish(AWS_IOT_PUBLISH_TOPIC, jsonBuffer);
// }

// void setup() {
//   pinMode(trigPin, OUTPUT);
//   pinMode(echoPin, INPUT);
//   Serial.begin(115200);
//   connectAWS();
// }

// void loop() {

//   digitalWrite(trigPin, LOW);
//   delayMicroseconds(2);
//   digitalWrite(trigPin, HIGH);        // trigger on trigPin
//   delayMicroseconds(10);
//   digitalWrite(trigPin, LOW);

//   duration = pulseIn(echoPin, HIGH);  // read echoPin
//   distance = duration * 0.034 / 2;

//   Serial.print("Distance: ");
//   Serial.println(distance);
//   //delay(1000);

//   publishMessage();

//   if (!mqtt_client.connected())
//   {
//     connectAWS();
//   }
//   else
//   {
//     mqtt_client.loop();
//   }
//   delay(1000);
// }

**********************************

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