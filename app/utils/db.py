import json

"""
get_ticket_data function
opens tickets.json and returns the json object

update_ticket_data function
updates the json object and write the new object to the json file

Params:
ticket_data - the updated json object
"""


def get_ticket_data():
    with open("./db/tickets.json") as f:
        return json.load(f)


def update_ticket_data(ticket_data):
    with open("./db/tickets.json", "w") as f:
        json.dump(ticket_data, f, indent=4)
