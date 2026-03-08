from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client # Ikkada kotha client add chesa
from geopy.distance import geodesic
from pymongo import MongoClient
import urllib.parse
import certifi
import random

app = Flask(__name__)

# --- CONFIGURATION ---
# Twilio Console nunchi nee SID and Token ikkada pettu mawa (Demo kosam logic rasthunna)
ACCOUNT_SID = 'AC...' 
AUTH_TOKEN = 'your_token'
TWILIO_NUMBER = 'whatsapp:+14155238886' 
EMERGENCY_CONTACT = "whatsapp:+919110760928" 

# 1. MONGODB CONNECTION SETUP
password = urllib.parse.quote_plus("Ganesh@69") 
uri = f"mongodb+srv://Ganesh69:{password}@cluster0.vgrea6x.mongodb.net/?appName=Cluster0"

client = MongoClient(uri, tlsCAFile=certifi.where())
db = client['smart_sentinel_db']
black_spots_col = db['black_spots']
services_col = db['services']

# --- HELPER FUNCTIONS ---

def get_dynamic_report(user_pos):
    all_spots = black_spots_col.find()
    alerts = []
    for spot in all_spots:
        dist = geodesic(user_pos, tuple(spot['coords'])).km
        if dist < 0.5:
            alerts.append(f"🔴 *IMMEDIATE ALERT:* {spot['name']} is just {int(dist*1000)}m away! \n👉 *Reason:* {spot['reason']}")
        elif dist < 10.0:
            alerts.append(f"⚠️ *UPCOMING:* {spot['name']} in {dist:.1f} km. \n👉 *Note:* {spot['reason']}")
    return "\n\n".join(alerts) if alerts else "✅ *Route Clear:* No danger zones detected for the next 10km."

def get_mock_health():
    temp = random.randint(75, 95)
    oil = random.randint(70, 90)
    battery = round(random.uniform(12.1, 14.2), 1)
    status = (
        "📊 *Smart Sentinel: Vehicle Diagnostics*\n"
        "--------------------------\n"
        f"🌡️ Engine Temp: {temp}°C {'✅' if temp < 90 else '⚠️'}\n"
        f"🛢️ Oil Level: {oil}% ✅\n"
        f"🔋 Battery: {battery}V (Healthy) ✅\n"
        "🏎️ Live Tracking: Enabled\n\n"
        "All systems operational, mawa!"
    )
    return status

@app.route("/bot", methods=['POST'])
def bot():
    user_msg = request.values.get('Body', '').lower().strip()
    lat = request.values.get('Latitude')
    lon = request.values.get('Longitude')

    resp = MessagingResponse()
    msg = resp.message()

    # --- 1. LOCATION LOGIC ---
    if lat and lon:
        user_pos = (float(lat), float(lon))
        
        # --- SOS TRIGGER LOGIC ---
        if 'sos' in user_msg or 'emergency' in user_msg:
            google_map = f"https://www.google.com/maps?q={lat},{lon}"
            
            # Repu demo lo neeku reply vacchela ee message rasanu
            sos_confirmation = (
                f"🆘 *SOS TRIGGERED!* 🆘\n\n"
                f"Mawa, stay calm! I have initiated emergency protocols.\n"
                f"📞 *Alerting:* {EMERGENCY_CONTACT}\n"
                f"📍 *Location:* {google_map}\n\n"
                f"Emergency teams have been notified with your coordinates! 🛡️"
            )
            
            # Internal Debugging for Demo (Mee sir ki terminal lo chupinchu)
            print(f"!!! CRITICAL ALERT: SOS sent to {EMERGENCY_CONTACT} !!!")
            print(f"Location Coordinates: {lat}, {lon}")
            
            msg.body(sos_confirmation)
            return str(resp)

        # Normal Safety Report
        safety_text = get_dynamic_report(user_pos)
        services_text = "\n\n--------------------------\n🛠️ *Nearby Services (15km):*\n"
        services_data = services_col.find_one()
        found_service = False
        
        if services_data:
            for cat in ['mechanic', 'medical']:
                for shop in services_data.get(cat, []):
                    d = geodesic(user_pos, tuple(shop['coords'])).km
                    if d < 15:
                        icon = "🔧" if cat == 'mechanic' else "🏥"
                        services_text += f"{icon} {shop['name']} ({d:.1f}km) 📞 {shop['phone']}\n"
                        found_service = True
        
        if not found_service:
            services_text += "No shops found nearby."
            
        msg.body(f"🛡️ *Smart Sentinel Safety Report* 🛡️\n\n{safety_text}{services_text}")

    # --- 2. COMMAND LOGIC ---
    elif 'hi' in user_msg or 'hello' in user_msg:
        msg.body("Hello! I am your *Smart Sentinel* 🛡️.\n\n📍 *Please Share your Location* to start the safety scan!")

    elif 'status' in user_msg:
        msg.body(get_mock_health())

    elif 'sos' in user_msg or 'emergency' in user_msg:
        msg.body("🚨 *Emergency Detected!* \n\nI need your live location to alert your emergency contact. Please *Share Location* now! 📍")

    else:
        msg.body("I didn't quite get that. Try saying 'Hi', 'Status', or share your location!")

    return str(resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)