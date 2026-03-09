from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from geopy.distance import geodesic
from pymongo import MongoClient
import urllib.parse
import certifi
import random
from textblob import TextBlob

app = Flask(__name__)

# --- 1. CONFIGURATION & DATABASE ---
EMERGENCY_CONTACT = "whatsapp:+919110760928"

password = urllib.parse.quote_plus("Ganesh@69") 
uri = f"mongodb+srv://Ganesh69:{password}@cluster0.vgrea6x.mongodb.net/?appName=Cluster0"

try:
    # SSL/Handshake issues bypass with tlsAllowInvalidCertificates
    client = MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=5000)
    db = client['smart_sentinel_db']
    black_spots_col = db['black_spots']
    services_col = db['services'] 
    user_logs_col = db['user_logs'] 
    client.admin.command('ping')
    print("✅ Connected to MongoDB Atlas Successfully!")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

# --- 2. HELPER FUNCTIONS ---

def get_dynamic_report(user_pos):
    """Danger zones and black spots scan logic"""
    try:
        all_spots = list(black_spots_col.find())
        alerts = []
        for spot in all_spots:
            dist = geodesic(user_pos, tuple(spot['coords'])).km
            if dist < 0.5:
                alerts.append(f"🔴 *IMMEDIATE ALERT:* {spot['name']} is {int(dist*1000)}m away! \n👉 {spot['reason']}")
            elif dist < 10.0:
                alerts.append(f"⚠️ *UPCOMING:* {spot['name']} in {dist:.1f} km. \n👉 {spot['reason']}")
        return "\n\n".join(alerts) if alerts else "✅ *Route Clear:* No danger zones detected in 10km radius."
    except Exception:
        return "⚠️ Unable to fetch safety data at this moment mawa."

def get_mock_health():
    """Advanced Vehicle Health - Inspired by Taabi AI"""
    temp, fuel = random.randint(80, 98), random.randint(15, 85)
    battery = round(random.uniform(12.5, 14.2), 1)
    tires = [random.randint(30, 35) for _ in range(4)]
    return (f"📊 *Vehicle Health Update*\n"
            f"--------------------------\n"
            f"🌡️ Engine: {temp}°C | ⛽ Fuel: {fuel}%\n"
            f"🔋 Battery: {battery}V\n"
            f"🚗 Tires (PSI): {tires[0]}, {tires[1]}, {tires[2]}, {tires[3]}\n"
            f"✅ Status: All systems are kummings, mawa!")

# --- 3. MAIN BOT ROUTE ---

@app.route("/bot", methods=['POST'])
def bot():
    user_msg = request.values.get('Body', '').lower().strip()
    lat = request.values.get('Latitude')
    lon = request.values.get('Longitude')
    sender = request.values.get('From')

    resp = MessagingResponse()
    msg = resp.message()

    greetings = [
        "Hi mawa! Smart Sentinel is active. 🛡️",
        "Hello baa! Safety scan cheddama? 🚀",
        "Namaste mawa! Ready for the ride? 😎",
        "Yo bro! Location share chey, nenu chusukunta! 🏎️"
    ]

    # --- A. LOCATION LOGIC ---
    if lat and lon:
        user_pos = (float(lat), float(lon))
        
        # 1. UPSERT (Update existing or Insert new)
        user_logs_col.update_one(
            {"sender": sender},
            {"$set": {"coords": [user_pos[0], user_pos[1]], "last_seen": "Real-time"}},
            upsert=True
        )

        # 2. CROWDSOURCING (User adding a service)
        if 'add' in user_msg:
            s_name = user_msg.replace('add', '').strip().title()
            if not s_name: s_name = "User Service"
            services_col.update_one(
                {"name": s_name, "coords": [user_pos[0], user_pos[1]]},
                {"$set": {"type": "Crowdsourced", "verified": False}},
                upsert=True
            )
            msg.body(f"✅ Adirindi mawa! '{s_name}' database lo add chesa. Future drivers ki idi help avthundi! 📍")
            return str(resp)

        # 3. NEARBY SERVICES DISCOVERY
        nearby = []
        try:
            for s in services_col.find():
                s_coords = s.get('coords')
                if s_coords:
                    d = geodesic(user_pos, tuple(s_coords)).km
                    if d < 2.5: 
                        nearby.append(f"🏢 {s.get('name', 'Service')} ({d:.1f} km)")
        except Exception:
            pass
        
        service_text = "\n".join(nearby) if nearby else "No nearby services found mawa."

        # 4. FINAL LOCATION RESPONSE
        safety_text = get_dynamic_report(user_pos)
        msg.body(f"🛡️ *Safety Report:* \n{safety_text}\n\n📍 *Nearby Services:* \n{service_text}\n\n✅ Cloud Sync Successful!")

    # --- B. CONVERSATIONAL LOGIC ---
    elif user_msg:
        sentiment = TextBlob(user_msg).sentiment.polarity
        
        if any(greet in user_msg for greet in ['hi', 'hello', 'namaste', 'hey']):
            msg.body(random.choice(greetings))
        elif 'status' in user_msg:
            msg.body(get_mock_health())
        elif 'sos' in user_msg or 'emergency' in user_msg:
            msg.body("🚨 *EMERGENCY!* \n\nMawa, fast ga live location share chey! 📍")
        elif sentiment > 0.5:
            msg.body("Abba! Thanks mawa, nuvvu thope anthe! 🔥")
        elif sentiment < -0.3:
            msg.body("Em ayindi mawa? Chill, drive safe! 👊")
        else:
            msg.body("Artham ayindi mawa, kaani mundhu location pampu, route check cheddham! 🚀")

    return str(resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)