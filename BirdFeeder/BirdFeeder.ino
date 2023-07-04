#include <ESP8266WiFi.h>        // Source: https://arduino-esp8266.readthedocs.io/en/latest/esp8266wifi/readme.html
#include <WiFiClientSecure.h>   // Source: https://github.com/esp8266/Arduino/blob/master/libraries/ESP8266WiFi/src/WiFiClientSecure.h (comes from <ESP8266WiFi.h>)
#include <PubSubClient.h>       // Source: https://pubsubclient.knolleary.net/
#include <ArduinoJson.h>        // Source: https://github.com/bblanchon/ArduinoJson
#include "HX711.h"              // Source: https://github.com/bogde/HX711
#include "secrets.h"

#define calibration_factor 244
#define DAT  14
#define CLK  12

float weight;

HX711 scale;

#define AWS_IOT_PUBLISH_TOPIC   "$aws/rules/LoadCellData"

// Configuration of NTP
// See https://werner.rothschopf.net/202011_arduino_esp8266_ntp_en.htm
#define MY_NTP_SERVER     "pool.ntp.org"             // Source: https://www.pool.ntp.org/zone/us
#define MY_TZ             "CST6CDT,M3.2.0,M11.1.0"   // Source: https://github.com/nayarsystems/posix_tz_db/blob/master/zones.csv
 
WiFiClientSecure wifi_client;
 
BearSSL::X509List cert(cacert);
BearSSL::X509List client_crt(client_cert);
BearSSL::PrivateKey key(privkey);
 
PubSubClient mqtt_client(wifi_client);

void connectAWS()
{
  WiFi.mode(WIFI_STA); 
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.println("Connecting to Wi-Fi");

  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  Serial.print("Setting time using SNTP");     // needed for certificate validation
  configTime(MY_TZ, MY_NTP_SERVER);
  Serial.println();

  Serial.print("Connecting to AWS IOT");

  wifi_client.setTrustAnchors(&cert);
  wifi_client.setClientRSACert(&client_crt, &key);
  mqtt_client.setServer(MQTT_HOST, 8883);

  while (!mqtt_client.connect(THINGNAME)) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if(!mqtt_client.connected()){
    Serial.println("AWS IoT Timeout!");
    return;
  }

  Serial.println("AWS IoT Connected!");
}

void publishMessage()
{
  //Create a JSON document of size 200 bytes, and populate it
  //See https://arduinojson.org/
  StaticJsonDocument<200> doc;
  doc["time"] = millis();
  doc["weight"] = weight;
  char jsonBuffer[512];
  serializeJson(doc, jsonBuffer);
 
  mqtt_client.publish(AWS_IOT_PUBLISH_TOPIC, jsonBuffer);
}

void setup() {

  delay(3000);
  Serial.begin(115200);
  connectAWS();

  scale.begin(DAT, CLK);
  scale.set_scale(calibration_factor);
  scale.tare();
  Serial.println("Readings:");
}

void loop() {

  weight = round(scale.get_units());    // scale.get_units() returns a float
  Serial.print(weight);
  Serial.print(" g");
  Serial.println();

  publishMessage();

  if (!mqtt_client.connected())
  {
    connectAWS();
  }
  else
  {
    mqtt_client.loop();
  }
  delay(1000);
}