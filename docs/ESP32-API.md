# ESP32 incident endpoint

The ESP32 should send a `POST` request to the Django computer running Elevate:

```text
http://<COMPUTER-LAN-IP>:8010/api/v1/incidents/
```

Use the computer's Wi-Fi/LAN IPv4 address in place of `<COMPUTER-LAN-IP>`. Do not use `127.0.0.1` in the ESP32 sketch: that address means the ESP32 itself. The computer and ESP32 must be on the same network, and the Windows firewall must allow Python on the private network.

## Start the API securely

In PowerShell, set a private shared token and add the computer's LAN IP to Django's allowed hosts before starting `run_project.bat`:

```powershell
$env:ELEVATE_DEVICE_API_TOKEN = "choose-a-long-random-secret"
$env:ELEVATE_ALLOWED_HOSTS = "127.0.0.1,localhost,192.168.1.23"
cd "$env:USERPROFILE\Desktop\project-elevate"
.\run_project.bat
```

Replace `192.168.1.23` with the computer's actual LAN IPv4 address. Keep this PowerShell window open. The same token must be sent by the ESP32 in the `X-Device-Token` header. Restart the server if either value changes.

## Request

Send `Content-Type: application/json` and an object like this:

```json
{
  "elevator_code": "ELEV-01",
  "device_id": "ESP32-ELEV-01",
  "title": "Door obstruction detected",
  "description": "Door sensor remained blocked for 8 seconds on floor 3.",
  "category": "Door sensor",
  "severity": "high"
}
```

Required fields: `elevator_code`, `title`, and `description`. `severity` can be `low`, `medium`, `high`, or `critical`; it defaults to `high`. The elevator code must already exist in Elevate. Successful requests return HTTP `201` and a JSON incident ID. Admin staff then assign the incident to a technician; it appears in that technician's task list after assignment.

Example response:

```json
{"id": 12, "status": "open", "message": "Incident created."}
```

The endpoint is `POST` only and returns JSON error messages for missing/invalid tokens, malformed requests, or unknown elevator codes.
