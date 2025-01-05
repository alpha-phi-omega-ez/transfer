import csv
import sys
from datetime import datetime

from pymongo import MongoClient

laf_types = (
    ("Attire", "A"),
    ("Bags", "B"),
    ("Chargers & Cables", "C"),
    ("Electronics", "E"),
    ("Glasses", "G"),
    ("Headphones", "H"),
    ("Jewelery", "J"),
    ("Keys", "K"),
    ("Miscellaneous Items", "M"),
    ("Notepads, Papers, Books, Folders", "P"),
    ("Umbrellas", "U"),
    ("USB Devices", "F"),
    ("Wallets & Purses", "I"),
    ("Water Bottle", "W"),
)

laf_locations = (
    "87 Gym",
    "Academy Hall",
    "Alumni House",
    "Amos Eaton",
    "Blitman",
    "CBIS",
    "CII",
    "Carnegie Building",
    "Cogswell Laboratory",
    "Commons Dining Hall",
    "DCC",
    "EMPAC",
    "Folsom Library",
    "Freshman Hill",
    "Greene Building",
    "JEC",
    "JROWL",
    "Lally Hall",
    "MRC",
    "Mueller Center",
    "Pittsburgh Building",
    "Ricketts",
    "Sage Dining Hall",
    "Sage Labs",
    "Shuttles",
    "Troy Building",
    "Union",
    "VCC",
    "Walker Laboratory",
    "West Hall",
)

top_laf_num = 3720  # 3720 is the top number of LAFs in the database

location_mapping = {
    1: "Union",
    2: "Mueller Center",
    3: "Commons Dining Hall",
    4: "CII",
    5: "Sage Dining Hall",
    6: "DCC",
    7: "JROWL",
    8: "Academy Hall",
    9: "CBIS",
    10: "JEC",
    11: "Greene Building",
    12: "Lally Hall",
    13: "Carnegie Building",
    14: "Walker Laboratory",
    15: "Troy Building",
    16: "Sage Labs",
    17: "87 Gym",
    18: "Ricketts",
    19: "Folsom Library",
    20: "VCC",
    21: "Cogswell Laboratory",
    22: "MRC",
    23: "Pittsburgh Building",
    24: "West Hall",
    25: "Alumni House",
    26: "Blitman",
    27: "Amos Eaton",
    28: "EMPAC",
}

type_mapping = {
    1: "Attire",
    2: "Bags",
    3: "Chargers & Cables",
    4: "Miscellaneous Items",
    5: "Electronics",
    6: "USB Devices",
    7: "Glasses",
    8: "Wallets & Purses",
    9: "Jewelery",
    10: "Keys",
    11: "Miscellaneous Items",
    12: "Notepads, Papers, Books, Folders",
    13: "Umbrellas",
    14: "Water Bottle",
}


def main(db_stuff) -> None:

    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017")
    db = client["apo_main"]
    laf_items_collection = db["laf_items"]
    laf_id_collection = db["sequence_id"]
    laf_types_collection = db["laf_types"]
    laf_locations_collection = db["laf_locations"]
    lost_reports_collection = db["lost_reports"]

    laf_types_data = {}

    if db_stuff:

        # Set id number
        laf_id_collection.insert_one({"_id": "laf_id", "seq": top_laf_num})

        # Insert laf_types into laf_types_collection
        laf_types_collection.insert_many(
            [
                {
                    "type": laf_type[0],
                    "view": True,
                    "letter": laf_type[1],
                }
                for laf_type in laf_types
            ]
        )

        for new_type in laf_types_collection.find():
            laf_types_data[new_type["type"]] = new_type["_id"]

        # Insert laf_locations into laf_locations_collection
        laf_locations_collection.insert_many(
            [{"location": location} for location in laf_locations]
        )

    now = datetime.now()

    archived_laf = 0

    # Open the CSV file and read its contents
    with open("./data/lostAndFound/lafItem.csv", mode="r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Map CSV data to a dictionary
            description = row["description"].lower()
            if any(
                keyword in description
                for keyword in ["headphone", "airpod", "earbud", "air pod"]
            ):
                item_type = "Headphones"
            else:
                item_type = type_mapping[int(row["typeId"])]

            archived = bool(int(row["active"]))

            if archived:
                archived_laf += 1

            laf_item = {
                "_id": int(row["itemId"]),
                "description": row["description"],
                "date": row["foundTime"],
                "type_id": laf_types_data[item_type],
                "location": location_mapping[int(row["locationId"])],
                "created": row["foundTime"],
                "archived": archived,
                "found": False,
                "name": None,
                "email": None,
                "returned": None,
                "updated": now,
            }
            if db_stuff:
                # Insert the dictionary into the MongoDB collection
                laf_items_collection.insert_one(laf_item)

    print("Archived LAF Items: ", archived_laf)

    location_intermediate = {}

    with open("./data/lostAndFound/reportLocations.csv", mode="r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            location = location_mapping[int(row["locationId"])]
            if row["reportId"] not in location_intermediate:
                location_intermediate[row["reportId"]] = []
            location_intermediate[row["reportId"]].append(location)

    count = 0
    archived_reports = 0

    # Open the CSV file and read its contents
    with open("./data/lostAndFound/lostReport.csv", mode="r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Map CSV data to a dictionary
            description = row["description"].lower()
            if any(
                keyword in description
                for keyword in ["headphone", "airpod", "earbud", "air pod"]
            ):
                item_type = "Headphones"
            else:
                item_type = type_mapping[int(row["typeId"])]

            lost_time = datetime.strptime(row["lostTime"], "%Y-%m-%d")
            archived = (
                bool(int(row["active"])) if (now - lost_time).days <= 365 else True
            )

            if archived:
                archived_reports += 1

            try:
                location = location_intermediate[row["reportId"]]
            except KeyError:
                if (now - lost_time).days <= 365:
                    print(f"Location not found for: {row['reportId']}")
                count += 1
                location = ["Union"]

            lost_report_item = {
                "description": row["description"],
                "date": row["lostTime"],
                "type_id": laf_types_data[item_type],
                "location": location,
                "created": row["lostTime"],
                "archived": archived,
                "found": False,
                "name": row["firstName"] + " " + row["lastName"],
                "email": row["ownerEmail"],
                "updated": now,
            }

            if db_stuff:
                # Insert the dictionary into the MongoDB collection
                lost_reports_collection.insert_one(lost_report_item)

    print("Archived Lost Reports: ", archived_reports)

    print("Lost Reports within 1 year with no location: ", count)

    client.close()


if __name__ == "__main__":
    db_stuff = sys.argv[1].lower() == "true" if len(sys.argv) > 1 else False
    main(db_stuff)
