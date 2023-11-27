import json
from ClientData import ClientData
import os


class Database:

    DATABASE_PATH = "ClientDatabase.csv"

    def open_database(self):
        client_list = []
        if os.path.exists(self.DATABASE_PATH):
            with open(self.DATABASE_PATH, mode="r") as database:
                for client_json in database.readlines():
                    client = ClientData(**json.loads(client_json))
                    client_list.append(client)

        return client_list

    def add_client(self, client):
        with open(self.DATABASE_PATH, mode="a", newline="") as database:
            database.write(json.dumps(client.__dict__) + "\n")

    # NEEDED:
    # def remove_client
    # def update_client
    # def publish_files

    def delete_database(self):
        if os.path.exists(self.DATABASE_PATH):
            os.remove(self.DATABASE_PATH)