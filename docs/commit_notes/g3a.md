# G3a

What changed
- Expanded Settings with a physics tuning mode for puck restitution, damping, max speed, and mallet speed.
- Applied physics settings to the Box2D world and clamped puck speed.

Manual test steps
- Run `python -m air_hockey.main`.
- Open Settings -> Physics Tuning and adjust values.
- Re-enter Play and verify behavior changes (speed/damping).

Known issues
- Physics changes apply when entering Play; live updates are not applied.
