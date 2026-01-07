# Phys10

What changed
- Switched mallets back to kinematic bodies for crisp, elastic collisions.
- Increased mallet restitution and reduced friction/damping to feel more “clicky.”

Manual test steps
- Run `python3 -m air_hockey.main`.
- Strike the puck with a mallet and confirm the collision feels elastic and clean.

Known issues
- Extremely fast camera jumps can still cause tunneling; adjust mallet speed if needed.
