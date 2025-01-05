import csv
from pymongo import MongoClient


def read_loanertech_csv(file_path) -> dict[str, list[int]]:
    loanertech_dict = {}
    with open(file_path, mode="r") as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            key = row[0]
            values = [
                int(value[1:]) for value in row[1:] if value
            ]  # Filter out empty strings
            loanertech_dict[key] = values
    return loanertech_dict


def push_to_mongo(loanertech_data) -> None:
    client = MongoClient("mongodb://localhost:27017")
    db = client["apo_main"]
    loanertech_collection = db["loanertech_collection"]
    id_collection = db["sequence_id"]

    largest_id = 0

    for key, values in loanertech_data.items():
        largest_id = max(largest_id, max(values))
        loanertech_collection.insert_many(
            [
                {
                    "_id": value,
                    "in_office": True,
                    "phone": "",
                    "email": "",
                    "name": "",
                    "description": key,
                }
                for value in values
            ]
        )

    id_collection.insert_one({"_id": "loanertech_id", "seq": largest_id})


def main() -> None:
    file_path = "data/loanertech/loanertech.csv"
    loanertech_data = read_loanertech_csv(file_path)
    print(loanertech_data)
    push_to_mongo(loanertech_data)


if __name__ == "__main__":
    main()
