# Cam3

What changed
- Added detection markers on the webcam overlay preview in Play.

Manual test steps
- Run `python3 -m air_hockey.main`.
- Enter Play with overlay mode enabled.
- Verify circles appear over tracked balls in the overlay.

Known issues
- Marker positions are approximate and based on the last detection.
