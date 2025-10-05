import random
import numpy as np

# --- 1. CONFIGURATION ---
GRID_SIZE = 20        # 20x20 horizontal cells
DEPTH_LAYERS = 3      # 0: Shallow (0-20m), 1: Mid-Water (20-150m), 2: Deep/Twilight Zone (150m+)

# The 20x20 grid now represents a local area defined relative to the shark's current position.
# We'll use a 2.0 degree span (2.0° Lat x 2.0° Lon) centered on the current location.
LOCAL_GRID_DEGREE_SPAN = 2.0
HALF_SPAN = LOCAL_GRID_DEGREE_SPAN / 2.0
DEGREES_PER_CELL = LOCAL_GRID_DEGREE_SPAN / GRID_SIZE

# --- 2. SHARK HABITAT PROFILES ---
# Weights are used to prioritize environmental factors (0.0 to 1.0).
# Preference by Depth Layer: [Shallow (0-20m), Mid-Water (20-150m), Deep/Twilight (>150m)]
SHARK_PROFILES = {
    # Existing Species (Core)
    "Great white shark": {
        "description": "Pelagic deep-forager. Uses warm eddies (SWOT) as thermal conduits to access cold, deep prey (Twilight Zone).",
        "preferences": {
            "depth_preference": [0.1, 0.4, 1.0], 
            "is_coastal": 0.1,    
            "phytoplankton": 0.4, 
            "eddy_strength": 1.0  # HIGH: Essential for deep foraging
        }
    },
    "Tiger shark": {
        "description": "Coastal-pelagic generalist. Favors highly productive, warmer, shallow regions (PACE/MODIS).",
        "preferences": {
            "depth_preference": [0.9, 0.6, 0.1], 
            "is_coastal": 0.8,    
            "phytoplankton": 0.9, 
            "eddy_strength": 0.3  
        }
    },
    "Bull shark": {
        "description": "Euryhaline species. Strongest preference for shallow, coastal regions (low salinity areas/estuaries).",
        "preferences": {
            "depth_preference": [1.0, 0.2, 0.0], 
            "is_coastal": 1.0,    # HIGHEST: Very strong coastal preference
            "phytoplankton": 0.6, 
            "eddy_strength": 0.1  
        }
    },
    
    # New Pelagic (Mako/Porbeagle)
    "Shortfin mako shark": {
        "description": "Fast pelagic predator. Migrates long distances, follows productive oceanic fronts.",
        "preferences": {
            "depth_preference": [0.3, 0.9, 0.5], 
            "is_coastal": 0.2,    
            "phytoplankton": 0.8, # Follows the food chain
            "eddy_strength": 0.6  # Uses eddies to concentrate prey
        }
    },
    "Longfin mako shark": {
        "description": "Warm-water pelagic species, prefers deep offshore waters.",
        "preferences": {
            "depth_preference": [0.2, 0.7, 0.8], 
            "is_coastal": 0.1,    
            "phytoplankton": 0.7, 
            "eddy_strength": 0.7  
        }
    },
    "Porbeagle shark": {
        "description": "Cold-temperate water species, often found near continental shelves and banks.",
        "preferences": {
            "depth_preference": [0.5, 0.8, 0.3], 
            "is_coastal": 0.4,    
            "phytoplankton": 0.7, 
            "eddy_strength": 0.5  
        }
    },
    "Salmon shark": {
        "description": "North Pacific predator, follows salmon migrations, favors temperate surface waters.",
        "preferences": {
            "depth_preference": [0.8, 0.6, 0.1], 
            "is_coastal": 0.5,    
            "phytoplankton": 0.8, 
            "eddy_strength": 0.4  
        }
    },

    # New Filter Feeders
    "Whale shark": {
        "description": "Largest filter feeder, strictly planktonic. Strong preference for warm, highly productive surface waters.",
        "preferences": {
            "depth_preference": [1.0, 0.6, 0.0], # Surface feeder
            "is_coastal": 0.3,    
            "phytoplankton": 1.0, # CRITICAL FACTOR
            "eddy_strength": 0.5  # Eddies concentrate plankton
        }
    },
    "Basking shark": {
        "description": "Cosmopolitan filter feeder, often near coastlines and upwelling zones.",
        "preferences": {
            "depth_preference": [1.0, 0.7, 0.1], 
            "is_coastal": 0.6,    
            "phytoplankton": 1.0, # CRITICAL FACTOR
            "eddy_strength": 0.3  
        }
    },

    # New Deep-Sea & Benthic
    "Sharpnose sevengill shark (Gill Seer)": {
        "description": "Deep-water scavenger and hunter, prefers continental slopes.",
        "preferences": {
            "depth_preference": [0.0, 0.3, 1.0], 
            "is_coastal": 0.1,    
            "phytoplankton": 0.1, 
            "eddy_strength": 0.1  
        }
    },
    "Bluntnose sixgill shark (The Deep Titan)": {
        "description": "Largest deep-sea shark, prefers deep benthic habitats.",
        "preferences": {
            "depth_preference": [0.0, 0.1, 1.0], 
            "is_coastal": 0.0,    
            "phytoplankton": 0.0, 
            "eddy_strength": 0.0  
        }
    },
    "Broadnose sevengill shark (The Primeval Beast)": {
        "description": "Coastal to shelf-break species, known for aggressive hunting.",
        "preferences": {
            "depth_preference": [0.4, 0.7, 0.5], 
            "is_coastal": 0.7,    
            "phytoplankton": 0.3, 
            "eddy_strength": 0.2  
        }
    },
    "Bigeyed sixgill shark (Ancient Watche_ Green Lantern)": {
        "description": "Very deep water species, found on seamounts and mid-ocean ridges.",
        "preferences": {
            "depth_preference": [0.0, 0.0, 1.0], 
            "is_coastal": 0.0,    
            "phytoplankton": 0.0, 
            "eddy_strength": 0.1  
        }
    },
    "Greenland shark": {
        "description": "Arctic predator. Extremely slow, favors deep, cold waters.",
        "preferences": {
            "depth_preference": [0.1, 0.3, 1.0], 
            "is_coastal": 0.2,    
            "phytoplankton": 0.1, 
            "eddy_strength": 0.0  
        }
    },
    "Velvet dogfish": {
        "description": "Benthic species of the upper continental slope.",
        "preferences": {
            "depth_preference": [0.1, 0.5, 0.8], 
            "is_coastal": 0.3,    
            "phytoplankton": 0.1, 
            "eddy_strength": 0.1  
        }
    },
    "Bramble shark": {
        "description": "Rare, sluggish deep-water species. Benthic, deep continental shelf/slope.",
        "preferences": {
            "depth_preference": [0.0, 0.4, 0.9], 
            "is_coastal": 0.2,    
            "phytoplankton": 0.0, 
            "eddy_strength": 0.0  
        }
    },
    "Centroscyllium species (like the Black dogfish)": {
        "description": "Small, deep-water benthic sharks of the continental slope.",
        "preferences": {
            "depth_preference": [0.0, 0.2, 1.0], 
            "is_coastal": 0.0,    
            "phytoplankton": 0.0, 
            "eddy_strength": 0.0  
        }
    },

    # New Coastal & Benthic Generalists
    "Spiny dogfish": {
        "description": "Small, widespread coastal shark. Highly migratory along shelves.",
        "preferences": {
            "depth_preference": [0.8, 0.6, 0.2], 
            "is_coastal": 0.8,    
            "phytoplankton": 0.6, 
            "eddy_strength": 0.2  
        }
    },
    "Blue shark": {
        "description": "Highly migratory oceanic species. Prefers cooler, productive surface waters.",
        "preferences": {
            "depth_preference": [0.7, 0.8, 0.4], 
            "is_coastal": 0.2,    
            "phytoplankton": 0.9, 
            "eddy_strength": 0.8  
        }
    },
    "Oceanic whitetip shark": {
        "description": "Tropical/subtropical oceanic apex predator, often found around strong currents/eddies.",
        "preferences": {
            "depth_preference": [0.6, 0.9, 0.4], 
            "is_coastal": 0.1,    
            "phytoplankton": 0.7, 
            "eddy_strength": 0.9  
        }
    },
    "Blacktip reef shark": {
        "description": "Small, shallow-water reef specialist. Strongly coastal and shallow.",
        "preferences": {
            "depth_preference": [1.0, 0.1, 0.0], 
            "is_coastal": 1.0,    # Strictly coastal/reef
            "phytoplankton": 0.7, 
            "eddy_strength": 0.0  
        }
    },
    "Leopard shark": {
        "description": "Coastal, temperate bottom-dweller, found in bays and estuaries.",
        "preferences": {
            "depth_preference": [1.0, 0.3, 0.0], 
            "is_coastal": 0.9,    
            "phytoplankton": 0.6, 
            "eddy_strength": 0.1  
        }
    },
    "Nurse shark (cat shark)": {
        "description": "Sluggish, nocturnal benthic species, strong preference for coral reefs and mangroves.",
        "preferences": {
            "depth_preference": [1.0, 0.1, 0.0], 
            "is_coastal": 1.0,    
            "phytoplankton": 0.5, 
            "eddy_strength": 0.0  
        }
    },
    "Blind shark (Peekaboo Shark)": {
        "description": "Nocturnal, coastal benthic species, found in rocky reefs and kelp beds.",
        "preferences": {
            "depth_preference": [1.0, 0.1, 0.0], 
            "is_coastal": 1.0,    
            "phytoplankton": 0.5, 
            "eddy_strength": 0.0  
        }
    },
    "Bluegrey carpetshark (Ocean Tapestry)": {
        "description": "Small, benthic reef shark of tropical waters.",
        "preferences": {
            "depth_preference": [1.0, 0.1, 0.0], 
            "is_coastal": 1.0,    
            "phytoplankton": 0.5, 
            "eddy_strength": 0.0  
        }
    },
    "Cookiecutter shark": {
        "description": "Diel vertical migrator, specialized parasitic feeder, uses deep water for safety.",
        "preferences": {
            "depth_preference": [0.5, 0.5, 0.9], # Can be at any depth
            "is_coastal": 0.0,    
            "phytoplankton": 0.3, 
            "eddy_strength": 0.7  # Pelagic environment
        }
    },
    
    # New Horn & Bullhead Sharks (Benthic)
    "Horn shark (Spiral Maker)": {
        "description": "Small, temperate, benthic ambush predator. Found on reefs and rocky bottom.",
        "preferences": {
            "depth_preference": [1.0, 0.3, 0.0], 
            "is_coastal": 0.9,    
            "phytoplankton": 0.4, 
            "eddy_strength": 0.0  
        }
    },
    "Whitespotted bullhead shark (Bullhead Phantom)": {
        "description": "Benthic coastal species, feeds on hard-shelled invertebrates.",
        "preferences": {
            "depth_preference": [1.0, 0.2, 0.0], 
            "is_coastal": 0.9,    
            "phytoplankton": 0.4, 
            "eddy_strength": 0.0  
        }
    },
    "Crested bullhead shark (Shellbreaker)": {
        "description": "Benthic coastal species, feeds on hard-shelled invertebrates.",
        "preferences": {
            "depth_preference": [1.0, 0.2, 0.0], 
            "is_coastal": 0.9,    
            "phytoplankton": 0.4, 
            "eddy_strength": 0.0  
        }
    },
    "Mexican hornshark (Pacific Ram)": {
        "description": "Benthic species of the eastern Pacific, feeds on small invertebrates.",
        "preferences": {
            "depth_preference": [1.0, 0.3, 0.0], 
            "is_coastal": 0.9,    
            "phytoplankton": 0.4, 
            "eddy_strength": 0.0  
        }
    },
    
    # New Angelsharks (Benthic Ambush)
    "Common Angel Shark (Squatina squatina)": {
        "description": "Flat, benthic ambush predator, prefers soft sediments near shore.",
        "preferences": {
            "depth_preference": [0.9, 0.3, 0.0], 
            "is_coastal": 0.9,    
            "phytoplankton": 0.5, 
            "eddy_strength": 0.0  
        }
    },
    "Australian Angel Shark (Squatina australis)": {
        "description": "Flat, benthic ambush predator, temperate Australian waters.",
        "preferences": {
            "depth_preference": [0.9, 0.3, 0.0], 
            "is_coastal": 0.9,    
            "phytoplankton": 0.5, 
            "eddy_strength": 0.0  
        }
    },
    "Clouded Angel Shark (Squatina nebulosa)": {
        "description": "Flat, benthic ambush predator, western Pacific shelf.",
        "preferences": {
            "depth_preference": [0.9, 0.3, 0.0], 
            "is_coastal": 0.9,    
            "phytoplankton": 0.5, 
            "eddy_strength": 0.0  
        }
    },
    "Brazilian Angel Shark (Squatina guggenheim)": {
        "description": "Flat, benthic ambush predator, shallow Atlantic shelf.",
        "preferences": {
            "depth_preference": [0.9, 0.3, 0.0], 
            "is_coastal": 0.9,    
            "phytoplankton": 0.5, 
            "eddy_strength": 0.0  
        }
    },
    "Pacific Angelshark (Squatina californica)": {
        "description": "Flat, benthic ambush predator, rocky and soft bottoms.",
        "preferences": {
            "depth_preference": [0.9, 0.3, 0.0], 
            "is_coastal": 0.9,    
            "phytoplankton": 0.5, 
            "eddy_strength": 0.0  
        }
    },
    "Smoothback Angelshark (Squatina oculata)": {
        "description": "Flat, benthic ambush predator, Eastern Atlantic and Mediterranean.",
        "preferences": {
            "depth_preference": [0.9, 0.3, 0.0], 
            "is_coastal": 0.9,    
            "phytoplankton": 0.5, 
            "eddy_strength": 0.0  
        }
    },
    
    # New Sawsharks (Benthic)
    "Japanese Sawshark (Pristiophorus japonicus)": {
        "description": "Benthic shark of the continental shelf and slope, uses saw for hunting.",
        "preferences": {
            "depth_preference": [0.7, 0.6, 0.3], 
            "is_coastal": 0.7,    
            "phytoplankton": 0.4, 
            "eddy_strength": 0.1  
        }
    },
    "African Dwarf Sawshark (Pristiophorus nancyae)": {
        "description": "Small, deep-water sawshark, continental slope.",
        "preferences": {
            "depth_preference": [0.5, 0.7, 0.5], 
            "is_coastal": 0.4,    
            "phytoplankton": 0.3, 
            "eddy_strength": 0.1  
        }
    },
    "Longnose Sawshark (Pristiophorus nudipinnis)": {
        "description": "Benthic shark of the continental shelf and slope.",
        "preferences": {
            "depth_preference": [0.7, 0.6, 0.3], 
            "is_coastal": 0.7,    
            "phytoplankton": 0.4, 
            "eddy_strength": 0.1  
        }
    },
    "Bahamas Sawshark (Pristiophorus schroederi)": {
        "description": "Deep-water species of the Caribbean and Bahamas.",
        "preferences": {
            "depth_preference": [0.4, 0.7, 0.6], 
            "is_coastal": 0.3,    
            "phytoplankton": 0.3, 
            "eddy_strength": 0.1  
        }
    },
    "Sixgill Sawshark (Pliotrema warreni)": {
        "description": "Unique sixgill sawshark, continental shelf and slope.",
        "preferences": {
            "depth_preference": [0.6, 0.8, 0.4], 
            "is_coastal": 0.4,    
            "phytoplankton": 0.3, 
            "eddy_strength": 0.1  
        }
    },
    "Shortnose Sawshark (Pristiophorus nudipinnis)": {
        "description": "Benthic shark of the continental shelf and slope.",
        "preferences": {
            "depth_preference": [0.7, 0.6, 0.3], 
            "is_coastal": 0.7,    
            "phytoplankton": 0.4, 
            "eddy_strength": 0.1  
        }
    },
}

