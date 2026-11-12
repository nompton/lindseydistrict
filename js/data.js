/* =========================================================
   Lindsey Street District — business directory data
   ---------------------------------------------------------
   Auto-generated from the district business spreadsheet.
   Safe to hand-edit. To add a business, copy a block in
   BUSINESSES and fill in the fields (blank fields are hidden).
   `category` must match a key in CATEGORIES below.
   Map pins are placed automatically from the street address
   (see approxCoords() in app.js); positions are APPROXIMATE.
   Add explicit  lat: 35.xx, lng: -97.xx  to a business to
   pin it precisely.
   ========================================================= */

const CATEGORIES = {
  food: { label: "Food", emoji: "\ud83c\udf7d\ufe0f" },
  service: { label: "Services", emoji: "\ud83d\udee0\ufe0f" },
  beauty: { label: "Health & Beauty", emoji: "\ud83d\udc87" },
  shop: { label: "Shops", emoji: "\ud83d\udecd\ufe0f" },
  auto: { label: "Automotive", emoji: "\ud83d\udd27" },
  bank: { label: "Banks & Finance", emoji: "\ud83c\udfe6" },
  smoke: { label: "Smoke & Vape", emoji: "\ud83d\udca8" },
  gym: { label: "Fitness", emoji: "\ud83c\udfcb\ufe0f" },
  fun: { label: "Entertainment", emoji: "\ud83c\udfb6" },
  civic: { label: "Civic", emoji: "\ud83c\udfdb\ufe0f" },
  education: { label: "Education", emoji: "\ud83d\udcda" },
  pets: { label: "Pets", emoji: "\ud83d\udc3e" },
  worship: { label: "Worship", emoji: "\u26ea" }
};

