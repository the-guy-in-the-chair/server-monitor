# when ready to ship, run "pip3 freeze > requirements.txt" and it will
# pipe all of your requirements into the file

# GENERAL IMPORTS
from dotenv import load_dotenv
import os
import time

# FLASK IMPORTS
from flask import Flask, render_template, jsonify, request
import subprocess

# SMS SYSTEM IMPORTS
import threading
import smtplib
from email.message import EmailMessage

load_dotenv()  # Load environment variables from .env file
DB_PATH = os.getenv('DB_PATH')
DB_CONNECT_CMD = os.getenv('DB_CONNECT_CMD')
APP_EMAIL = os.environ.get('APP_EMAIL')
APP_PASS = os.environ.get('APP_PASS')
DEST_NUMBER = os.environ.get('DEST_NUMBER')
DEST_EMAIL = DEST_NUMBER+'@'+os.environ.get('GATEWAY')


#### SMS SYSTEM FUNCTIONS ####

def server_event_listener():
    while True:
        # need some sort of break statement

        # get NAS Connection status
        nas_status = get_nas_connection_status()
        if ( nas_status != "Connected" ):
            send_text("NAS_DISCONNECT","The NAS has disconnected!",DEST_EMAIL)
        # get Plex Connection status
        plex_status = plex_status()
        if ( plex_status != "Running" ):
            send_text("PLEX_DOWN","Plex is currently down!",DEST_EMAIL)
        # get NAS Connection status
        jellyfin_status = jellyfin_status()
        if ( jellyfin_status != "Running" ):
            send_text("JELLYFIN_DOWN","Jellyfin is currently down!",DEST_EMAIL)
        
        # 10s between calls
        time.sleep(60)

def send_text(subject, body, destination):

    # creating the email message
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = destination
    msg['from'] = APP_EMAIL

    # creating the SMTP server
    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_server.starttls()
    smtp_server.login(APP_EMAIL, APP_PASS)
    smtp_server.send_message(msg)
    smtp_server.quit()

##############################


###### FLASK APP SETUP #######

app = Flask(__name__)

def get_nas_connection_status():
    try:
        result = subprocess.run(['timeout', '10', 'ls', DB_PATH], capture_output=True, text=True)
        if result.returncode == 0:
            return "Connected"
        elif result.returncode == 124 or result.returncode == 2:
            return "Disconnected"
        else:
            return "Unknown"
    except Exception as e:
        print(f"Error checking NAS connection status: {e}")
    return "Unknown"

def retryNasConnection():
    print("Retrying NAS connection...")
    try:
        subprocess.run(['sudo', 'mount', '-o', 'remount', DB_CONNECT_CMD], check=True)
    except Exception as e:
        print(f"Error retrying NAS connection: {e}")

@app.route('/nas-status')
def nas_status():
    # Return full status with HTML for initial load
    status = get_nas_connection_status()
    return f'<div class="status-badge status-{"running" if status == "Connected" else "down" if status == "Disconnected" else "default"}">{status}</div>'

@app.route('/retry-nas-connection')
def retry_nas_connection():
    try:
        retryNasConnection()  # Call the function to retry NAS connection
        status = get_nas_connection_status()  # Get new status after retry
    except Exception as e:
        print(f"Error retrying NAS connection: {e}")
        status = "Error"
    return status

@app.route('/')
def index():
    # Get the initial status for all services
    nas_status = get_nas_connection_status()
    plex_status = get_plex_status()
    jellyfin_status = get_jellyfin_status()
    return render_template('index.html', 
                         nas_connection_status=nas_status,
                         plex_status=plex_status,
                         jellyfin_status=jellyfin_status)

def get_plex_status():
    try:
        result = subprocess.run(['sudo', 'systemctl', 'is-active', 'plexmediaserver'], capture_output=True, text=True)
        status_output = result.stdout.strip()
        if status_output == 'active':
            return "Running"
        elif status_output == 'inactive':
            return "Down"
        else:
            return "Unknown"
    except Exception as e:
        print(f"Error getting Plex status: {e}")
    return "Unknown"  # Default status

@app.route('/plex-status')
def get_plex_status_endpoint():
    # Return full status with HTML for initial load
    status = get_plex_status()
    return f'<div class="status-badge status-{"running" if status == "Running" else "down" if status == "Down" else "default"}">{status}</div>'

