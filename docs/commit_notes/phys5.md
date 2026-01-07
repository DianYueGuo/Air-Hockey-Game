# Phys5

What changed
- Switched mallets back to dynamic bodies with fixed rotation for better collision response.
- Enabled continuous collision on mallets to reduce tunneling.

Manual test steps
- Run `python3 -m air_hockey.main`.
- Move mallets into the puck and verify they push it away from center.

Known issues
- Mallets will react slightly to puck impacts; adjust damping if needed.