const BUSINESSES = [
  {"name": "McGee Street Animal Hospital", "category": "pets", "address": "1140 McGee, Norman, OK", "lat": 35.204745, "lng": -97.467852},
  {"name": "Flawless Auto Center", "category": "auto", "address": "1209 W Lindsey, Norman, OK", "lat": 35.203963, "lng": -97.459559},
  {"name": "Ron's Automotive", "category": "auto", "address": "1215 24th Ave SW, Norman, OK", "lat": 35.203281, "lng": -97.47659},
  {"name": "Mike's Tire & Auto", "category": "auto", "address": "1802 W Lindsey, Norman, OK", "lat": 35.20385, "lng": -97.467985},
  {"name": "Well's Automotive", "category": "auto", "address": "1901 W Lindsey, Norman, OK", "lat": 35.203972, "lng": -97.469271},
  {"name": "Mr. Short Stop", "category": "auto", "address": "2007 W Lindsey, Norman, OK", "lat": 35.203969, "lng": -97.470633},
  {"name": "O'Reilly Auto Parts", "category": "auto", "address": "2113 W Lindsey, Norman, OK", "lat": 35.203961, "lng": -97.474235},
  {"name": "Best of Imports", "category": "auto", "address": "2114 W Lindsey, Norman, OK", "lat": 35.203845, "lng": -97.473621},
  {"name": "Costa Oil", "category": "auto", "address": "2201 W Lindsey, Norman, OK", "phone": "(405) 561-6019", "website": "https://costaoils.com/oil-change/costa-oil-norman-ok/", "lat": 35.203961, "lng": -97.474318},
  {"name": "Midas", "category": "auto", "address": "2206 W Lindsey, Norman, OK", "lat": 35.203847, "lng": -97.474318},
  {"name": "Casey's", "category": "auto", "address": "2316 W Lindsey, Norman, OK", "lat": 35.203848, "lng": -97.475683},
  {"name": "True Sky Credit Union", "category": "bank", "address": "1212 W Lindsey, Norman, OK", "lat": 35.203849, "lng": -97.459491},
  {"name": "Security Finance Loans", "category": "bank", "address": "1213 W Lindsey, Norman, OK", "center": "Lindsey Park Center", "lat": 35.203963, "lng": -97.459609},
  {"name": "Continental Credit Loans", "category": "bank", "address": "1221 W Lindsey, Norman, OK", "center": "Lindsey Park Center", "lat": 35.203963, "lng": -97.459709},
  {"name": "First Fidelity Bank", "category": "bank", "address": "1337 W Lindsey, Norman, OK", "lat": 35.203961, "lng": -97.461157},
  {"name": "Arvest Bank", "category": "bank", "address": "1355 W Lindsey, Norman, OK", "lat": 35.203961, "lng": -97.461382},
  {"name": "OU Federal Credit Union", "category": "bank", "address": "2000 W Lindsey, Norman, OK", "lat": 35.203852, "lng": -97.471003},
  {"name": "Red River Credit Corporation", "category": "bank", "address": "2102 W Lindsey #B, Norman, OK", "center": "West Lindsey Center", "lat": 35.203847, "lng": -97.472519},
  {"name": "Regional Finance", "category": "bank", "address": "2108 W Lindsey #A, Norman, OK", "center": "West Lindsey Center", "lat": 35.203845, "lng": -97.473118},
  {"name": "CON Investigation Center", "category": "civic", "address": "1507 W Lindsey, Norman, OK", "lat": 35.203955, "lng": -97.46456},
  {"name": "Mine Safety and Health Administration", "category": "civic", "address": "2227 W Lindsey #1450, Norman, OK", "center": "Westoaks Office Park", "lat": 35.203962, "lng": -97.47469},
  {"name": "KISS Institute for Practical Robotics", "category": "education", "address": "1818 W Lindsey D180, Norman, OK", "center": "Lindsey Square", "phone": "(405) 579-4609", "email": "info@kipr.org", "website": "https://www.kipr.org/", "facebook": "https://www.facebook.com/BotballRobotics/", "instagram": "https://www.instagram.com/botballrobotics", "lat": 35.203858, "lng": -97.469525},
  {"name": "Happy Monk", "category": "fun", "address": "1430 W Lindsey, Norman, OK", "center": "Opies", "lat": 35.203843, "lng": -97.46393},
  {"name": "Oklahoma Tickets", "category": "fun", "address": "2215 W Lindsey #200, Norman, OK", "center": "Westoaks Office Park", "lat": 35.203961, "lng": -97.474574},
  {"name": "Starbucks", "category": "food", "address": "1200 W Lindsey, Norman, OK", "lat": 35.20385, "lng": -97.459047},
  {"name": "Taqueria La Chiva", "category": "food", "address": "1209 W Lindsey, Norman, OK", "lat": 35.203963, "lng": -97.459559},
  {"name": "Donut King", "category": "food", "address": "1214 W Lindsey, Norman, OK", "lat": 35.203849, "lng": -97.459522},
  {"name": "Subway", "category": "food", "address": "1222 W Lindsey, Norman, OK", "lat": 35.203848, "lng": -97.459649},
  {"name": "Legends", "category": "food", "address": "1313 W Lindsey, Norman, OK", "lat": 35.203961, "lng": -97.460858},
  {"name": "Legends Times Two", "category": "food", "address": "1333 W Lindsey, Norman, OK", "lat": 35.203961, "lng": -97.461107},
  {"name": "El Sombrero", "category": "food", "address": "1424 W Lindsey, Norman, OK", "lat": 35.203843, "lng": -97.463878},
  {"name": "Velvet Taco", "category": "food", "address": "1440 W Lindsey, Norman, OK", "featured": true, "lat": 35.203842, "lng": -97.464018},
  {"name": "Pizza Shuttle", "category": "food", "address": "1506 W Lindsey, Norman, OK", "lat": 35.203841, "lng": -97.464594},
  {"name": "Classic 50's Drive-In", "category": "food", "address": "1521 W Lindsey, Norman, OK", "featured": true, "lat": 35.203952, "lng": -97.465572},
  {"name": "Mr. Hui", "category": "food", "address": "1522 W Lindsey, Norman, OK", "lat": 35.20384, "lng": -97.464734},
  {"name": "McDonald's", "category": "food", "address": "1720 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203845, "lng": -97.467051},
  {"name": "Beanstalk Sno", "category": "food", "address": "1724 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203845, "lng": -97.467114},
  {"name": "Sonic", "category": "food", "address": "1730 W Lindsey, Norman, OK", "lat": 35.203846, "lng": -97.467318},
  {"name": "KFC", "category": "food", "address": "1801 W Lindsey, Norman, OK", "lat": 35.203964, "lng": -97.467855},
  {"name": "HTeaO", "category": "food", "address": "1807 W Lindsey, Norman, OK", "featured": true, "lat": 35.203968, "lng": -97.468535},
  {"name": "Teapioca", "category": "food", "address": "1808 W Lindsey #300, Norman, OK", "center": "Jackson Square", "lat": 35.203852, "lng": -97.468374},
  {"name": "Krave Teriyaki", "category": "food", "address": "1808 W Lindsey #400, Norman, OK", "center": "Jackson Square", "lat": 35.203852, "lng": -97.468374},
  {"name": "Eagle One Pizza", "category": "food", "address": "1951 W Lindsey, Norman, OK", "center": "Heritage Plaza", "lat": 35.203972, "lng": -97.469476},
  {"name": "Level 10 Nutrition", "category": "food", "address": "1959 W Lindsey, Norman, OK", "center": "Heritage Plaza", "lat": 35.203972, "lng": -97.469509},
  {"name": "Artisan's Pride Quality Meats", "category": "food", "address": "1965 W Lindsey, Norman, OK", "center": "Heritage Plaza", "lat": 35.203971, "lng": -97.469978},
  {"name": "Sabor Guanaco Salvadoreño Restaurant", "category": "food", "address": "2030 W Lindsey, Norman, OK", "lat": 35.203851, "lng": -97.471363},
  {"name": "The Fix Energy & Nutrition Lounge", "category": "food", "address": "2100 W Lindsey #104, Norman, OK", "center": "West Lindsey Center", "lat": 35.203847, "lng": -97.472319},
  {"name": "India Village", "category": "food", "address": "2110 W Lindsey, Norman, OK", "lat": 35.203845, "lng": -97.473258},
  {"name": "Lupita's Mexican Food", "category": "food", "address": "2108 W Lindsey #B, Norman, OK", "lat": 35.203845, "lng": -97.473118},
  {"name": "Taco Bell", "category": "food", "address": "2125 W Lindsey, Norman, OK", "lat": 35.203961, "lng": -97.474246},
  {"name": "Del Rancho", "category": "food", "address": "2300 W Lindsey, Norman, OK", "lat": 35.203848, "lng": -97.475388},
  {"name": "El Rincon Chapin", "category": "food", "address": "2305 W Lindsey #107, Norman, OK", "center": "Rahimi Plaza", "lat": 35.203962, "lng": -97.475571},
  {"name": "Corkscrew Wine & Spirits", "category": "food", "address": "2319 W Lindsey, Norman, OK", "featured": true, "lat": 35.203963, "lng": -97.475724},
  {"name": "Press & Plow", "category": "food", "address": "800 W Lindsey, Norman, OK", "featured": true, "lat": 35.2038, "lng": -97.451712},
  {"name": "Koda CrossFit", "category": "gym", "address": "1210 McGee, Norman, OK", "lat": 35.203722, "lng": -97.467856},
  {"name": "Fight or Flight Fitness", "category": "gym", "address": "1309 24th Ave SW, Norman, OK", "lat": 35.202641, "lng": -97.476587},
  {"name": "Downtown Fitness", "category": "gym", "address": "1610 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203841, "lng": -97.466358},
  {"name": "Vin's Styling", "category": "beauty", "address": "1300 McGee #130, Norman, OK", "center": "Hilltop", "lat": 35.202493, "lng": -97.467877},
  {"name": "Sooner Pharmacy", "category": "beauty", "address": "1811 W Lindsey, Norman, OK", "lat": 35.20397, "lng": -97.468903},
  {"name": "Nail Boutique", "category": "beauty", "address": "1932 W Lindsey #H, Norman, OK", "center": "Clarendon Park Shopping Center", "lat": 35.203856, "lng": -97.470192},
  {"name": "KEDPLASMA", "category": "beauty", "address": "2101 W Lindsey, Norman, OK", "lat": 35.203961, "lng": -97.474224},
  {"name": "Native Stylz Salon", "category": "beauty", "address": "1212 S Berry, Norman, OK", "lat": 35.203765, "lng": -97.459046},
  {"name": "The Mane Man", "category": "beauty", "address": "1215 W Lindsey, Norman, OK", "center": "Lindsey Park Center", "lat": 35.203963, "lng": -97.459634},
  {"name": "MM Salon Spa", "category": "beauty", "address": "1217 W Lindsey, Norman, OK", "center": "Lindsey Park Center", "lat": 35.203963, "lng": -97.459659},
  {"name": "Savvy Nails", "category": "beauty", "address": "1630 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203838, "lng": -97.465633},
  {"name": "Hair Co Salon", "category": "beauty", "address": "1632 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203838, "lng": -97.465665},
  {"name": "Integrative Health Center Massage & Spa", "category": "beauty", "address": "1634 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203838, "lng": -97.465696},
  {"name": "Karen Barbalace Aesthetics", "category": "beauty", "address": "1636 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203838, "lng": -97.465728},
  {"name": "Massage Therapy Norman", "category": "beauty", "address": "1300 McGee #100A, Norman, OK", "center": "Hilltop", "lat": 35.202493, "lng": -97.467877},
  {"name": "Fade N Up", "category": "beauty", "address": "1955 W Lindsey, Norman, OK", "center": "Heritage Plaza", "lat": 35.203972, "lng": -97.469492},
  {"name": "Lifetime Dental of Norman", "category": "beauty", "address": "2001 W Lindsey, Norman, OK", "lat": 35.203969, "lng": -97.47054},
  {"name": "Sooner Urgent Care", "category": "beauty", "address": "2100 W Lindsey #106, Norman, OK", "center": "West Lindsey Center", "lat": 35.203847, "lng": -97.472319},
  {"name": "Chinese Relax Massage", "category": "beauty", "address": "2305 W Lindsey #123, Norman, OK", "center": "Rahimi Plaza", "lat": 35.203962, "lng": -97.475571},
  {"name": "Skills for Living", "category": "beauty", "address": "1818 W Lindsey C248, Norman, OK", "center": "Lindsey Square", "phone": "405-360-5554", "website": "https://www.skillsforliving.net/", "lat": 35.203858, "lng": -97.469525},
  {"name": "Bright Start", "category": "service", "address": "1212 McGee, Norman, OK", "lat": 35.203697, "lng": -97.467856},
  {"name": "Julia's Dance Academy", "category": "service", "address": "1229 W Lindsey, Norman, OK", "center": "Lindsey Park Center", "lat": 35.203963, "lng": -97.459809},
  {"name": "Dale K. Graham Veterans Foundation", "category": "service", "address": "1233 W Lindsey, Norman, OK", "center": "Lindsey Park Center", "lat": 35.203963, "lng": -97.459859},
  {"name": "Lanoy Tag Agency", "category": "service", "address": "1315 24th Ave SW, Norman, OK", "lat": 35.201195, "lng": -97.476586},
  {"name": "All Around Tattoo", "category": "service", "address": "1430 W Lindsey #K, Norman, OK", "center": "Opies", "lat": 35.203843, "lng": -97.46393},
  {"name": "Star Kids", "category": "service", "address": "1600 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203837, "lng": -97.465539},
  {"name": "Titan Martial Arts", "category": "service", "address": "1704 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203843, "lng": -97.466799},
  {"name": "UpperCrust Food Service", "category": "service", "address": "1712 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203844, "lng": -97.466925},
  {"name": "Hollywood Coin Laundry", "category": "service", "address": "1746 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203847, "lng": -97.467411},
  {"name": "Dowell Properties", "category": "service", "address": "1932 W Lindsey #A, Norman, OK", "center": "Clarendon Park Shopping Center", "lat": 35.203856, "lng": -97.470192},
  {"name": "Enhanced Benefits Solutions", "category": "service", "address": "1932 W Lindsey #B, Norman, OK", "center": "Clarendon Park Shopping Center", "lat": 35.203856, "lng": -97.470192},
  {"name": "Farmers Insurance – Josh Jacks", "category": "service", "address": "1932 W Lindsey #C, Norman, OK", "center": "Clarendon Park Shopping Center", "lat": 35.203856, "lng": -97.470192},
  {"name": "In Home TV Repair", "category": "service", "address": "1932 W Lindsey #D, Norman, OK", "center": "Clarendon Park Shopping Center", "lat": 35.203856, "lng": -97.470192},
  {"name": "Lu's Alterations", "category": "service", "address": "1932 W Lindsey #E, Norman, OK", "center": "Clarendon Park Shopping Center", "lat": 35.203856, "lng": -97.470192},
  {"name": "Metro Brokers Connect Team", "category": "service", "address": "1932 W Lindsey #F, Norman, OK", "center": "Clarendon Park Shopping Center", "lat": 35.203856, "lng": -97.470192},
  {"name": "Shelter Insurance – JD Johnson", "category": "service", "address": "1932 W Lindsey #G, Norman, OK", "center": "Clarendon Park Shopping Center", "lat": 35.203856, "lng": -97.470192},
  {"name": "Precision Garage Door of Norman", "category": "service", "address": "2100 W Lindsey #100, Norman, OK", "center": "West Lindsey Center", "lat": 35.203847, "lng": -97.472319},
  {"name": "Boost Mobile", "category": "service", "address": "2100 W Lindsey #102, Norman, OK", "center": "West Lindsey Center", "lat": 35.203847, "lng": -97.472319},
  {"name": "Oklahoma's Finest Electric, Heating & Air", "category": "service", "address": "2215 W Lindsey #109, Norman, OK", "center": "Westoaks Office Park", "lat": 35.203961, "lng": -97.474574},
  {"name": "Sooner Traditions", "category": "service", "address": "2221 W Lindsey #201, Norman, OK", "center": "Westoaks Office Park", "lat": 35.203962, "lng": -97.474632},
  {"name": "Legal Aid Services of Oklahoma", "category": "service", "address": "2227 W Lindsey #1550, Norman, OK", "center": "Westoaks Office Park", "lat": 35.203962, "lng": -97.47469},
  {"name": "I-Drive", "category": "service", "address": "2233 W Lindsey #117, Norman, OK", "center": "Westoaks Office Park", "lat": 35.203962, "lng": -97.474749},
  {"name": "South Central CASA of Oklahoma", "category": "service", "address": "2241 W Lindsey #500, Norman, OK", "center": "Westoaks Office Park", "lat": 35.203962, "lng": -97.474826},
  {"name": "Cricket Wireless", "category": "service", "address": "2305 W Lindsey #111, Norman, OK", "center": "Rahimi Plaza", "lat": 35.203962, "lng": -97.475571},
  {"name": "Metro by T-Mobile", "category": "service", "address": "2305 W Lindsey #119, Norman, OK", "center": "Rahimi Plaza", "lat": 35.203962, "lng": -97.475571},
  {"name": "Virginia Henson, PLLC", "category": "service", "address": "1820 W Lindsey #100, Norman, OK", "center": "Lindsey Square", "lat": 35.203857, "lng": -97.469665},
  {"name": "DaVita Dialysis Center", "category": "service", "address": "1818 W Lindsey B104, Norman, OK", "center": "Lindsey Square", "lat": 35.203858, "lng": -97.469525},
  {"name": "Oklahoma Hypnosis Centers", "category": "service", "address": "1818 W Lindsey C120, Norman, OK", "center": "Lindsey Square", "phone": "(405) 956-5098", "email": "vicky@oklahomahypnosiscenters.com", "website": "https://www.oklahomahypnosiscenters.com/", "lat": 35.203858, "lng": -97.469525},
  {"name": "Susan Beyer, CPA", "category": "service", "address": "1818 W Lindsey C140, Norman, OK", "center": "Lindsey Square", "phone": "405-620-5396", "email": "susanbeyer@normantax.com", "website": "https://www.normantax.com/", "lat": 35.203858, "lng": -97.469525},
  {"name": "Peace Homecare", "category": "service", "address": "1818 W Lindsey C180, Norman, OK", "center": "Lindsey Square", "phone": "(405) 701-5951", "email": "info@peacehomecare.net", "website": "https://www.peacehomecare.net/", "facebook": "https://www.facebook.com/peacehomecareincok/", "instagram": "https://www.instagram.com/peacehome2020/", "lat": 35.203858, "lng": -97.469525},
  {"name": "Rietta Miller, Social Worker", "category": "service", "address": "1818 W Lindsey C210, Norman, OK", "center": "Lindsey Square", "phone": "(405) 831-6388", "lat": 35.203858, "lng": -97.469525},
  {"name": "United Energy Drilling", "category": "service", "address": "1818 W Lindsey C100, Norman, OK", "center": "Lindsey Square", "phone": "(405) 482-0080", "email": "lisa@ued-ok.com", "website": "https://unitedenergydrilling.com", "facebook": "https://facebook.com/UEDOK", "lat": 35.203858, "lng": -97.469525},
  {"name": "Homeland", "category": "shop", "address": "1724 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203845, "lng": -97.467114},
  {"name": "Dollar General", "category": "shop", "address": "1221 W Lindsey, Norman, OK", "lat": 35.203963, "lng": -97.459709},
  {"name": "Dollar Tree", "category": "shop", "address": "1614 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203843, "lng": -97.466686},
  {"name": "International Pantry", "category": "shop", "address": "1618 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203845, "lng": -97.467013},
  {"name": "Rainbow Cleaning Systems", "category": "shop", "address": "1622 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203842, "lng": -97.466449},
  {"name": "Mattress By Appointment", "category": "shop", "address": "1628 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203837, "lng": -97.465602},
  {"name": "Assist Wireless", "category": "shop", "address": "1744 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203847, "lng": -97.467399},
  {"name": "Salvation Army", "category": "shop", "address": "1742 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203846, "lng": -97.467388},
  {"name": "Heat4yaFeet", "category": "shop", "address": "1953 W Lindsey, Norman, OK", "center": "Heritage Plaza", "lat": 35.203972, "lng": -97.469484},
  {"name": "Christie's Toy Box", "category": "shop", "address": "2106 W Lindsey, Norman, OK", "center": "West Lindsey Center", "lat": 35.203846, "lng": -97.472918},
  {"name": "Christmas Expressions", "category": "shop", "address": "2214 W Lindsey, Norman, OK", "lat": 35.203847, "lng": -97.474519},
  {"name": "Meds and Wares", "category": "smoke", "address": "1404 W Lindsey, Norman, OK", "lat": 35.203845, "lng": -97.462531},
  {"name": "TNT Vapes", "category": "smoke", "address": "1225 W Lindsey, Norman, OK", "center": "Lindsey Park Center", "lat": 35.203963, "lng": -97.459759},
  {"name": "Lotus Botanicals CBD & Kratom", "category": "smoke", "address": "1714 W Lindsey, Norman, OK", "center": "Hollywood Shopping Center", "lat": 35.203844, "lng": -97.466957},
  {"name": "Vapor Lax", "category": "smoke", "address": "1808 W Lindsey #100, Norman, OK", "center": "Jackson Square", "lat": 35.203852, "lng": -97.468374},
  {"name": "Cronic Solutions", "category": "smoke", "address": "1808 W Lindsey #200, Norman, OK", "center": "Jackson Square", "lat": 35.203852, "lng": -97.468374},
  {"name": "Xclusive Cannabis", "category": "smoke", "address": "2102 W Lindsey #A, Norman, OK", "center": "West Lindsey Center", "lat": 35.203847, "lng": -97.472519},
  {"name": "How High", "category": "smoke", "address": "2118 W Lindsey, Norman, OK", "lat": 35.203846, "lng": -97.473942},
  {"name": "Bethel Baptist Church", "category": "worship", "address": "1717 W Lindsey, Norman, OK", "lat": 35.203958, "lng": -97.466703}
];

/* ---------------------------------------------------------
   District Deals — the email "unlock" incentive.
   ⚠️ Only publish REAL offers a business has approved. While this
   array is EMPTY, the site automatically shows a "deals dropping
   soon — subscribe to be first" state (still captures emails).
   Add offers to flip it back to the unlock/coupon experience:
     { business: "Velvet Taco", offer: "$2 off any entrée",
       details: "Dine-in, show phone", expires: "Sep 30" },
   --------------------------------------------------------- */
const DEALS = [];

/* Upcoming district events. While empty, the section shows an honest
   "follow us for events" state. Add real ones like this — include `date`
   (YYYY-MM-DD) and the event auto-hides the day after it passes:
     { "date": "2026-11-07", "month": "NOV", "day": "07",
       "title": "First Friday Sidewalk Stroll", "when": "Fri · 6–9pm",
       "desc": "Shops stay open late with live music and food trucks." }
*/
const EVENTS = [];

/* Map center + zoom (W Lindsey St corridor, Norman OK). */
const MAP_CONFIG = { center: [35.2045, -97.4655], zoom: 15 };
