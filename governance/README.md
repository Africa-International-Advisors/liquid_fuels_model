# Assumption governance

The register is a declaration and audit trail, not a claim that the forecasts are validated.
Initial ownership is carried from the draft vintage owner, nigel.zhuwaki. Reviewer and
approver fields remain empty; confidence is unassessed. Nothing was marked verified.

Each structured YAML block declares `register_id` (a group) and `exception_id`.
Every scalar, null country slot and CSV observation within it has a separate register
row. CSV observation identities include the row index and dimension columns so changed
or reordered series require deliberate register reconciliation. Units and sources are
inherited from the original block; missing units are explicitly `not recorded`.
Missing original sources are labelled as such, not replaced with invented citations.

When updating an input:

1. Confirm the vintage is draft; create a new vintage if the current one is shipped.
2. Change the YAML/CSV and update the corresponding register values and metadata.
3. For new inputs, assign unique register row IDs and inherit a valid block reference.
4. Keep an open exception for unknown confidence/dates or provisional inputs. Every
   exception needs an owner, reason, risk, expiry date/trigger and migration path.
5. Source and review inputs before removing their exception reference. Record reviewer,
   confidence and source date; close the matching exception only when resolved.
6. Run `python -m lfm check --vintage 2026` and the model tests; examine output changes.

`check` rejects value drift, omitted/duplicate rows, missing ownership/source references,
missing or closed referenced exceptions, and expired exceptions. `--strict` additionally
rejects all open exceptions. The initial 43 exceptions expire on 12 November 2026 or
before formal release, whichever is earlier; closure requires work, not a date extension.

Workbook historical-demand CSVs used only by reconciliation are reference series, not
consumed forecast assumptions. They are nevertheless included in each run's input hashes.
Code-based legacy assumptions and central-engine integration are separately logged;
this migration does not claim those development tasks are complete.
