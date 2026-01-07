# Phys4

What changed
- Increased Box2D solver iterations for more stable contacts.
- Enabled continuous collision (bullet) for the puck.
- Clamped kinematic mallet velocity to reduce tunneling and overlap.

Manual test steps
- Run `python3 -m air_hockey.main`.
- Move mallets into the puck and confirm they push it without overlapping.

Known issues
- Extremely fast camera jumps can still cause brief overlap.