# Function to calculate the maximum theoretical HSI score for a profile
def calculate_max_hsi(profile):
    """Calculates the maximum possible Habitat Suitability Index for a given shark profile."""
    prefs = profile["preferences"]
    # Max Depth Preference is the maximum value in the list, as only one depth applies at a time
    max_depth_pref = max(prefs["depth_preference"])
    
    # All other environmental factors (coastal, phyto, eddy) max out at 1.0
    # Score = Depth_Pref * 1.0 + Coastal_Pref * Coastal_Factor + ...
    max_hsi = (
        max_depth_pref * 1.0 + 
        prefs["is_coastal"] * 1.0 +
        prefs["phytoplankton"] * 1.0 +
        prefs["eddy_strength"] * 1.0
    )
    return max_hsi

# --- 3. SIMULATED 3D OCEAN ENVIRONMENT GRID (Represents satellite data) ---

def generate_simulated_environment(size, depth_layers):
    """
    Simulates environmental data (derived from PACE, MODIS, SWOT) in 3D.
    The coastal simulation is now conceptual: Row 0 represents the closest conceptual shore 
    within the local 2 degree map centered on the shark's current position.
    """
    # Initialize 3D arrays
    shape = (size, size, depth_layers)
    environment = {
        "coastal_map": np.zeros(shape),
        "phytoplankton_abundance": np.zeros(shape),
        "eddy_strength": np.zeros(shape)
    }
    
    # 1. Coastal Map (Only varies horizontally, strongest at row 0, constant across depth)
    for i in range(size):
        # Coastal influence decreases as row index (i) increases (moves offshore)
        coastal_factor = 1.0 - (i / size)
        environment["coastal_map"][i, :, :] = coastal_factor
            
    # 2. Phytoplankton Abundance (Highest at surface, decreases with depth - PACE/MODIS)
    base_phyto = np.random.normal(0.5, 0.2, (size, size))
    for i in range(size):
        for j in range(size):
            environment["phytoplankton_abundance"][i, j, 0] = np.clip(base_phyto[i, j] + 0.3, 0.0, 1.0) 
            environment["phytoplankton_abundance"][i, j, 1] = np.clip(base_phyto[i, j], 0.0, 1.0)
            environment["phytoplankton_abundance"][i, j, 2] = np.clip(base_phyto[i, j] - 0.4, 0.0, 1.0) 
            
    # 3. Eddy Strength (Varies across all dimensions - SWOT/Articles)
    base_eddy = np.random.normal(0.3, 0.2, shape)
    
    # Simulate a strong warm eddy slightly offshore (center at [15, 5] grid index)
    for k in range(depth_layers):
        for i in range(size):
            for j in range(size):
                dist = np.sqrt((i - 15)**2 + (j - 5)**2)
                eddy_bump = max(0, (10 - dist) / 10) * 0.7 
                environment["eddy_strength"][i, j, k] = np.clip(base_eddy[i, j, k] + eddy_bump, 0.0, 1.0)
            
    return environment

# --- UTILITY FUNCTIONS: MAPPING ---

def map_lat_lon_to_grid(lat, lon, start_lat, start_lon):
    """
    Converts a global Lat/Lon to its Row/Col grid index within the local 2-degree map 
    centered on the start_lat/start_lon. (Not currently used for input, but kept for calculation.)
    """
    # Calculate difference from the center (start_lat/lon)
    lat_diff = lat - start_lat
    lon_diff = lon - start_lon
    
    # Normalize difference to a 0.0 to 1.0 scale within the HALF_SPAN
    normalized_lat = (lat_diff + HALF_SPAN) / LOCAL_GRID_DEGREE_SPAN
    normalized_lon = (lon_diff + HALF_SPAN) / LOCAL_GRID_DEGREE_SPAN
    
    # Map normalized values to grid indices (0 to GRID_SIZE - 1)
    # Row 0 of the grid is the lowest Lat boundary (Lat - HALF_SPAN)
    row = GRID_SIZE - 1 - int(normalized_lat * GRID_SIZE)
    col = int(normalized_lon * GRID_SIZE)

    row = np.clip(row, 0, GRID_SIZE - 1)
    col = np.clip(col, 0, GRID_SIZE - 1)

    return row, col

def map_grid_to_lat_lon_relative(row, col, start_lat, start_lon):
    """
    Converts 0-indexed Row/Col grid coordinates back to global Lat/Lon.
    """
    # Use (index + 0.5) to target the center of the grid cell
    
    # Map column (Longitude)
    normalized_lon = (col + 0.5) / GRID_SIZE
    lon_offset = normalized_lon * LOCAL_GRID_DEGREE_SPAN - HALF_SPAN
    lon = start_lon + lon_offset
    
    # Map row (Latitude). Row 0 is the highest Latitude edge of the span.
    normalized_lat = 1.0 - (row + 0.5) / GRID_SIZE
    lat_offset = normalized_lat * LOCAL_GRID_DEGREE_SPAN - HALF_SPAN
    lat = start_lat + lat_offset

    return lat, lon

