// Basic demo for accelerometer readings from Adafruit MPU6050

// ESP32 Guide: https://RandomNerdTutorials.com/esp32-mpu-6050-accelerometer-gyroscope-arduino/
// ESP8266 Guide: https://RandomNerdTutorials.com/esp8266-nodemcu-mpu-6050-accelerometer-gyroscope-arduino/
// Arduino Guide: https://RandomNerdTutorials.com/arduino-mpu-6050-accelerometer-gyroscope/

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266HTTPClient.h>

#define WIFI_SSID "WIFI_SSID"            // WIFI SSID here                                   
#define WIFI_PASSWORD "WIFI Password"        // WIFI password here

Adafruit_MPU6050 mpu;
sensors_event_t la, lg, ltemp;

String sendval, sendval2, postData;

WiFiClient wifiClient;


void setup(void) {
  Serial.begin(115200);
  while (!Serial)
    delay(10); // will pause Zero, Leonardo, etc until serial console opens

  Serial.println("Adafruit MPU6050 test!");

  // Try to initialize!
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
/*    while (1) {
      delay(10);
    }*/
    while(!mpu.begin()) ESP.restart();

  }
  Serial.println("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  Serial.print("Accelerometer range set to: ");
  switch (mpu.getAccelerometerRange()) {
  case MPU6050_RANGE_2_G:
    Serial.println("+-2G");
    break;
  case MPU6050_RANGE_4_G:
    Serial.println("+-4G");
    break;
  case MPU6050_RANGE_8_G:
    Serial.println("+-8G");
    break;
  case MPU6050_RANGE_16_G:
    Serial.println("+-16G");
    break;
  }
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  Serial.print("Gyro range set to: ");
  switch (mpu.getGyroRange()) {
  case MPU6050_RANGE_250_DEG:
    Serial.println("+- 250 deg/s");
    break;
  case MPU6050_RANGE_500_DEG:
    Serial.println("+- 500 deg/s");
    break;
  case MPU6050_RANGE_1000_DEG:
    Serial.println("+- 1000 deg/s");
    break;
  case MPU6050_RANGE_2000_DEG:
    Serial.println("+- 2000 deg/s");
    break;
  }

  mpu.setFilterBandwidth(MPU6050_BAND_5_HZ);
  Serial.print("Filter bandwidth set to: ");
  switch (mpu.getFilterBandwidth()) {
  case MPU6050_BAND_260_HZ:
    Serial.println("260 Hz");
    break;
  case MPU6050_BAND_184_HZ:
    Serial.println("184 Hz");
    break;
  case MPU6050_BAND_94_HZ:
    Serial.println("94 Hz");
    break;
  case MPU6050_BAND_44_HZ:
    Serial.println("44 Hz");
    break;
  case MPU6050_BAND_21_HZ:
    Serial.println("21 Hz");
    break;
  case MPU6050_BAND_10_HZ:
    Serial.println("10 Hz");
    break;
  case MPU6050_BAND_5_HZ:
    Serial.println("5 Hz");
    break;
  }

  Serial.println("");
  mpu.getEvent(&la, &lg, &ltemp);
  delay(100);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);


  Serial.println("Communication Started \n\n");  
  delay(1000);
  
  pinMode(LED_BUILTIN, OUTPUT);     // initialize built in led on the board 
  
  WiFi.mode(WIFI_STA);           
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);        //try to connect with wifi
  Serial.print("Connecting to ");
  Serial.print(WIFI_SSID);
  while (WiFi.status() != WL_CONNECTED) 
  { Serial.print(".");
    delay(500); }
  Serial.println();
  Serial.print("Connected to ");
  Serial.println(WIFI_SSID);
  Serial.print("IP Address is : ");
  Serial.println(WiFi.localIP());    //print local IP address
  delay(30);
}



void loop() {
  /* Get new sensor events with the readings */
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  if(a.acceleration.x == 0 && a.acceleration.y==0 && a.acceleration.z==0){
    Serial.println("Lost connection");
    while(!mpu.begin()) ESP.restart();
    mpu.getEvent(&la, &lg, &ltemp);
    return;
  }

  HTTPClient http;    // http object of clas HTTPClient
  
  if(la.acceleration.x - a.acceleration.x > 0.9 || la.acceleration.y-a.acceleration.y > 0.9){
    digitalWrite(LED_BUILTIN, LOW);
    Serial.print("Acceleration X: ");
    Serial.print(a.acceleration.x);
    Serial.print(", Y: ");
    Serial.print(a.acceleration.y);
    Serial.print(", Z: ");
    Serial.print(a.acceleration.z);
    Serial.println(" m/s^2");
    Serial.print("Temperature: ");
    Serial.print(temp.temperature);
    Serial.println(" degC");
    Serial.println();

    sendval = String(temp.temperature);
    sendval2 = String(abs(la.acceleration.x - a.acceleration.x)+abs(la.acceleration.y-a.acceleration.y));

    postData = "sendval=" + sendval + "&sendval2=" + sendval2;

    http.begin(wifiClient, "http://IP_OF_LOCALHOST_DEVICE/IOT/dbwrite.php");              // Connect to host where MySQL databse is hosted
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");            //Specify content-type header
    
    Serial.println("Http begin done");

    Serial.println("Calling php");
    int httpCode = http.POST(postData);   // Send POST request to php file and store server response code in variable named httpCode
    Serial.println("Values are, sendval = " + sendval + " and sendval2 = "+sendval2 );
    
    // if connection eatablished then do this
    if (httpCode == 200)
    {
      Serial.println("Values uploaded successfully."); Serial.println(httpCode); 
      String webpage = http.getString();    // Get html webpage output and store it in a string
      Serial.println(webpage + "\n");
    }

    // if failed to connect then return and restart
    else
    { 
      Serial.println(httpCode); 
      Serial.println("Failed to upload values. \n"); 
      http.end(); 
      return;
    }

    delay(500);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
  }
  digitalWrite(LED_BUILTIN, HIGH);

//  delay(500);
  la = a;
  lg = g;
  ltemp = temp;
}
