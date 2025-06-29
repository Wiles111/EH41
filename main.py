import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
import json
from business import BeautyBusiness
from client import Client
from service import Service

# --- Initialize Business ---
business = BeautyBusiness("Glow Beauty Studio")
business.add_service(Service("Eyebrow Tattoo", 250, 90, "Brows"))
business.add_service(Service("Lip Filler", 400, 60, "Lips"))
business.add_service(Service("Eyelash Extensions", 120, 75, "Lashes"))

# --- GUI Setup ---
root = tk.Tk()
root.title("Admin Appointment Manager")
root.geometry("420x800")

# --- Placeholder Helper ---
def add_placeholder(entry, text):
    entry.insert(0, text)
    entry.config(fg='gray')

    def on_focus_in(event):
        if entry.get() == text:
            entry.delete(0, tk.END)
            entry.config(fg='black')

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, text)
            entry.config(fg='gray')

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

# --- Client Form ---
tk.Label(root, text="Add Client", font=('Helvetica', 14)).pack(pady=5)
entry_name = tk.Entry(root, width=30)
entry_name.pack()
add_placeholder(entry_name, "Name")

entry_phone = tk.Entry(root, width=30)
entry_phone.pack()
add_placeholder(entry_phone, "Phone")

entry_email = tk.Entry(root, width=30)
entry_email.pack()
add_placeholder(entry_email, "Email")

def add_client():
    name, phone, email = entry_name.get(), entry_phone.get(), entry_email.get()
    if name not in ["", "Name"] and phone not in ["", "Phone"]:
        business.add_client(Client(name, phone, email))
        messagebox.showinfo("Success", f"Client '{name}' added.")
        for e, text in zip([entry_name, entry_phone, entry_email], ["Name", "Phone", "Email"]):
            e.delete(0, tk.END)
            add_placeholder(e, text)
    else:
        messagebox.showerror("Error", "Name and phone are required.")

tk.Button(root, text="Add Client", command=add_client).pack(pady=5)

# --- Book Appointment ---
tk.Label(root, text="Book Appointment", font=('Helvetica', 14)).pack(pady=10)
entry_client = tk.Entry(root, width=30)
entry_client.pack()
add_placeholder(entry_client, "Client Name")

entry_service = tk.Entry(root, width=30)
entry_service.pack()
add_placeholder(entry_service, "Service Name")

tk.Label(root, text="Select Date").pack()
calendar = DateEntry(root, width=27, date_pattern='yyyy-mm-dd')
calendar.pack()

tk.Label(root, text="Select Time").pack()
frame_time = tk.Frame(root)
frame_time.pack()

hour_var = tk.StringVar(value="12")
minute_var = tk.StringVar(value="00")
spin_hour = tk.Spinbox(frame_time, from_=0, to=23, textvariable=hour_var, width=5, format="%02.0f")
spin_minute = tk.Spinbox(frame_time, from_=0, to=59, textvariable=minute_var, width=5, format="%02.0f")
spin_hour.pack(side=tk.LEFT)
tk.Label(frame_time, text=":").pack(side=tk.LEFT)
spin_minute.pack(side=tk.LEFT)

def book_appointment():
    client_name = entry_client.get()
    service_name = entry_service.get()
    dt_str = f"{calendar.get()} {hour_var.get()}:{minute_var.get()}"
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        business.book_appointment(client_name, service_name, dt)
        update_appointment_list()
        messagebox.showinfo("Success", "Appointment booked.")
    except ValueError:
        messagebox.showerror("Error", "Invalid date/time format.")

tk.Button(root, text="Book Appointment", command=book_appointment).pack(pady=5)

# --- Appointment List ---
tk.Label(root, text="Appointments", font=('Helvetica', 14)).pack(pady=10)
frame_appt = tk.Frame(root)
frame_appt.pack()
scrollbar_appt = tk.Scrollbar(frame_appt)
scrollbar_appt.pack(side=tk.RIGHT, fill=tk.Y)
listbox_appts = tk.Listbox(frame_appt, width=50, height=6, yscrollcommand=scrollbar_appt.set)
listbox_appts.pack()
scrollbar_appt.config(command=listbox_appts.yview)

def update_appointment_list():
    listbox_appts.delete(0, tk.END)
    for appt in business.appointments:
        display = f"{appt.datetime.strftime('%Y-%m-%d %H:%M')} - {appt.client.name} - {appt.service.name}"
        listbox_appts.insert(tk.END, display)

update_appointment_list()

def delete_appointment():
    selected = listbox_appts.curselection()
    if not selected:
        messagebox.showerror("Error", "No appointment selected.")
        return
    index = selected[0]
    appt = business.appointments.pop(index)
    appt.client.history.remove(appt)
    update_appointment_list()
    messagebox.showinfo("Deleted", "Appointment deleted.")

def edit_appointment():
    selected = listbox_appts.curselection()
    if not selected:
        messagebox.showerror("Error", "No appointment selected.")
        return
    index = selected[0]
    appt = business.appointments[index]
    new_dt_str = f"{calendar.get()} {hour_var.get()}:{minute_var.get()}"
    try:
        new_dt = datetime.strptime(new_dt_str, "%Y-%m-%d %H:%M")
        appt.datetime = new_dt
        update_appointment_list()
        messagebox.showinfo("Updated", "Appointment time updated.")
    except ValueError:
        messagebox.showerror("Error", "Invalid new date/time format.")

tk.Button(root, text="Delete Appointment", command=delete_appointment).pack(pady=2)
tk.Button(root, text="Edit Appointment Time", command=edit_appointment).pack(pady=2)

# --- Load Client Requests ---
tk.Label(root, text="Pending Requests", font=('Helvetica', 14)).pack(pady=10)
frame_req = tk.Frame(root)
frame_req.pack()
scrollbar_req = tk.Scrollbar(frame_req)
scrollbar_req.pack(side=tk.RIGHT, fill=tk.Y)
listbox_requests = tk.Listbox(frame_req, width=50, height=6, yscrollcommand=scrollbar_req.set)
listbox_requests.pack()
scrollbar_req.config(command=listbox_requests.yview)

def load_client_requests():
    listbox_requests.delete(0, tk.END)
    try:
        with open("client_requests.json", "r") as f:
            data = json.load(f)
        for req in data:
            listbox_requests.insert(tk.END, f"{req['datetime']} - {req['name']} - {req['service']}")
    except FileNotFoundError:
        messagebox.showinfo("No Requests", "No client requests found.")

def approve_request():
    selection = listbox_requests.curselection()
    if not selection:
        messagebox.showerror("Error", "No request selected.")
        return

    index = selection[0]
    with open("client_requests.json", "r") as f:
        data = json.load(f)
    request = data.pop(index)

    client = business.find_client(request["name"])
    if not client:
        client = Client(request["name"], request["phone"], request["email"])
        business.add_client(client)

    dt = datetime.strptime(request["datetime"], "%Y-%m-%d %H:%M")
    business.book_appointment(client.name, request["service"], dt)

    with open("client_requests.json", "w") as f:
        json.dump(data, f, indent=4)

    update_appointment_list()
    load_client_requests()
    messagebox.showinfo("Success", "Request approved and booked.")

tk.Button(root, text="Load Requests", command=load_client_requests).pack(pady=3)
tk.Button(root, text="Approve & Book Selected", command=approve_request).pack(pady=3)

root.mainloop()
