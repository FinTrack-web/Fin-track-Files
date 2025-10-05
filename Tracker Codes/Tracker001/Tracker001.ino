#include <WiFi.h>          
#include <HTTPClient.h>    
#include <WiFiClient.h>        // Library for client connections
#include <TinyGPSPlus.h>
#include <Adafruit_MPU6050.h> // For sensor data structures (sensors_event_t)
#include <Adafruit_Sensor.h>   // Required for the sensor event types
#include <math.h> // For sqrt() and atan2()

// --- 1. WIFI AND GOOGLE SCRIPT CONFIGURATION ---
// IMPORTANT: Replace these placeholders with your actual values.
const char* ssid = "AI2";
const char* password = "October2025";

// REPLACE THIS with the URL you get after deploying your Google Apps Script (Code.gs)
const char* GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzvB_49RGeMLaJoOwPMbJPkluPumGtZQb0owdIClTVYDye54pmdU95NvXiKUjEiY1SX2g/exec"; 

// --- SHARK DEFINITIONS (42 Custom Sharks) ---

// Define the structure for a single shark profile, including its specific primary diet
struct SharkProfile {
    const char* id;
    const char* name;
    // Ecological Types: 
    // APEX (Apex Predator), CSTL (Coastal Benthic), PLGC (Pelagic/Open Ocean), 
    // FLTR (Filter Feeder), DEEP (Deepwater/Benthic Slope)
    const char* type; 
    const char* primaryDiet; // Specific prey for this species
};

