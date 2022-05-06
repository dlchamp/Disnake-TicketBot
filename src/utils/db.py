from json import dump, load


def get_ticket_data():
    '''get open tickets from json'''
    with open("./db/tickets.json") as f:
        return load(f)


def update_ticket_data(ticket_data):
    '''update the open tickets json data'''
    with open("./db/tickets.json", "w") as f:
        dump(ticket_data, f, indent=4)
