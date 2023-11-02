import googlemaps
import tkinter as tk
# from time import strftime
from datetime import datetime  # , timedelta
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("API_KEY")
gmaps = googlemaps.Client(key)

"""def getDist(origin, dest):
    result = gmaps.distance_matrix(origin, dest)

    if result:
        return result['rows'][0]['elements'][0]['duration']['value']
    else:
        print("no work")
        return -1"""


def getDist(x, y):
    return 120


def update_time(timeStamps, idx, box):
    current_time = datetime.now()
    timeStamps[idx] = current_time
    box.config(text=current_time.strftime("%H:%M:%S"))


def save_drive(root, row, timeStamps):
    times = ["order ID", "Time to store", "Time at store", "Time to customer"
             "Time at customer", "Time to zone"]
    # last = datetime.strptime(times[0], '%Y-%m-%d %H:%M:%S')
    for i, col in enumerate(times[1:]):
        delta = timeStamps[i+1] - timeStamps[i]
        row[col] = delta.total_seconds()

    actualDF.loc[len(actualDF.index)] = row
    actualDF.to_csv("data.csv", index=False)
    root.destroy()


def newOrder(row):
    column_names = [col for col, value in row.items()]
    root = tk.Toplevel()
    root.title("Time Table App")
    timeStamps = [None]*(1 + len(column_names))
    timeStamps[0] = datetime.now()

    for idx, col_name in enumerate(times[1:]):
        col = tk.Label(root, text=col_name, font=('calibri', 12, 'bold'))
        col.grid(row=0, column=idx+1, padx=10)

        box = tk.Label(root, text="", font=('calibri', 12), width=12,
                       borderwidth=1, relief='solid')
        box.grid(row=1, column=idx+1)

        update_button = tk.Button(root, text="Update",
                                  command=lambda t=timeStamps, i=idx, box=box:
                                  update_time(t, i + 1, box))

        update_button.grid(row=2, column=idx+1)

    save = tk.Button(root, text="Save",
                     command=lambda
                     row=row, t=timeStamps: save_drive(root, row, t))
    save.grid(row=1, column=len(column_names) + 1)


def get_inputs():
    store_name = entries[0].get()
    address = entries[1].get()
    payout = entries[2].get()

    return store_name, address, payout


def show_rate():
    store_name, address, payout = get_inputs()
    row = pd.Series({col: None for col in orderInfoDF.columns})
    row['Order ID'] = generateOrderID()
    row["Origin"] = getOrigin()
    row['Store Location'] = ""  # get store
    row["Customer Address"] = address
    row['Payout'] = payout

    rate = float(payout) / (float(calculate_time(row)) / 3600)

    result_label.config(text=f"This order pays ${rate}/hour")


def calculate_time(row):  # untested
    # Get values
    storeLocation = row['Store Location']
    customer = row['Customer Address']

    #  Get store = ??
    #  gmaps.getPlacesNearby
    storeLocation = {'lat': 35.9424814, 'lng': -78.9072968}

    # calculate eta for trip
    pickup_drive = getDist(row['origin'], storeLocation)
    pickup_store = 120

    dropoff_drive = getDist(storeLocation, customer)
    dropoff_time = 60

    downtime = 300

    row = pd.Series({col: None for col in predictedDF.columns})

    row["Time to store"] = pickup_drive
    row["Time at store"] = pickup_store
    row["Time to customer"] = dropoff_drive
    row["Time at customer"] = dropoff_time
    row["Time to zone"] = downtime

    return (pickup_drive + pickup_store + dropoff_drive + dropoff_time +
            downtime)


def accept():
    # Make sure variables are set for df
    rowInfo = orderInfoDF.loc[len(actualDF.index) - 1]
    if rowInfo["order ID"] == actualDF.loc[len(actualDF.index) - 1]["order ID"]:
        print("Didn't submit new order")

    row = pd.Series({col: None for col in actualDF.columns})

    row['order ID'] = rowInfo["order ID"]

    # Set accepted
    rowInfo['Accepted'] = True

    # Backup

    newOrder(row)
    return


def generateOrderID():  # TODO Pattern for generating OrderID
    return 420


def declineOrder():  # TODO finish
    rowInfo = orderInfoDF.loc[len(actualDF.index) - 1]
    # Set decline
    rowInfo['Accepted'] = False

    # Backup to df

    # Reset text boxes
    return


def getOrigin():
    return


root = tk.Tk()
root.title("Main Window")

# Create labels for column names
orderInfo = ['Order ID', 'Origin', 'Store Location', 'Customer Address',
             'Accepted', 'Payout', 'wasAccepted']
times = ["order ID", "Time to store", "Time at store", "Time to customer"
         "Time at customer", "Time to zone"]

orderInfoDF = pd.DataFrame(columns=orderInfo)
predictedDF = pd.DataFrame(columns=times)
actualDF = pd.DataFrame(columns=times)

storeLocation = {}

# Main window
input_frame = tk.Frame(root)
input_frame.pack()

# Create labels and entry widgets for each input,
# and pack them side by side inside the frame
labels = ['Store', 'Customer Address', 'Payout']
entries = []

for label_text in labels:
    label = tk.Label(input_frame, text=label_text)
    label.pack(side=tk.LEFT, padx=5)  # Pack labels to the left

    entry = tk.Entry(input_frame)
    entry.pack(side=tk.LEFT, padx=5)  # Pack entry widgets to the left
    entries.append(entry)

# Create a button to submit the inputs
submit_button = tk.Button(input_frame, text="Submit", command=show_rate)
submit_button.pack(side=tk.LEFT)

# Create a label to display the input values
result_label = tk.Label(root, text="", padx=5, pady=10)
result_label.pack()

decision_buttons = tk.Frame(root)
decision_buttons.pack()

accept = tk.Button(decision_buttons, text="Accept", command=accept)
decline = tk.Button(decision_buttons, text="Decline", command=accept)
accept.pack(side=tk.LEFT)
decline.pack()


root.mainloop()