# --- INPUT FUNCTIONS (No change) ---
def ask_for_shark_type():
    """Prompts the user to select the shark type."""
    print("\n--- Shark Species Selection ---")
    available_sharks = list(SHARK_PROFILES.keys())
    print("Available sharks for prediction:")
    # Sort the list alphabetically for easier selection
    available_sharks.sort() 
    
    for i, shark in enumerate(available_sharks):
        print(f"  [{i + 1}] {shark}")
        
    while True:
        try:
            choice = input(f"Enter the number corresponding to the shark: ")
            index = int(choice) - 1
            if 0 <= index < len(available_sharks):
                return available_sharks[index]
            else:
                print(f"Error: Choice must be between 1 and {len(available_sharks)}.")
        except ValueError:
            print("Error: Please enter a valid number.")

def ask_for_current_location():
    """Prompts the user for a starting location using global Lat/Lon and Depth."""
    print("\n--- Starting Location Input (Global Coordinates) ---")
    
    # 1. Get Latitude (Any value from -90 to 90)
    while True:
        try:
            lat_input = input(f"Enter the current LATITUDE (-90.0 to 90.0): ")
            lat = float(lat_input)
            if -90.0 <= lat <= 90.0: break
            else: print(f"Error: Latitude must be between -90.0 and 90.0.")
        except ValueError: print("Error: Please enter a valid number.")

    # 2. Get Longitude (Any value from -180 to 180)
    while True:
        try:
            # Updated prompt to clarify the full global range
            lon_input = input(f"Enter the current LONGITUDE (-180.0 to 180.0): ")
            lon = float(lon_input)
            if -180.0 <= lon <= 180.0: break
            else: print(f"Error: Longitude must be between -180.0 and 180.0.")
        except ValueError: print("Error: Please enter a valid number.")

    # 3. Get Depth
    while True:
        try:
            depth_input = input(f"Enter the current DEPTH LAYER (0=Shallow, 1=Mid, 2=Deep): ")
            depth = int(depth_input)
            if 0 <= depth < DEPTH_LAYERS: break
            else: print(f"Error: Depth must be 0, 1, or 2.")
        except ValueError: print("Error: Please enter a valid integer.")
            
    # For internal processing, the start point is always the center of the 20x20 grid (index 9, 9)
    # The actual coordinates are passed to the prediction mapping functions.
    start_row = 9 
    start_col = 9 
    
    return lat, lon, start_row, start_col, depth

