from flask import Flask, request, json
import os
import csv
import math

app = Flask(__name__)


def file_exist_check():
    if os.path.exists("data/user_data.csv"):
        return 1
    else:
        return 0


def get_all_users():
    csvfile = open("data/user_data.csv", "r")
    reader = csv.DictReader(csvfile, delimiter=",", quotechar=",")

    users = []

    for row in reader:
        users.append(row)

    csvfile.close()
    return users


def fetch_last_user_id():
    csvfile = open("data/user_data.csv", "r")
    reader = csv.DictReader(csvfile, delimiter=",", quotechar=",")

    last_user_id = 0

    for row in reader:
        last_user_id = int(row["id"])

    csvfile.close()
    return last_user_id


def create_user_entry(name, email, mobile, age):
    fieldnames = ["id", "name", "email", "mobile", "age"]

    if file_exist_check():
        csvfile = open("data/user_data.csv", "a")
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    else:
        csvfile = open("data/user_data.csv", "w")
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    last_user_id = fetch_last_user_id()

    writer.writerow({"id": last_user_id + 1, "name": name, "email": email, "mobile": mobile, "age": age})

    csvfile.close()


def fetch_user(id):
    csvfile = open("data/user_data.csv", "r")
    reader = csv.DictReader(csvfile, delimiter=",", quotechar=",")

    for row in reader:
        if int(row["id"]) == id:
            csvfile.close()
            return row

    csvfile.close()
    return None


def fetch_paged_users(start, end):
    csvfile = open("data/user_data.csv", "r")
    reader = csv.DictReader(csvfile, delimiter=",", quotechar=",")

    line_count = 0
    paged_users = []

    for row in reader:
        if line_count > end:
            break
        elif line_count >= start:
            paged_users.append(row)

        line_count += 1

    csvfile.close()
    return paged_users


def edit_user_id(id, name, email, mobile, age):
    csvfile = open("data/user_data.csv", "r")
    reader = csv.DictReader(csvfile, delimiter=",", quotechar=",")

    file = []

    for row in reader:
        file.append(row)

    csvfile.close()

    new_file = []

    for user in file:
        if int(user["id"]) == id:
            user["name"] = name
            user["email"] = email
            user["mobile"] = mobile
            user["age"] = age
            new_file.append(user)
        else:
            new_file.append(user)

    csvfile = open("data/user_data.csv", "w")
    fieldnames = ["id", "name", "email", "mobile", "age"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for user in new_file:
        writer.writerow(user)

    csvfile.close()


def delete_user_id(id):
    csvfile = open("data/user_data.csv", "r")
    reader = csv.DictReader(csvfile, delimiter=",", quotechar=",")

    file = []

    for row in reader:
        file.append(row)

    csvfile.close()

    new_file = []

    for user in file:
        if not int(user["id"]) == id:
            new_file.append(user)

    csvfile = open("data/user_data.csv", "w")
    fieldnames = ["id", "name", "email", "mobile", "age"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for user in new_file:
        writer.writerow(user)

    csvfile.close()


@app.route("/list/all", methods=["GET"])
def list_users():
    page_no = request.args.get('page_no', default=1, type=int)
    results_per_page = request.args.get('results_per_page', default=5, type=int)

    if file_exist_check():
        users = get_all_users()
        total_users = len(users)
        total_pages = math.ceil(float(total_users) / results_per_page)

        start_index = ((page_no * results_per_page) - results_per_page)
        end_index = start_index + results_per_page - 1

        if end_index > total_users:
            end_index = total_users

        paged_users = fetch_paged_users(start_index, end_index)

        return json.dumps({"status": 200, "message": "success", "data": paged_users, "total_pages": total_pages})
    else:
        return json.dumps({"status": 400, "message": "user_data.csv does not exist"})


@app.route("/create/user", methods=["POST"])
def create_user():
    name = request.json["name"]
    email = request.json["email"]
    mobile = request.json["mobile"]
    age = request.json["age"]

    if name == "":
        return json.dumps({"status": 400, "message": "Name missing"})
    elif email == "":
        return json.dumps({"status": 400, "message": "Email missing"})
    elif len(mobile) < 10 or len(mobile) > 10:
        return json.dumps({"status": 400, "message": "Mobile number should be of 10 digits"})
    elif age <= 0:
        return json.dumps({"status": 400, "message": "Age cannot be less than or equal to 0"})
    else:
        create_user_entry(name, email, mobile, age)
        return json.dumps({"status": 200, "message": "User added"})


@app.route("/show/user/<id>", methods=["GET"])
def show_user(id):
    id = int(id)

    if id <= 0:
        return json.dumps({"status": 400, "message": "ID cannot be less than or equal to 0"})
    else:
        user = fetch_user(id)
        if user is None:
            return json.dumps({"status": 400, "message": "User not found"})
        else:
            return json.dumps({"status": 200, "message": "success", "data": user})


@app.route("/edit/user/<id>", methods=["PATCH"])
def edit_user(id):
    id = int(id)

    name = request.json["name"]
    email = request.json["email"]
    mobile = request.json["mobile"]
    age = request.json["age"]

    if name == "":
        return json.dumps({"status": 400, "message": "Name missing"})
    elif email == "":
        return json.dumps({"status": 400, "message": "Email missing"})
    elif len(mobile) < 10 or len(mobile) > 10:
        return json.dumps({"status": 400, "message": "Mobile number should be of 10 digits"})
    elif age <= 0:
        return json.dumps({"status": 400, "message": "Age cannot be less than or equal to 0"})
    elif id <= 0:
        return json.dumps({"status": 400, "message": "ID cannot be less than or equal to 0"})
    else:
        user = fetch_user(id)
        if user is None:
            return json.dumps({"status": 400, "message": "User not found"})
        else:
            edit_user_id(id, name, email, mobile, age)
            return json.dumps({"status": 200, "message": "User edited successfully"})


@app.route("/delete/user/<id>", methods=["DELETE"])
def delete_user(id):
    id = int(id)

    if id <= 0:
        return json.dumps({"status": 400, "message": "ID cannot be less than or equal to 0"})
    else:
        user = fetch_user(id)
        if user is None:
            return json.dumps({"status": 400, "message": "User not found"})
        else:
            delete_user_id(id)
            return json.dumps({"status": 200, "message": "User deleted successfully"})


@app.after_request
def add_header(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization ')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE')

    return response
