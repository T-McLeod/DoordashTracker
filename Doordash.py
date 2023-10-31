import googlemaps
import tkinter as tk
from time import strftime
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("API_KEY")
print(key)
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


def update_time(arr):
    row, box, col = arr
    current_time = strftime('%H:%M:%S')
    row[col] = current_time
    box.config(text=current_time)


def save_drive(root, row):
    df.loc[len(df.index)] = row
    df.to_csv("data.csv", index=False)
    root.destroy()


def newOrder(df, column_names):
    root = tk.Toplevel()
    root.title("Time Table App")
    row = pd.Series({col: None for col in df.columns}) # Pull from last row instead of new row

    for idx, col_name in enumerate(column_names):
        col = tk.Label(root, text=col_name, font=('calibri', 12, 'bold'))
        col.grid(row=0, column=idx+1, padx=10)

        box = tk.Label(root, text="", font=('calibri', 12), width=12, borderwidth=1, relief='solid')
        box.grid(row=1, column=idx+1)

        update_button = tk.Button(root, text="Update", command=lambda b=[row, box, col_name]: update_time(b))
        update_button.grid(row=2, column=idx+1)

    save = tk.Button(root, text="Save", command=lambda row=row: save_drive(root, row))
    save.grid(row=1, column=len(column_names) + 1)


def get_inputs():
    store_name = entries[0].get()
    address = entries[1].get()
    payout = entries[2].get()

    return store_name, address, payout


def show_rate():
    store_name, address, payout = get_inputs()

    rate = float(payout) / (float(calculate_time()) / 3600)

    result_label.config(text=f"This order pays ${rate}/hour")


def calculate_time():  #untested
    # Get values
    store, customer, payout = get_inputs()

        # Get origin = TBD
    origin = "107 Ashton Drive, 28115 Mooresville North Carolina"
        # Get store = ??
        # gmaps.getPlacesNearby
    storeLocation = {'lat': 35.9424814, 'lng': -78.9072968}

    # calculate eta for trip
        
    pickup_drive = getDist(origin, storeLocation)
    pickup_store = 120
        
    dropoff_drive = getDist(storeLocation, customer)
    dropoff_time = 60

    downtime = 300

    total = pickup_drive + pickup_store + dropoff_drive + dropoff_time + downtime
    times[0] = pickup_drive
    times[1] = pickup_store
    times[2] = dropoff_drive
    times[3] = dropoff_time
    times[4] = downtime
    timesUpdated = True
        
    
    # Set all variables for df

    return total


def accept():
    # Make sure variables are set for df
    row = pd.Series({col: None for col in df.columns})
    print(timesUpdated)
    
    if(not timesUpdated): #Fix this
        calculate_time()

    row['order ID'] = 1 # Change
    row['origin'] = "here" # Change
    row['store location'] = storeLocation
    row['Customer Address'] = entries[1].get()
    row['Payout'] = entries[2].get()

    time = datetime.now()
    row['Time accepeted'] = time

    keys = ["Est to Store", "Est leave store", "Est arrived customer", "Est dropped food", "Est back to zone"]
    for i in range(len(keys)):
        time = time + timedelta(seconds=times[i])
        row[keys[i]] = time
    
    # Set accepted
    row['Accepted'] = True
    print(row)

    # Backup?
    df.loc[len(df)] = row

    # New order
    newOrder(df, column_names)
    return


def decline():
    # Set decline

    # Backup to df

    # Reset text boxes
    return


def reset():
    storeLocation = False
    timesUpdated = False


    
root = tk.Tk()
root.title("Main Window")

# Create labels for column names
meta = ['order ID', 'origin', 'store location', 'Customer Address', 'Accepted', 'Payout', 'Time accepeted', "Est to Store", "Est leave store","Est arrived customer", "Est dropped food", "Est back to zone"]
column_names = ["Arrived at Store", "Left from store", "Dropped food", "Back to zone"]
df = pd.DataFrame(columns=(meta + column_names))

timesUpdated = False
times = [0]*5

storeLocation = {}
timesUpdated = False

# Main window
input_frame = tk.Frame(root)
input_frame.pack()

# Create labels and entry widgets for each input, and pack them side by side inside the frame
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
