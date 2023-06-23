import requests

if __name__ == "__main__":
    token = input("Enter token: ")
    res = requests.get(f"http://api.sms-man.com/control/countries?token={token}")

    countries = res.json()
    if "error_msg" in countries:
        print(f"Error: {res.json()['error_msg']}")
        exit(1)

    country = input("Enter country (must be an exact match): ")
    for key, value in countries.items():
        if country.lower() == value["title"].lower():
            print(f"Country: {value['title']}")
            print(f"Country ID: {value['id']}")
            exit(0)

    print("Country not found.")
