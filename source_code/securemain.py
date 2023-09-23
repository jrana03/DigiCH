from tkinter import *
from tkinter.ttk import *
import sqlite3
from cryptography.fernet import Fernet

connection = sqlite3.connect("names.db")
#creating database table
connection.execute("create table if not exists names (ID text, ID2 text, name text, card_number text, expiry text, cvv text)")

def new_card():
    def save_names():
        if len(name.get()) != 0:
            general_label.configure(text="")
            cursor = connection.execute("""select name from names where name=?""", (name.get(),))
            result = cursor.fetchone()
            
            if result:
                duplicatecheck_label.config(text="ALREADY EXISTS")
            else:
                duplicatecheck_label.config(text="SAVED")

                #encrypting the card and cvv before being stored
                cardkey = Fernet.generate_key()
                cvvkey = Fernet.generate_key()

                card_fernet = Fernet(cardkey)
                cvv_fernet = Fernet(cvvkey)
                
                encCard = card_fernet.encrypt(card_number.get().encode())
                encCVV = cvv_fernet.encrypt(cvv.get().encode())

                mytuple = (cardkey, cvvkey, name.get(), encCard, expiry_date.get(), encCVV)

                #add to database
                connection.execute("insert into names values (?, ?, ?, ?, ?, ?)", mytuple)
                connection.commit()

                #name.configure(state=DISABLED)
                name.configure(state="readonly")
                card_number.configure(state="readonly")
                expiry_date.configure(state="readonly")
                cvv.configure(state="readonly")

                save_button.configure(state=DISABLED)
        else:
            general_label.configure(text="The name field is not filled out, please input something to save info.")
    
    #setting up window
    newWindow = Toplevel(root)
    newWindow.title("Save New Card")
    newWindow.geometry('400x200')

    #New Card Info Frame
    new_card_info = LabelFrame(newWindow, text="New Card Info")
    new_card_info.grid(row=0, sticky=W)

    #Setting up general label to check if required info is filled
    general_label=Label(newWindow, text="")
    general_label.grid(row=2, sticky=W)

    #Required info label
    required_label=Label(newWindow, text="*Fields with a star are required to be filled to save information.")
    required_label.grid(row=1, sticky=W)

    #First name & save button
    Label(new_card_info, text='*Name: ').grid(row=0, sticky=E)
    name = Entry(new_card_info)
    name.grid(row=0, column=1)
    save_button = Button(new_card_info, text = 'Save', command = save_names)
    save_button.grid(row=0, column=2)

    #Setting up duplicate check label for new card registration
    duplicatecheck_label=Label(new_card_info, text="")
    duplicatecheck_label.grid(row=1, column=2)

    #Card Number
    Label(new_card_info, text='Card Number: ').grid(row=1, sticky=E)
    card_number = Entry(new_card_info)
    card_number.grid(row=1, column=1)

    #Expiry Date
    Label(new_card_info, text='Expiry Date (mm/yy): ').grid(row=2, sticky=E)
    expiry_date = Entry(new_card_info)
    expiry_date.grid(row=2, column=1)

    #CVV
    Label(new_card_info, text='CVV: ').grid(row=3, sticky=E)
    cvv = Entry(new_card_info)
    cvv.grid(row=3, column=1)