// Define the 42 Shark Profiles with their specific primary diets
const SharkProfile SHARK_PROFILES[] = {
    {"S01", "African Dwarf Sawshark", "DEEP", "Benthic Invertebrates & Deep-Sea Fish"},
    {"S02", "Australian Angel Shark", "CSTL", "Flatfish & Benthic Crustaceans"},
    {"S03", "Bahamas Sawshark", "DEEP", "Worms, Crustaceans, and Small Fish"},
    {"S04", "Basking Shark", "FLTR", "Plankton & Krill"},
    {"S05", "Bigeyed Sixgill Shark (Ancient Watche)", "DEEP", "Deep-Sea Squid and Rays"},
    {"S06", "Blacktip Reef Shark", "CSTL", "Reef Fish, Cephalopods, and Crustaceans"},
    {"S07", "Blind Shark (Peekaboo Shark)", "CSTL", "Small Fish, Crabs, and Marine Worms"},
    {"S08", "Blue Shark", "PLGC", "Pelagic Squid & Small Bony Fish (Herring)"},
    {"S09", "Bluegrey Carpetshark (Ocean Tapestry)", "CSTL", "Benthic Invertebrates & Bottom Fish"},
    {"S10", "Bluntnose Sixgill Shark (The Deep Titan)", "DEEP", "Deep-Sea Fish, Rays, and Pinnipeds (Opportunistic)"},
    {"S11", "Bramble Shark", "DEEP", "Benthic Cephalopods & Small Deep-Sea Rays"},
    {"S12", "Brazilian Angel Shark", "CSTL", "Small Rays, Crustaceans, and Worms"},
    {"S13", "Broadnose Sevengill Shark (Primeval Beast)", "APEX", "Marine Mammals & Large Coastal Fish"},
    {"S14", "Bull Shark", "APEX", "Bony Fish, Smaller Sharks, and Sea Turtles"},
    {"S15", "Black Dogfish (Centroscyllium sp.)", "DEEP", "Small Deep-Sea Squid & Shrimp"},
    {"S16", "Clouded Angel Shark", "CSTL", "Flatfish and Benthic Crustaceans"},
    {"S17", "Common Angel Shark", "CSTL", "Flatfish, Crabs, and Mollusks"},
    {"S18", "Cookiecutter Shark", "DEEP", "Flesh Plugs from Tunas, Whales, and Seals (Parasitic)"},
    {"S19", "Crested Bullhead Shark (Shellbreaker)", "CSTL", "Hard-Shelled Invertebrates (Urchins, Mollusks)"},
    {"S20", "Great White Shark", "APEX", "Marine Mammals & Large Pelagic Fish"},
    {"S21", "Greenland Shark", "DEEP", "Arctic Fish, Seals, and Carrion"},
    {"S22", "Horn Shark (Spiral Maker)", "CSTL", "Sea Urchins & Hard-Shelled Mollusks"},
    {"S23", "Japanese Sawshark", "CSTL", "Small Fish and Crustaceans"},
    {"S24", "Leopard Shark", "CSTL", "Worms, Clams, and Benthic Crustaceans"},
    {"S25", "Longfin Mako Shark", "PLGC", "Fast-Swimming Pelagic Fish (Tuna, Swordfish)"},
    {"S26", "Longnose Sawshark", "CSTL", "Benthic Fish and Crustaceans"},
    {"S27", "Mexican Hornshark (Pacific Ram)", "CSTL", "Sea Urchins and Mollusks"},
    {"S28", "Nurse Shark (Cat Shark)", "CSTL", "Lobsters, Shrimps, and Small Fish"},
    {"S29", "Oceanic Whitetip Shark", "PLGC", "Bony Fish, Dead Whales, and Carrion"},
    {"S30", "Pacific Angelshark", "CSTL", "Flatfish and Rockfish"},
    {"S31", "Porbeagle Shark", "PLGC", "Bony Fish (Mackerel, Herring, Hake)"},
    {"S32", "Salmon Shark", "PLGC", "Salmon, Herring, and Pollock"},
    {"S33", "Sharpnose Sevengill Shark (Gill Seer)", "DEEP", "Small Deep Fish and Squid"},
    {"S34", "Shortfin Mako Shark", "PLGC", "Fast-Swimming Fish (Tuna, Swordfish)"},
    {"S35", "Shortnose Sawshark", "DEEP", "Deep-Sea Invertebrates & Fish"},
    {"S36", "Sixgill Sawshark", "CSTL", "Small Rays and Crustaceans"},
    {"S37", "Smoothback Angelshark", "CSTL", "Flatfish and Benthic Fish"},
    {"S38", "Spiny Dogfish", "CSTL", "Small Bony Fish, Squid, and Invertebrates"},
    {"S39", "Tiger Shark", "APEX", "Anything (Turtles, Seals, Birds, Fish, and Carrion)"}, // Index 38
    {"S40", "Velvet Dogfish", "DEEP", "Deep-Sea Squid and Hake"},
    {"S41", "Whale Shark", "FLTR", "Plankton, Krill, and Small Fish"},
    {"S42", "Whitespotted Bullhead Shark (Bullhead Phantom)", "CSTL", "Benthic Invertebrates & Sea Urchins"}
};

const int NUM_SHARKS = sizeof(SHARK_PROFILES) / sizeof(SharkProfile);

// --- CONFIGURATION CONSTANTS (SELECT SHARK HERE) ---
const int CURRENT_SHARK_INDEX = 38; 

// Fixed geographical coordinates (Monoufya, EGYPT) for simulation of a 'coastal' range
const float BASE_LATITUDE = 30.5694;
const float BASE_LONGITUDE = 31.993;
const float DITHER_RANGE = 0.005; // 0.005 degrees latitude/longitude for simulated movement
const float SIMULATED_MAX_DEPTH = 15.0; // Simulated depth in meters (fixed for this test)

// Time intervals (Updated from original 'interval')
const unsigned long SIM_INTERVAL = 5000;    // Serial Log / Data Calculation interval: 5 seconds
const unsigned long DATA_SEND_INTERVAL = 30000; // HTTP POST to Google Sheet interval: 30 seconds

// --- DATA STRUCTURES: Prey Ranges (7 distinct, conceptual habitats) ---

