    filepath = "/path/to/file.txt"
    new_string = "correct code"
    old_string = "incorrect code"

try:
    with open(filepath, 'r') as file:
        # Read the entire file into a string
        data = file.read()

    # Replace all occurrences of old_string with new_string
    data = data.replace(old_string, new_string)

    with open(filepath, 'w') as file:
        # Write the modified data back to the file
        file.write(data)

except FileNotFoundError:
    print(f"File '{filepath}' not found.")

    import subprocess

    try:
        # Run the dashboard command in a new terminal window
        subprocess.run(['powershell.exe', 'Start-Process', '-FilePath', 'C:\\Path\\To\\Dashboard.exe'], check=True, shell=True)

    except subprocess.CalledProcessError as e:
        print(f"Failed to run dashboard: {e}")