# --- 4. MIGRATION PREDICTION LOGIC (Updated for 6-month scale) ---

def predict_next_location(shark_type, environment):
    """
    Calculates HSI for every cell, then aggregates scores into 4 major directional 
    sectors to determine the optimal long-distance migratory heading (6-month period).
    The prediction finds the most promising general direction (N, S, E, W) 
    within the local 2°x2° simulation and assumes a 15° migratory path.
    """
    profile = SHARK_PROFILES[shark_type]
    
    # 1. Calculate HSI for every 3D cell
    scores = np.zeros((GRID_SIZE, GRID_SIZE, DEPTH_LAYERS))
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            for k in range(DEPTH_LAYERS):
                # --- Environmental Data ---
                is_coastal = environment["coastal_map"][i, j, k]
                phytoplankton = environment["phytoplankton_abundance"][i, j, k]
                eddy_strength = environment["eddy_strength"][i, j, k]
                
                # --- Habitat Suitability Index (HSI) Calculation ---
                score = 0
                # All environmental factors are weighted by the shark's preference (0.0 to 1.0)
                score += profile["preferences"]["depth_preference"][k] * 1.0 
                score += profile["preferences"]["is_coastal"] * is_coastal
                score += profile["preferences"]["phytoplankton"] * phytoplankton
                score += profile["preferences"]["eddy_strength"] * eddy_strength
                scores[i, j, k] = score

    # 2. Determine the best score in each vertical water column (2D max score array)
    # This represents the best possible HSI if the shark can dive to the optimal depth
    max_scores_2d = np.max(scores, axis=2) 
    
    # 3. Define and average HSI scores across 4 major directional sectors
    directional_indices = {
        # Slicing is [Row, Col]
        "North": (slice(0, 10), slice(0, 20)),   # Rows 0-9 (highest Lat half)
        "South": (slice(10, 20), slice(0, 20)),  # Rows 10-19 (lowest Lat half)
        "East": (slice(0, 20), slice(10, 20)),   # Cols 10-19 (highest Lon half)
        "West": (slice(0, 20), slice(0, 10)),    # Cols 0-9 (lowest Lon half)
    }
    
    directional_averages = {}
    for direction, (r_slice, c_slice) in directional_indices.items():
        # Get the scores for this sector and calculate the average HSI
        sector_scores = max_scores_2d[r_slice, c_slice]
        directional_averages[direction] = np.mean(sector_scores)
        
    # 4. Identify the best migratory direction
    best_direction = max(directional_averages, key=directional_averages.get)
    max_sector_score = directional_averages[best_direction]
    
    # 5. Define the 6-month migration vector (approx. 15 degrees)
    # This vector determines the long-distance destination
    migration_delta = {
        "North": (15.0, 0.0),  # (Delta Lat, Delta Lon)
        "South": (-15.0, 0.0),
        "East": (0.0, 15.0),
        "West": (0.0, -15.0),
    }

    # 6. Find the absolute optimal depth *within the best sector* (for recommended start)
    r_slice, c_slice = directional_indices[best_direction]
    scores_in_sector = scores[r_slice, c_slice, :]
    
    # Find the maximum index (row, col, depth) relative to the sector slice
    relative_max_index = np.unravel_index(np.argmax(scores_in_sector), scores_in_sector.shape)
    optimal_depth = relative_max_index[2]

    # Return the migration vector, optimal depth, best sector score, and current score
    return migration_delta[best_direction], optimal_depth, max_sector_score, best_direction, scores[9, 9, :]