// Structure for defining a geographical box for prey ranges
struct PreyRange {
    float latMin, latMax;
    float lonMin, lonMax;
    const char* preyName; // General name of prey in this zone 
    const char* habitatTag; // Tag for contextual analysis
};

// Define the simulated prey ranges (These coordinates are fabricated for testing)
const PreyRange MARINE_PREY_RANGES[] = {
    // Range 0: Coral Reef/Rocky Coastal - Matches base location
    {30.560, 30.575, 30.990, 31.005, "Coastal Reef Fish & Mollusks", "P_Coral_Reef"},
    
    // Range 1: Temperate Coastal/Shelf 
    {30.000, 30.550, 30.000, 31.000, "Baitfish & Rays (Sardines, Herring, Skates)", "P_Temperate_Coastal"},
    
    // Range 2: High Seas Surface 
    {32.000, 35.000, 35.000, 40.000, "Tuna & Billfish (Mahi-Mahi, Wahoo, Squid)", "P_High_Seas_Surface"},
    
    // Range 3: Marine Mammal Breeding Grounds 
    {30.000, 30.200, 32.000, 32.200, "Marine Mammals & Turtles (Seals, Dolphins, Turtles)", "P_Breeding_Ground"},

    // Range 4: Abyssal Deep Trench 
    {35.000, 40.000, 30.000, 31.000, "Abyssal Squid & Benthic Inverts", "P_Abyssal_Deep"},
    
    // Range 5: Pelagic Midwater Zone 
    {28.000, 30.000, 34.000, 35.000, "Midwater Organisms (Deep-Sea Fish, Gelatinous Zooplankton)", "P_Pelagic_Midwater"},

    // Range 6: Shallow Filter Zone - This range is broad and covers the base location
    {30.000, 31.000, 30.000, 32.000, "Shallow Water Plankton & Krill", "P_Plankton_Shallow"}
};
const int NUM_PREY_RANGES = sizeof(MARINE_PREY_RANGES) / sizeof(MARINE_PREY_RANGES[0]);


// --- GLOBAL VARIABLES ---
TinyGPSPlus gps;
unsigned long lastMsg = 0;      // Tracks last 5-second serial log (original logic)
unsigned long lastDataSend = 0; // Tracks last 30-second HTTP POST
int eatingCount = 0;

// =========================================================================
// FUNCTION PROTOTYPES
// =========================================================================
void connectWiFi();
void sendDataToSheet(const SharkProfile& shark, float lat, float lon, float depth, const String& dietStatus, int eventCount);
void executeDataCycle(const SharkProfile& currentShark, bool forceEating); // New function for logging/sending
void calculateOrientation(const sensors_event_t &a, float &roll, float &pitch);
bool detectEatingEvent(float accelMag, const sensors_event_t &a, const sensors_event_t &g);
String getSharkDiet(float latitude, float longitude, const SharkProfile& currentShark);
const char* getHabitatName(const char* tag);

// =========================================================================
// SETUP AND LOOP
// =========================================================================

void setup() {
    // Check if the selected index is valid
    if (CURRENT_SHARK_INDEX < 0 || CURRENT_SHARK_INDEX >= NUM_SHARKS) {
        Serial.begin(115200);
        Serial.println("FATAL ERROR: CURRENT_SHARK_INDEX is out of bounds (0-41).");
        while(1) delay(100); // Halt execution
    }

    const SharkProfile& currentShark = SHARK_PROFILES[CURRENT_SHARK_INDEX];

    // --- SERIAL SETUP AND INITIAL CHECK ---
    Serial.begin(115200);
    delay(100);

    Serial.println("\n--- FinTrack Wi-Fi Tracker Startup (Baud: 115200) ---");

    Serial.println("!!! COMMANDS: Type 'reset' to clear count, or 'eat' to simulate an event an event. !!!");
    
    // Connect to Wi-Fi before the main loop starts
    connectWiFi();

    Serial.print("Simulated Shark: ID:"); Serial.print(currentShark.id); 
    Serial.print(", Name: "); Serial.print(currentShark.name); 
    Serial.print(", Type: "); Serial.print(currentShark.type);
    Serial.print(", Primary Diet: "); Serial.println(currentShark.primaryDiet);
    
    Serial.print("Simulated Location (Monoufya, EGYPT): ");
    Serial.print(BASE_LATITUDE, 6);
    Serial.print(", ");
    Serial.print(BASE_LONGITUDE, 6);
    Serial.println(" (Base location is within P_Coral_Reef and P_Plankton_Shallow)");
    Serial.println("-------------------------------------");

    randomSeed(analogRead(0));

    // Initialize GPS Serial port (assuming Serial1 for hardware serial)
    Serial1.begin(9600);

    delay(100);
}

