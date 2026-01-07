# Rules1

What changed
- Implemented traditional serve rule: the player who was scored on serves next.
- Puck now spawns on the serving player’s side after goals.
- Fixed reset to use teleport positioning.

Manual test steps
- Run `python3 -m air_hockey.main`.
- Score on the left goal; confirm the puck respawns on the left side.
- Score on the right goal; confirm the puck respawns on the right side.

Known issues
- None.
