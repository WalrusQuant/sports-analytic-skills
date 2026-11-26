# Setup checklist

- [ ] `npx skills add` completed for the skills this project needs
- [ ] `npx skills add . --list` on a checkout shows 20 skills, when a checkout is what is being tested
- [ ] sports-leader connector status recorded (connected, or explicitly not connected)
- [ ] `get_data_status` succeeded, or the manifest `generated_at` was read
- [ ] the chosen Parquet `url` is copied from that manifest
- [ ] optional notebook imports succeed only if the user asked for local Python
- [ ] no package from this repository was installed
- [ ] manifest `sha256` values for files the analysis will cite are written down