void loop() {
    unsigned long now = millis();
    const SharkProfile& currentShark = SHARK_PROFILES[CURRENT_SHARK_INDEX];

    // Keep reading the GPS line for time data
    while (Serial1.available() > 0) {
        if (gps.encode(Serial1.read())) {
            // GPS data successfully encoded
        }
    }

    // --- CHECK FOR SERIAL COMMANDS (NEW LOGIC) ---
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        command.trim();
        
        if (command.equalsIgnoreCase("reset")) {
            eatingCount = 0;
            Serial.println("!!! COMMAND: Eating count reset by user command.");
        } 
        else if (command.equalsIgnoreCase("eat")) {
            Serial.println("!!! COMMAND: Forcing an immediate eating event log and data send.");
            // Immediately execute a data cycle, forcing the 'isEating' flag to true
            executeDataCycle(currentShark, true);
        }
    }

    // --- TIMED DATA CALCULATION AND LOGGING (5 second interval) ---
    if (now - lastMsg > SIM_INTERVAL) {
        lastMsg = now; 
        
        // Execute the data cycle based on simulated sensor readings
        executeDataCycle(currentShark, false);
    }
}

// =========================================================================
// CORE DATA PROCESSING FUNCTION (Replaces the main loop logic)
// =========================================================================

/**
 * @brief Performs a full data collection, logging, and transmission cycle.
 * @param currentShark The profile of the shark being tracked.
 * @param forceEating If true, overrides sensor data to simulate an eating event.
 */
