# Phys11

What changed
- Switched mallets back to dynamic bodies with high density for solid elastic hits.
- Tuned mallet damping to keep control stable without tunneling.

Manual test steps
- Run `python3 -m air_hockey.main`.
- Strike the puck with each mallet and confirm collisions occur and feel elastic.

Known issues
- If mallets feel too heavy, reduce mallet speed or density.
