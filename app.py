from flask import Flask, render_template, request
import boto3
import uuid
from datetime import datetime

app = Flask(__name__)

# -----------------------------
# AWS SERVICES
# -----------------------------

dynamodb = boto3.resource(
    "dynamodb",
    region_name="ap-south-1"
)

booking_table = dynamodb.Table("booking")

sns = boto3.client(
    "sns",
    region_name="ap-south-1"
)

TOPIC_ARN = "arn:aws:sns:ap-south-1:968077439442:busBooking"

# -----------------------------
# BUS DATA
# -----------------------------

buses = [

    {
        "name":"Express Travels",
        "number":"MH12AB1234",
        "source":"Mumbai",
        "destination":"Pune",
        "departure":"08:00 AM",
        "arrival":"11:30 AM",
        "seats":18,
        "fare":450
    },

    {
        "name":"Orange Travels",
        "number":"MH11AA2211",
        "source":"Pune",
        "destination":"Mumbai",
        "departure":"10:30 AM",
        "arrival":"02:00 PM",
        "seats":15,
        "fare":500
    },

    {
        "name":"Royal Bus",
        "number":"MH14XY5678",
        "source":"Mumbai",
        "destination":"Nashik",
        "departure":"09:30 AM",
        "arrival":"02:00 PM",
        "seats":22,
        "fare":650
    },

    {
        "name":"Shivneri",
        "number":"MH20SH1001",
        "source":"Pune",
        "destination":"Nashik",
        "departure":"07:00 AM",
        "arrival":"11:00 AM",
        "seats":30,
        "fare":400
    },

    {
        "name":"VRL Travels",
        "number":"MH09VR1111",
        "source":"Nagpur",
        "destination":"Mumbai",
        "departure":"09:00 PM",
        "arrival":"08:00 AM",
        "seats":20,
        "fare":1400
    },

    {
        "name":"SRS Travels",
        "number":"KA51SR1111",
        "source":"Nagpur",
        "destination":"Pune",
        "departure":"08:30 PM",
        "arrival":"06:00 AM",
        "seats":18,
        "fare":1100
    },

    {
        "name":"Mahendra Travels",
        "number":"MH18MA5555",
        "source":"Nashik",
        "destination":"Mumbai",
        "departure":"06:00 AM",
        "arrival":"10:00 AM",
        "seats":25,
        "fare":500
    },

    {
        "name":"Sai Travels",
        "number":"MH15SA1000",
        "source":"Nashik",
        "destination":"Pune",
        "departure":"04:00 PM",
        "arrival":"08:00 PM",
        "seats":17,
        "fare":450
    }

]

# -----------------------------
# HOME
# -----------------------------

@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# SEARCH
# -----------------------------

@app.route("/search", methods=["POST"])
def search():

    source = request.form.get("source","").strip().lower()
    destination = request.form.get("destination","").strip().lower()

    matched_buses = []

    for bus in buses:

        if (
            bus["source"].lower() == source
            and
            bus["destination"].lower() == destination
        ):

            matched_buses.append(bus)

    return render_template(
        "booking.html",
        buses=matched_buses
    )

# -----------------------------
# BOOK
# -----------------------------

@app.route("/book", methods=["POST"])
def book():

    passenger = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    seat = request.form.get("seat")
    busname = request.form.get("busname")

    user_id = str(uuid.uuid4())
    booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("===================================")
    print("New Booking Started")
    print("User ID :", user_id)
    print("Passenger :", passenger)
    print("Bus :", busname)
    print("Seat :", seat)

    # -----------------------------
    # Store in DynamoDB
    # -----------------------------

    booking_table.put_item(
        Item={
            "userId": user_id,
            "PassengerName": passenger,
            "Email": email,
            "Phone": phone,
            "BusName": busname,
            "Seat": seat,
            "BookingTime": booking_time,
            "Status": "Confirmed"
        }
    )

    print("Booking Stored Successfully In DynamoDB")

    # -----------------------------
    # SNS Notification
    # -----------------------------

    message = f"""
🚌 BUS BOOKING CONFIRMATION

Passenger : {passenger}

Bus : {busname}

Seat : {seat}

Phone : {phone}

Booking Time : {booking_time}

Status : Confirmed

Thank you for choosing our Bus Booking System.

Have a Safe Journey!
"""

    try:

        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject="Bus Booking Confirmation",
            Message=message
        )

        print("SNS Notification Sent Successfully")

    except Exception as e:

        print("SNS Error :", e)

    print("===================================")

    return render_template(
        "booking.html",
        buses=buses,
        success=True,
        passenger=passenger
    )

# -----------------------------
# VIEW ALL BOOKINGS
# -----------------------------

@app.route("/bookings")
def view_bookings():

    print("Fetching Bookings From DynamoDB...")

    response = booking_table.scan()

    bookings = response.get("Items", [])

    print("Total Bookings :", len(bookings))

    return render_template(
        "bookings.html",
        bookings=bookings
    )


# -----------------------------
# BOOKING DETAILS
# -----------------------------

@app.route("/booking/<user_id>")
def booking_details(user_id):

    response = booking_table.get_item(
        Key={
            "userId": user_id
        }
    )

    booking = response.get("Item")

    if not booking:

        return "Booking Not Found"

    return render_template(
        "booking_details.html",
        booking=booking
    )

# -----------------------------
# ERROR HANDLER
# -----------------------------

@app.errorhandler(404)
def page_not_found(error):

    return render_template("404.html"), 404


# -----------------------------
# HEALTH CHECK
# -----------------------------

@app.route("/health")
def health():

    return {
        "status": "Running",
        "service": "Bus Booking System",
        "database": "DynamoDB",
        "notification": "SNS"
    }


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":

    print("====================================")
    print("Bus Booking System Started")
    print("Database : DynamoDB")
    print("SNS : Connected")
    print("Running On : http://0.0.0.0:5000")
    print("====================================")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )