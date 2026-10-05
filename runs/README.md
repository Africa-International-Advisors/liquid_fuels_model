# Model runs

Calculated CSVs and provenance are ignored by Git. First execution uses
`<vintage>-<scenario>-v<version>/`; subsequent executions preserve those files and create
a UTC timestamped subfolder within it. Provenance includes source and input hashes,
Git commit and dirty status, user, time, scenario, vintage and open exceptions.
`_migration/` is ignored local verification evidence, not a released model run.