# --- 5. MAIN EXECUTION ---
def run_predictor():
    """Initializes the environment and runs predictions for the selected shark."""
    print("--- 3D Predictive Habitat Model Initialized (Global Coordinates) ---")
    print(f"Local simulation covers a {LOCAL_GRID_DEGREE_SPAN}°x{LOCAL_GRID_DEGREE_SPAN}° area to assess migratory potential.")
    
    ocean_environment = generate_simulated_environment(GRID_SIZE, DEPTH_LAYERS)
    
    selected_shark = ask_for_shark_type()
    profile = SHARK_PROFILES[selected_shark]
    
    start_lat, start_lon, start_row, start_col, start_depth = ask_for_current_location()
    
    print(f"\nAnalyzing conditions for the {selected_shark} at: ({start_lat:.4f}°, {start_lon:.4f}°)...")

    # Run the 6-month migration prediction
    (lat_delta, lon_delta), optimal_depth, max_sector_score, best_direction, current_scores = predict_next_location(selected_shark, ocean_environment)
    
    # Calculate the predicted 6-month destination
    optimal_lat = start_lat + lat_delta
    optimal_lon = start_lon + lon_delta
    
    # Handle longitude wrap-around (e.g., crossing the 180/-180 meridian)
    if optimal_lon > 180.0:
        optimal_lon -= 360.0
    elif optimal_lon < -180.0:
        optimal_lon += 360.0

    # The current HSI score is fixed at the center of the grid (index 9, 9)
    current_score = current_scores[start_depth]
    
    # Calculate Max HSI
    max_hsi = calculate_max_hsi(profile)
    
    # Environmental factors at the current location (center of the local map, fixed row/col)
    current_coastal_factor = ocean_environment["coastal_map"][start_row, start_col, start_depth]
    current_eddy_influence = ocean_environment["eddy_strength"][start_row, start_col, start_depth]
    current_phytoplankton = ocean_environment["phytoplankton_abundance"][start_row, start_col, start_depth]
    
    # Helper to interpret depth layer
    def get_depth_label(layer):
        return ["Shallow (0-20m)", "Mid-Water (20-150m)", "Deep/Twilight (>150m)"][layer]
        
    print("\n--- Habitat Suitability Analysis & 6-MONTH MIGRATION PREDICTION ---")
    
    current_habitat = "Conceptual Open Ocean"
    if start_row < 5:
         current_habitat = "Conceptual Transition Zone" if current_coastal_factor > 0.4 else "Open Ocean"
    if start_row == 0:
        current_habitat = "Conceptual Coastal Shelf"
    
    # Output the results
    print(f"\n==========================================")
    print(f"[{selected_shark.upper()} - Migratory Potential]")
    print(f"THEORETICAL MAXIMUM SUITABILITY: {max_hsi:.2f}")
    print(f"==========================================")
    
    print(f"  --- CURRENT POSITION SUITABILITY ---")
    print(f"  Coordinates: ({start_lat:.4f}°, {start_lon:.4f}°)")
    print(f"  Current Depth: {get_depth_label(start_depth)} ({start_depth})")
    print(f"  Current Suitability Score: {current_score:.2f} ({(current_score/max_hsi)*100:.1f}% of Max)")
    print(f"  - Key Environmental Factors (Local Simulation):")
    print(f"    - Phytoplankton (PACE/MODIS): {current_phytoplankton:.2f}")
    print(f"    - Eddy Influence (SWOT): {current_eddy_influence:.2f}")
    
    print(f"  --- PREDICTED 6-MONTH MIGRATION ---")
    print(f"  Optimal Direction: {best_direction.upper()} (Sector Avg HSI: {max_sector_score:.2f})")
    print(f"  Predicted Destination Coordinates: ({optimal_lat:.4f}°, {optimal_lon:.4f}°)")
    print(f"  Recommended Starting Depth for Migration: {get_depth_label(optimal_depth)}")
    print(f"  Est. Migratory Distance: ~15 degrees Lat/Lon change.")


if __name__ == "__main__":
    run_predictor()