@app.route('/start-plex')
def start_plex():
    try:
        startPlex()  # Call the function to start Plex
        status = get_plex_status()  # Check if started successfully
    except Exception as e:
        print(f"Error starting Plex: {e}")
        status = "Error" # what do i do with this?
    return status

@app.route('/stop-plex')
def stop_plex():
    try:
        stopPlex()  # Call the function to stop Plex
        status = get_plex_status() # Check if stopped successfully
    except Exception as e:
        print(f"Error stopping Plex: {e}")
        status = "Error"
    return status

@app.route('/restart-plex')
def restart_plex():
    try:
        restartPlex()  # Call the function to restart Plex
        status = get_plex_status()  # Check if restarted successfully
    except Exception as e:
        print(f"Error restarting Plex: {e}")
        status = "Error"
    return status

def startPlex():
    print("Starting Plex server...")
    try:
        subprocess.run(['sudo', 'systemctl', 'start', 'plexmediaserver'], check=True)
    except Exception as e:
        print(f"Error starting Plex: {e}")

def stopPlex():
    print("Stopping Plex server...")
    try:
        subprocess.run(['sudo', 'systemctl', 'stop', 'plexmediaserver'], check=True)
    except Exception as e:
        print(f"Error stopping Plex: {e}")

def restartPlex():
    print("Restarting Plex server...")
    try:
        subprocess.run(['sudo', 'systemctl', 'restart', 'plexmediaserver'], check=True)
    except Exception as e:
        print(f"Error restarting Plex: {e}")

# Jellyfin Control Functions
def get_jellyfin_status():
    try:
        result = subprocess.run(['sudo', 'systemctl', 'is-active', 'jellyfin.service'], capture_output=True, text=True)
        status_output = result.stdout.strip()
        if status_output == 'active':
            return "Running"
        elif status_output == 'inactive':
            return "Down"
        else:
            return "Unknown"
    except Exception as e:
        print(f"Error getting Jellyfin status: {e}")
    return "Unknown"  # Default status until actual check is implemented

@app.route('/jellyfin-status')
def get_jellyfin_status_endpoint():
    # Return full status with HTML for initial load
    status = get_jellyfin_status()
    return f'<div class="status-badge status-{"running" if status == "Running" else "down" if status == "Down" else "default"}">{status}</div>'

@app.route('/start-jellyfin')
def start_jellyfin():
    try:
        startJellyfin()  # Call the function to start Jellyfin
        status = get_jellyfin_status()  # Check if started successfully
    except Exception as e:
        print(f"Error starting Jellyfin: {e}")
        status = "Error"
    return status

@app.route('/stop-jellyfin')
def stop_jellyfin():
    try:
        stopJellyfin()  # Call the function to stop Jellyfin
        status = get_jellyfin_status()  # Check if stopped successfully
    except Exception as e:
        print(f"Error stopping Jellyfin: {e}")
        status = "Error"
    return status

@app.route('/restart-jellyfin')
def restart_jellyfin():
    try:
        restartJellyfin()  # Call the function to restart Jellyfin
        status = get_jellyfin_status()  # Check if restarted successfully
    except Exception as e:
        print(f"Error restarting Jellyfin: {e}")
        status = "Error"
    return status

def startJellyfin():
    print("Starting Jellyfin server...")
    try:
        subprocess.run(['sudo', 'systemctl', 'start', 'jellyfin.service'], check=True)
    except Exception as e:
        print(f"Error starting Jellyfin: {e}")

def stopJellyfin():
    print("Stopping Jellyfin server...")
    try:
        subprocess.run(['sudo', 'systemctl', 'stop', 'jellyfin.service'], check=True)
    except Exception as e:
        print(f"Error stopping Jellyfin: {e}")

def restartJellyfin():
    print("Restarting Jellyfin server...")
    try:
        subprocess.run(['sudo', 'systemctl', 'restart', 'jellyfin.service'], check=True)
    except Exception as e:
        print(f"Error restarting Jellyfin: {e}")

@app.route('/helloworld')
def helloworld():
    return "<h1>Hello World!</h1>"

##############################


if __name__ == "__main__":
    # starting the flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
    # running the server event listener in a separate thread
    threading.Thread(target=server_event_listener, daemon=True).start()
