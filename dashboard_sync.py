import folium
from pymongo import MongoClient
import urllib.parse

# 1. DATABASE CONNECTION
password = urllib.parse.quote_plus("Ganesh@69") 
uri = f"mongodb+srv://Ganesh69:{password}@cluster0.vgrea6x.mongodb.net/?appName=Cluster0"

client = MongoClient(uri)
db = client['smart_sentinel_db']
black_spots_col = db['black_spots']
services_col = db['services']

def generate_live_map():
    # 2. CREATE MAP CENTERED AROUND YOUR DATA (Ootagadda/Vizianagaram)
    # Default location ga Ootagadda petti map start chedham
    m = folium.Map(location=[18.144965, 83.432859], zoom_start=13)

    # 3. ADD BLACK SPOTS FROM CLOUD
    for spot in black_spots_col.find():
        folium.Circle(
            location=spot['coords'],
            radius=500, # 500 Meters alert zone
            color='red',
            fill=True,
            fill_color='red',
            popup=f"⚠️ {spot['name']}: {spot['reason']}"
        ).add_to(m)

    # 4. ADD SERVICES FROM CLOUD
    services_data = services_col.find_one()
    if services_data:
        # Mechanics (Blue Markers)
        for shop in services_data.get('mechanic', []):
            folium.Marker(
                location=shop['coords'],
                popup=f"🛠️ {shop['name']}: {shop['phone']}",
                icon=folium.Icon(color='blue', icon='wrench', prefix='fa')
            ).add_to(m)
        
        # Medical (Green Markers)
        for shop in services_data.get('medical', []):
            folium.Marker(
                location=shop['coords'],
                popup=f"🏥 {shop['name']}: {shop['phone']}",
                icon=folium.Icon(color='green', icon='plus-sign')
            ).add_to(m)

    # 5. SAVE AND SHOW
    m.save("index.html")
    print("✅ Mawa! Live Dashboard Map ready aindi. Open index.html to see.")

if __name__ == "__main__":
    generate_live_map()