void executeDataCycle(const SharkProfile& currentShark, bool forceEating) {
    unsigned long now = millis();
    
    // Declare structures for simulated data
    sensors_event_t a, g, temp;
    float accelMag;
    float currentRoll, currentPitch;
    float latitude, longitude;
    float currentDepth = SIMULATED_MAX_DEPTH;
    
    // --- SIMULATE SENSOR DATA (MPU6050 Mock) ---
    float base_accel = (float)random(90, 105) / 100.0; // Base magnitude between 0.90 G and 1.05 G
    float gyro_spike = 0.5;

    // Sensor spike logic: use 15% chance OR force the event
    bool sensorSpike = forceEating || (random(0, 100) < 15);

    if (sensorSpike) {
        base_accel = (float)random(150, 250) / 100.0; // Spike: 1.50 G to 2.50 G
        gyro_spike = 6.0; // Add a corresponding spike in rotation (rad/s)
    }

    // Populate simulated acceleration data
    a.acceleration.x = base_accel;
    a.acceleration.y = 0.5 + ((float)random(0, 10) / 100.0);
    a.acceleration.z = 0.8 + ((float)random(0, 10) / 100.0);

    // Populate simulated gyro data
    g.gyro.x = gyro_spike;
    g.gyro.y = 0.1;
    g.gyro.z = 0.1;

    // Calculate the acceleration magnitude based on the mocked data
    accelMag = sqrt(a.acceleration.x * a.acceleration.x +
                    a.acceleration.y * a.acceleration.y +
                    a.acceleration.z * a.acceleration.z);
    // ------------------------------------------

    calculateOrientation(a, currentRoll, currentPitch);

    // --- FORCED COORDINATES WITH DITHERING ---
    float randomFactor = (float)(rand() % 200 - 100) / 100.0;
    latitude = BASE_LATITUDE + randomFactor * DITHER_RANGE;
    longitude = BASE_LONGITUDE + randomFactor * DITHER_RANGE;
    // ------------------------------------------

    // Current hour is primarily for context.
    int currentHour = (gps.time.isValid()) ? gps.time.hour() : (now / 3600000) % 24;

    // Use forced event or check if sensor spike triggers a detection
    bool isEating = forceEating || detectEatingEvent(accelMag, a, g);

    String dietReport = "Normal Traversal";
    if (isEating) {
        eatingCount++;
        // Pass the entire shark profile struct reference
        dietReport = getSharkDiet(latitude, longitude, currentShark);
    }
    
    // --- SERIAL MONITOR LOGGING ---
    Serial.println("-------------------------------------");
    Serial.print("Time (Mock H): "); Serial.println(currentHour);
    Serial.print("Lat/Lon: "); Serial.print(latitude, 6); Serial.print(", "); Serial.println(longitude, 6);
    Serial.print("Depth (m): "); Serial.println(currentDepth);
    Serial.print("Accel Mag (G): "); Serial.println(accelMag, 3);
    Serial.print("Roll/Pitch (deg): "); Serial.print(currentRoll, 1); Serial.print(", "); Serial.println(currentPitch, 1);
    Serial.print("Diet Status: "); Serial.println(dietReport);
    Serial.print("Total Eating Events: "); Serial.println(eatingCount);

    if (gps.time.isValid() && gps.date.isValid()) {
        Serial.print("GPS Date/Time: ");
        Serial.print(gps.date.year()); Serial.print("-");
        Serial.print(gps.date.month()); Serial.print("-");
        Serial.print(gps.date.day()); Serial.print(" ");
        Serial.print(gps.time.hour()); Serial.print(":");
        Serial.print(gps.time.minute()); Serial.print(":");
        Serial.println(gps.time.second());
    }

    // --- GOOGLE SHEET HTTP POST LOGIC ---
    if (forceEating || (now - lastDataSend > DATA_SEND_INTERVAL)) {
         lastDataSend = now;
         if (WiFi.status() == WL_CONNECTED) {
            Serial.println("--- Sending Data to Google Sheet ---");
            sendDataToSheet(currentShark, latitude, longitude, currentDepth, dietReport, eatingCount);
         } else {
            Serial.println("--- WiFi Disconnected. Attempting Reconnect... ---");
            connectWiFi();
         }
    }
}


// =========================================================================
// FUNCTION IMPLEMENTATIONS (Wi-Fi and HTTP)
// =========================================================================

/**
 * @brief Attempts to connect to the configured Wi-Fi network.
 */
void connectWiFi() {
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);
    int attempts = 0;

    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi connected successfully.");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\nWiFi connection failed. Check credentials.");
    }
}

/**
 * @brief Sends a JSON payload of sensor data to the Google Apps Script Web App.
 */