def view_cards():
    newWindow = Toplevel(root)
    newWindow.title("View Saved Cards")
    newWindow.geometry('400x270')

    #creating dropdown menu frame
    choices_frame = LabelFrame(newWindow, text="Choice")
    choices_frame.grid(row=0, sticky=W)

    #General Label for Saved Cards to show search empty, or delete empty
    general_label=Label(newWindow, text="")
    general_label.grid(row=2, sticky=W)

    #creating dropdown menu with name values from database
    Label(choices_frame, text='Name').grid(row=0, column=0)
    saved_names = []
    cursor = connection.execute("select name, card_number, expiry, cvv from names")
    for row in cursor:
        saved_names.append(row[0])
    var = StringVar()
    cb = Combobox(choices_frame, textvariable=var)
    cb['values'] = saved_names
    cb['state']= 'readonly'
    cb.grid(row=1, column=0)

    #search for specific card
    def get_card():
        if len(var.get()) != 0:
            general_label.configure(text="")
            cursor.execute("select * from names where name=:c", {"c": str(var.get())})
            result = cursor.fetchall()
            for row in result:
                name.configure(state="normal")
                name.delete(0, END)
                name.insert(0, row[2])
                name.configure(state="readonly")

                card_number.configure(state="normal")
                card_number.delete(0, END)
                card_fernet = Fernet(row[0])
                decCard = card_fernet.decrypt(row[3]).decode()
                card_number.insert(0, decCard)
                card_number.configure(state="readonly")

                expiry_date.configure(state="normal")
                expiry_date.delete(0, END)
                expiry_date.insert(0, row[4])
                expiry_date.configure(state="readonly")

                cvv.configure(state="normal")
                cvv.delete(0, END)
                cvv_fernet = Fernet(row[1])
                decCVV = cvv_fernet.decrypt(row[5]).decode()
                cvv.insert(0, decCVV)
                cvv.configure(state="readonly")
        else:
            general_label.configure(text="Nothing is selected to search.")
    search_button = Button(choices_frame, text = 'Search', command=get_card)
    search_button.grid(row=1, column=1)

    #creating card details frame
    details_frame = LabelFrame(newWindow, text="Details")
    details_frame.grid(row=1, sticky=W)
    Label(details_frame, text='Name: ').grid(row=0, sticky=E)
    name = Entry(details_frame)
    name.grid(row=0, column=1)
    name.configure(state="readonly")

    #Card Number
    Label(details_frame, text='Card Number: ').grid(row=1, sticky=E)
    card_number = Entry(details_frame)
    card_number.grid(row=1, column=1)
    card_number.configure(state="readonly")

    #Expiry Date
    Label(details_frame, text='Expiry Date (mm/yy): ').grid(row=2, sticky=E)
    expiry_date = Entry(details_frame)
    expiry_date.grid(row=2, column=1)
    expiry_date.configure(state="readonly")

    #CVV
    Label(details_frame, text='CVV: ').grid(row=3, sticky=E)
    cvv = Entry(details_frame)
    cvv.grid(row=3, column=1)
    cvv.configure(state="readonly")

    #Confirmation window pop up & delete
    def confirm_window():
        if len(var.get()) != 0:
            general_label.configure(text="")
            #confirmation window
            confirm_window = Toplevel(newWindow)
            confirm_window.geometry("400x100")
            confirm_window.title("Confirm")
            confirm_label = Label(confirm_window, text="Are you sure you want to delete this card?")
            confirm_label.place(relx=0.5, rely=0.2, anchor=CENTER)

            def confirm_yes():
                connection.execute("delete from names where name=?", (str(var.get()), ))
                connection.commit()
                search_button.configure(state=DISABLED)
                delete_button.configure(state=DISABLED)
                cb.configure(state=DISABLED)
                deleted_label = Label(newWindow, text="Deleted. Please close the window to refresh.")
                deleted_label.place(relx=0.3, rely=0.7, anchor=CENTER)
            
            #confirmation choices
            yes_button = Button(confirm_window, text='Yes', command=lambda: [confirm_yes(), confirm_window.destroy()])
            yes_button.place(relx=0.4, rely=0.5, anchor=CENTER)
            no_button = Button(confirm_window, text='No', command=confirm_window.destroy)
            no_button.place(relx=0.6, rely=0.5, anchor=CENTER)
        else:
            general_label.configure(text="Nothing is selected to delete.")

    #Delete button
    delete_button = Button(choices_frame, text = 'Delete', command=confirm_window)
    delete_button.grid(row=1, column=2, sticky=E)


root = Tk()

root.geometry('500x100')
root.title('Digital Card Holder')

#new card registery
new_button = Button(root, text = 'New Card', command = new_card)
new_button.pack()

#view previously saved cards
view_button = Button(root, text = 'Saved Cards', command = view_cards)
view_button.pack()

root.mainloop()