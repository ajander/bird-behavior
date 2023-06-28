#include <ESP8266WiFi.h> 
#include <WiFiClientSecure.h> // Source: https://github.com/esp8266/Arduino/blob/master/libraries/ESP8266WiFi/src/WiFiClientSecure.h (comes from <ESP8266.WiFi.h>)
#include <MQTTClient.h> //MQTT Library Source: https://github.com/256dpi/arduino-mqtt
#include <ArduinoJson.h> //ArduinoJson Library Source: https://github.com/bblanchon/ArduinoJson
//#include "WiFi.h"
#include "secrets.h"


// MQTT topics for the device
#define AWS_IOT_PUBLISH_TOPIC   "feather/pub"

WiFiClientSecure wifi_client = WiFiClientSecure();
MQTTClient mqtt_client = MQTTClient(256); //256 indicates the maximum size for packets being published and received.

uint32_t t1;

void connectAWS()
{
  //Begin WiFi in station mode
  WiFi.mode(WIFI_STA); 
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.println("Connecting to Wi-Fi");

  //Wait for WiFi connection
  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  // Configure wifi_client with the correct certificates and keys
  // wifi_client.setCACert(cacert);
  // wifi_client.setCertificate(client_cert);
  // wifi_client.setPrivateKey(privkey);
  X509List clientCertificate(client_cert);
  PrivateKey clientPrivateKey(privkey);
  X509List caCertificate(cacert);

  //Connect to AWS IOT Broker. 8883 is the port used for MQTT
  mqtt_client.begin(MQTT_HOST, 8883, wifi_client);

  Serial.print("Connecting to AWS IOT");

  //Wait for connection to AWS IoT
  while (!mqtt_client.connect(THINGNAME)) {
    Serial.print(".");
    delay(100);
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
  doc["elapsed_time"] = millis() - t1;
  doc["value"] = random(1000);
  char jsonBuffer[512];
  serializeJson(doc, jsonBuffer); // print to mqtt_client

  //Publish to the topic
  mqtt_client.publish(AWS_IOT_PUBLISH_TOPIC, jsonBuffer);
  Serial.println("Sent a message");
}

void setup() {
  Serial.begin(115200);
  t1 = millis();
  connectAWS();
}

void loop() {
  publishMessage();
  mqtt_client.loop();
  delay(4000);
}