Installation Guide – Habit Tracker App
This guide explains how to install and run the Habit Tracker project step-by-step, even if you have never programmed before.

1. Download the Project
1.	Open the GitHub repository link: https://github.com/markushu05/habit_tracker
2.	Click the green “Code” button.
3.	Choose “Download ZIP” and save it on your computer.
4.	Right-click the ZIP file → “Extract All…”
→ You’ll now have a folder named habit_tracker.

 2. Install Visual Studio Code
1.	Go to https://code.visualstudio.com/
2.	Click Download for Windows (or macOS/Linux).
3.	Install VS Code using the default settings.
4.	When finished, start VS Code.

 3. Install Python Extension in VS Code
1.	In VS Code, open the Extensions view (left-hand icon bar or Ctrl+Shift+X).
2.	Search for “Python”.
3.	Click Install on the extension by Microsoft.
This extension automatically installs and configures Python for you.

4. Open the Project
1.	In VS Code, click File → Open Folder…
2.	Select the extracted habit_tracker folder.
3.	When prompted, click “Yes, I trust the authors.”
 
5. Create and Activate the Virtual Environment
1.	Open the Terminal in VS Code:
View → Terminal
2.	Type and run: python -m venv venv
When active, you’ll see (venv) before your terminal prompt.

6. Install Required Packages
Now install all project dependencies by running: pip install -r requirements.txt
This automatically installs everything your project needs (Flask, SQLite, etc.).

7. Start the Habit Tracker App
Run the following command:
python app.py
You’ll see: Running on http://127.0.0.1:5000

8. Open in Your Browser
1.	Open your web browser.
2.	Enter the address shown in the terminal (usually http://127.0.0.1:5000).
3.	The Habit Tracker App will open and is ready to use 

