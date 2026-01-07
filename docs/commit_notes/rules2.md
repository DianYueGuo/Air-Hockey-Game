# Rules2

What changed
- Added goal openings in the physics walls so the puck can score.
- Set initial puck spawn to the serving side.
- Linked goal rendering to the new goal height field.

Manual test steps
- Run `python3 -m air_hockey.main`.
- Verify the puck can enter a goal opening and score.
- Confirm the puck spawns on the serving side at game start and after goals.

Known issues
- Goal width is fixed by `FieldSpec.goal_height`.
