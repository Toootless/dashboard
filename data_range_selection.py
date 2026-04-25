import tkinter as tk
from datetime import datetime

def create_data_range_selection():
    # Create a new button
    start_date = datetime(2022, 1, 1)
    end_date = datetime.now()
    label = tk.Label(root, text=f'Date Range: {start_date} - {end_date}')
    label.pack()

    # Get the current date and time
    now = datetime.now()

    # Create a new frame for date selection
    frame = tk.Frame(root)
    frame.pack()

    # Add start date entry field
    start_label = tk.Label(frame, text='Start Date:')
    start_label.pack(side=tk.LEFT)
    start_entry = tk.Entry(frame)
    start_entry.pack(side=tk.LEFT)

    # Add end date entry field
    end_label = tk.Label(frame, text='End Date:')
    end_label.pack(side=tk.LEFT)
    end_entry = tk.Entry(frame)
    end_entry.pack(side=tk.LEFT)

    # Create a new button to apply date range selection
    def apply_date_range():
        try:
            start_date = datetime.strptime(start_entry.get(), '%Y-%m-%d')
            end_date = datetime.strptime(end_entry.get(), '%Y-%m-%d')
            label['text'] = f'Date Range: {start_date.date()} - {end_date.date()}'
        except ValueError:
            label['text'] = 'Invalid date format (use YYYY-MM-DD)'
    apply_button = tk.Button(frame, text='Apply', command=apply_date_range)
    apply_button.pack(side=tk.LEFT)

root = tk.Tk()
create_data_range_selection()
root.mainloop()