void sendDataToSheet(const SharkProfile& shark, float lat, float lon, float depth, const String& dietStatus, int eventCount) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Error: WiFi not connected. Cannot send data.");
        return;
    }

    WiFiClient client;
    HTTPClient http;

    // Create the JSON payload. Keys MUST match your Google Script (Code.gs).
    String jsonPayload = "{";
    jsonPayload += "\"shark_id\":\"" + String(shark.id) + "\",";
    jsonPayload += "\"shark_name\":\"" + String(shark.name) + "\",";
    jsonPayload += "\"primary_diet\":\"" + String(shark.primaryDiet) + "\",";
    jsonPayload += "\"latitude\":" + String(lat, 6) + ",";
    jsonPayload += "\"longitude\":" + String(lon, 6) + ",";
    jsonPayload += "\"depth\":" + String(depth, 1) + ",";
    jsonPayload += "\"diet_status\":\"" + dietStatus + "\",";
    jsonPayload += "\"eating_count\":" + String(eventCount);
    jsonPayload += "}";

    http.begin(client, GOOGLE_SCRIPT_URL);
    http.addHeader("Content-Type", "application/json");

    int httpCode = http.POST(jsonPayload);

    if (httpCode > 0) {
        String payload = http.getString();
        Serial.print("HTTP Code: "); Serial.println(httpCode);
        Serial.print("Server Response: "); Serial.println(payload);
    } else {
        Serial.print("HTTP POST failed, error: ");
        Serial.println(http.errorToString(httpCode).c_str());
    }

    http.end();
}

/**
 * @brief Calculates Roll and Pitch from MPU6050 accelerometer data.
 */
void calculateOrientation(const sensors_event_t &a, float &roll, float &pitch) {
    roll = atan2(a.acceleration.y, sqrt(a.acceleration.x * a.acceleration.x + a.acceleration.z * a.acceleration.z)) * 180.0 / PI;
    pitch = atan2(a.acceleration.x, a.acceleration.z) * 180.0 / PI;
}

/**
 * @brief Detects a simulated shark eating event based on sensor data thresholds.
 */
bool detectEatingEvent(float accelMag, const sensors_event_t &a, const sensors_event_t &g) {
    // Requires a high acceleration spike and a high rotation spike simultaneously
    if (accelMag > 1.5 && g.gyro.x > 5.0) {
        return true;
    }
    return false;
}

/**
 * @brief Maps a habitat tag to a friendly, descriptive name.
 */
const char* getHabitatName(const char* tag) {
    if (strcmp(tag, "P_Coral_Reef") == 0) return "Coastal Reef Habitat";
    if (strcmp(tag, "P_Temperate_Coastal") == 0) return "Temperate Shelf Habitat";
    if (strcmp(tag, "P_High_Seas_Surface") == 0) return "Open Ocean (Surface) Habitat";
    if (strcmp(tag, "P_Breeding_Ground") == 0) return "Marine Mammal/Turtle Migration Route";
    if (strcmp(tag, "P_Abyssal_Deep") == 0) return "Deep Abyssal Trench";
    if (strcmp(tag, "P_Pelagic_Midwater") == 0) return "Pelagic Midwater Zone";
    if (strcmp(tag, "P_Plankton_Shallow") == 0) return "Plankton-Rich Filter Zone";
    return "Unknown/Off-Range Location";
}

/**
 * @brief Determines the likely prey based on location and shark type, focusing on the specific diet.
 */
String getSharkDiet(float latitude, float longitude, const SharkProfile& currentShark) {
    // 1. Initialize the base string with identification and specific diet information
    String result = "ID: ";
    result += currentShark.id;
    result += ", Name: ";
    result += currentShark.name;
    result += " | CONFIRMED DIET: ";
    result += currentShark.primaryDiet; // Use the specific diet directly
    result += " | "; // Separator

    const char* detectedHabitatTag = "UNKNOWN";

    // 2. Determine the Habitat Tag based on current GPS location
    for (int i = 0; i < NUM_PREY_RANGES; i++) {
        if (latitude >= MARINE_PREY_RANGES[i].latMin && latitude <= MARINE_PREY_RANGES[i].latMax &&
            longitude >= MARINE_PREY_RANGES[i].lonMin && longitude <= MARINE_PREY_RANGES[i].lonMax) {
            
            detectedHabitatTag = MARINE_PREY_RANGES[i].habitatTag;
            break; // Found the habitat, stop searching
        }
    }
    
    // 3. Provide context based on the habitat tag
    const char* habitatName = getHabitatName(detectedHabitatTag);
    result += "Habitat Context: ";
    result += habitatName;

    return result;
}
