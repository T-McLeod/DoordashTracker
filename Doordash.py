# import googlemaps
import tkinter as tk
# from time import strftime
from datetime import datetime  # , timedelta
import pandas as pd
import os
from dotenv import load_dotenv
import location
import uuid

# TODO Organize functions

load_dotenv()
key = os.getenv("API_KEY")


def getDist(x, y):
    return 120


def update_time(box):
    current_time = datetime.now()
    box.config(text=current_time.strftime("%H:%M:%S"))


def save_drive(root, df, id, labels):
    columns = df.columns.tolist()
    row = {}
    for i, col in enumerate(times[1:]):
        delta = datetime.strptime(labels[i+1].cget("text"), "%H:%M:%S") - datetime.strptime(labels[i].cget("text"), "%H:%M:%S")
        row[col] = delta.total_seconds()

    actualDF.loc[id] = row
    actualDF.to_csv('Data/actualTimes.csv', mode='a', header=False)
    root.destroy()


def newOrder(df, id):
    column_names = ['Order Accepted', 'Arrived at Store', 'Left Store', 'Arrived At Customer', 'Left Customer', 'Back in Zone/Order']
    root = tk.Toplevel()
    root.title(f"Order: ${id}")
    row = {}
    labels = []

    col = tk.Label(root, text=column_names[0], font=('calibri', 12, 'bold'))
    col.grid(row=0, column=0, padx=10)

    box = tk.Label(root, text=datetime.now().strftime("%H:%M:%S"), font=('calibri', 12), width=12,
                borderwidth=1, relief='solid')
    box.grid(row=1, column=0)
    labels.append(box)

    for idx, col_name in enumerate(column_names[1:]):
        col = tk.Label(root, text=col_name, font=('calibri', 12, 'bold'))
        col.grid(row=0, column=idx+1, padx=10)

        box = tk.Label(root, text="", font=('calibri', 12), width=12,
                       borderwidth=1, relief='solid')
        box.grid(row=1, column=idx+1)
        labels.append(box)

        update_button = tk.Button(root, text="Update",
                                  command=lambda box=box:
                                  update_time(box))

        update_button.grid(row=2, column=idx+1)

    save = tk.Button(root, text="Save",
                     command=lambda
                     root=root, df=df, labels=labels, id=id: save_drive(root, df, id, labels))
    save.grid(row=1, column=len(column_names) + 1)


def get_inputs():
    store_name = entries[0].get()
    address = entries[1].get()
    payout = entries[2].get()

    return store_name, address, payout


def show_rate():
    global currentOrder
    currentOrder = generateOrderID()
    id = currentOrder

    store_name, address, payout = get_inputs()
    row = {}
    row["Origin"] = location.getDeviceLocation()
    row['Store Location'] = location.searchPlace(row['Origin'], store_name)
    row["Customer Address"] = location.addressToLocation(address, row["Origin"])
    row['Payout'] = payout

    orderInfoDF.loc[id] = row
    # TODO customer address -> customer location
    finalTime, subTimes = location.routeRequest([row['Origin'], row['Store Location'], row['Customer Address']])

    rate = float(payout) / (finalTime / 3600)

    result_label.config(text=f"This order pays ${round(rate, 2)}/hour")

    # Update df entry
    row = {}
    row["Time to store"] = subTimes[0]
    row["Time at store"] = 120 # TODO add estimation for this
    row["Time to customer"] = subTimes[1]
    row["Time at customer"] = 60 # TODO add estimation for this
    row["Time to zone"] = 300 # TODO add estimation for this
    predictedDF.loc[id] = row

def accept():
    global currentOrder
    
    # Make sure variables are set for df
    if currentOrder in actualDF.index:
        print("Didn't submit new order")
        return

    # Set accepted
    orderInfoDF.loc[currentOrder, 'WasAccepted'] = True

    # Backup

    newOrder(actualDF, currentOrder)
    orderInfoDF.to_csv('Data/orderInfo.csv', mode='a', header=False)
    predictedDF.to_csv('Data/predictedTimes.csv', mode='a', header=False)
    clear_entries()


def generateOrderID():
    order_id = uuid.uuid4()
    return str(order_id)


def declineOrder():
    # Set decline
    orderInfoDF.loc[currentOrder, 'wasAccepted'] = False

    # Backup to df
    orderInfoDF.to_csv('Data/orderInfo.csv', mode='a', header=False)
    predictedDF.to_csv('Data/predictedTimes.csv', mode='a', header=False)

    # Reset text boxes
    clear_entries()
    return

def clear_entries():
    for entry in entries:
        entry.delete(0, tk.END)

root = tk.Tk()
root.title("Main Window")

# Create labels for column names
orderInfo = ['Order ID', 'Origin', 'Store Location', 'Customer Address',
             'Payout', 'wasAccepted']
times = ["Order ID", "Time to store", "Time at store", "Time to customer",
         "Time at customer", "Time to zone"]

orderInfoDF = pd.DataFrame(columns=orderInfo)
orderInfoDF = orderInfoDF.set_index('Order ID')
orderInfoDF['wasAccepted'] = orderInfoDF['wasAccepted'].astype(bool)
predictedDF = pd.DataFrame(columns=times).set_index('Order ID')
actualDF = pd.DataFrame(columns=times).set_index('Order ID')

currentOrder = None

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
decline = tk.Button(decision_buttons, text="Decline", command=declineOrder)
accept.pack(side=tk.LEFT)
decline.pack()


root.mainloop()
