# when ready to ship, run "pip3 freeze > requirements.txt" and it will
# pipe all of your requirements into the file
from flask import Flask, render_template
import subprocess

app = Flask(__name__)

def get_nas_connection_status():
    # TODO: Implement actual NAS connection check
    # This is a placeholder - replace with real NAS connection check
    return "Unknown"  # Default status until actual check is implemented

def retryNasConnection():
    # TODO: Implement actual NAS connection retry logic
    # This is where you'll put the code to retry the NAS connection
    print("Retrying NAS connection...")
    # Add your NAS connection retry implementation here
    pass

from flask import jsonify

from flask import request

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
        else:
            return "Down"
    except Exception as e:
        print(f"Error getting Plex status: {e}")
    return "Unknown"  # Default status until actual check is implemented

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
        status = "Down"  # Assuming successful stop
    except Exception as e:
        print(f"Error stopping Plex: {e}")
        status = "Error"
    return status

@app.route('/restart-plex')
def restart_plex():
    try:
        restartPlex()  # Call the function to restart Plex
        print("it works!")
        status = "Running"  # Assuming successful restart
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
    # TODO: Implement actual Jellyfin status check
    # This is a placeholder - replace with real Jellyfin server status check
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
        status = "Running"  # Assuming successful start
    except Exception as e:
        print(f"Error starting Jellyfin: {e}")
        status = "Error"
    return status

@app.route('/stop-jellyfin')
def stop_jellyfin():
    try:
        stopJellyfin()  # Call the function to stop Jellyfin
        status = "Down"  # Assuming successful stop
    except Exception as e:
        print(f"Error stopping Jellyfin: {e}")
        status = "Error"
    return status

@app.route('/restart-jellyfin')
def restart_jellyfin():
    try:
        restartJellyfin()  # Call the function to restart Jellyfin
        status = "Running"  # Assuming successful restart
    except Exception as e:
        print(f"Error restarting Jellyfin: {e}")
        status = "Error"
    return status

def startJellyfin():
    # TODO: Implement actual Jellyfin start logic
    # This is where you'll put the code to start your Jellyfin server
    print("Starting Jellyfin server...")
    # Add your Jellyfin start implementation here
    pass

def stopJellyfin():
    # TODO: Implement actual Jellyfin stop logic
    # This is where you'll put the code to stop your Jellyfin server
    print("Stopping Jellyfin server...")
    # Add your Jellyfin stop implementation here
    pass

def restartJellyfin():
    # TODO: Implement actual Jellyfin restart logic
    # This is where you'll put the code to restart your Jellyfin server
    print("Restarting Jellyfin server...")
    # Add your Jellyfin restart implementation here
    pass

@app.route('/helloworld')
def helloworld():
    return "<h1>Hello World!</h1>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)