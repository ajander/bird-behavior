#include <ESP8266WiFi.h>        // Source: https://arduino-esp8266.readthedocs.io/en/latest/esp8266wifi/readme.html
#include <WiFiClientSecure.h>   // Source: https://github.com/esp8266/Arduino/blob/master/libraries/ESP8266WiFi/src/WiFiClientSecure.h (comes from <ESP8266WiFi.h>)
#include <PubSubClient.h>       // Source: https://pubsubclient.knolleary.net/
#include <ArduinoJson.h>        // Source: https://github.com/bblanchon/ArduinoJson
//#include "WiFi.h"
#include "secrets.h"

// defines pins numbers
const int trigPin = 14;
const int echoPin = 12;

// defines variables
long duration;
int distance;
unsigned long lastMillis = 0;
//uint32_t t1;

#define AWS_IOT_PUBLISH_TOPIC   "feather/pub"

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
  // Begin WiFi in station mode
  WiFi.mode(WIFI_STA); 
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.println("Connecting to Wi-Fi");

  // Wait for WiFi connection
  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  // Set time to allow for certificate validation
  Serial.print("Setting time using SNTP");
  configTime(MY_TZ, MY_NTP_SERVER);
  Serial.println();

  Serial.print("Connecting to AWS IOT");

  wifi_client.setTrustAnchors(&cert);
  wifi_client.setClientRSACert(&client_crt, &key);
  mqtt_client.setServer(MQTT_HOST, 8883);

  // Wait for connection to AWS IoT
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
  doc["distance"] = distance;
  char jsonBuffer[512];
  serializeJson(doc, jsonBuffer); // print to client
 
  mqtt_client.publish(AWS_IOT_PUBLISH_TOPIC, jsonBuffer);
}

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  Serial.begin(115200);
  connectAWS();
}

void loop() {

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);        // trigger on trigPin
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);  // read echoPin
  distance = duration * 0.034 / 2;

  Serial.print("Distance: ");
  Serial.println(distance);
  //delay(1000);

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



// const int testPin = 0;
// const int delayTime = 1000;

// void setup() {
//   Serial.begin(115200);
//   Serial.println("Starting setup");
//   Serial.println();
//   pinMode(testPin, OUTPUT);
//   Serial.println("Set pin 0 mode to output");
//   Serial.println();
// }

// void loop() {
//   Serial.println("Set pin high");
//   Serial.println();
//   digitalWrite(testPin, HIGH);
//   delay(delayTime);
//   Serial.println("Set pin low");
//   Serial.println();
//   digitalWrite(testPin, LOW);
//   delay(delayTime);
// }

