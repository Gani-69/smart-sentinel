import folium

# Database coordinates
BLACK_SPOTS = [
    {"name": "Gachibowli Sharp Curve", "coords": (17.4474, 78.3762), "reason": "High Accident Zone"},
    {"name": "Junction 4", "coords": (17.4500, 78.3800), "reason": "Blind Spot"}
]

SERVICES = {
    "mechanic": [
        {"name": "Siva Puncture Shop", "coords": (17.4480, 78.3750), "phone": "9876543210"},
        {"name": "National Car Garage", "coords": (17.4400, 78.3800), "phone": "9123456789"}
    ]
}

def build_dashboard():
    # Hyderabad center ga map start
    m = folium.Map(location=[17.4474, 78.3762], zoom_start=15)

    # Accident Zones - RED CIRCLES
    for spot in BLACK_SPOTS:
        folium.Circle(
            location=spot['coords'],
            radius=200, 
            popup=f"DANGER: {spot['name']}",
            color='red',
            fill=True,
            fill_color='red'
        ).add_to(m)

    # Mechanics - BLUE MARKERS
    for shop in SERVICES['mechanic']:
        folium.Marker(
            location=shop['coords'],
            popup=f"{shop['name']} - {shop['phone']}",
            icon=folium.Icon(color='blue', icon='wrench', prefix='fa')
        ).add_to(m)

    # Save as HTML
    m.save('travel_mate_dashboard.html')
    print("✅ Dashboard Ready! Folder lo 'travel_mate_dashboard.html' chudu.")

if __name__ == "__main__":
    build_dashboard()