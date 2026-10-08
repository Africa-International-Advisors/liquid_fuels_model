# South Africa review: first implementation

Open [the evidence pack](index.html) for the 12 exhibits, primary-source supply
findings and outstanding work. [Exhibit data](exhibit_data.csv),
[audit tracker](audit_tracker.csv), [source hashes](provenance.json) and
[supply findings](supply_findings.json) accompany it. Each chart is also an SVG.

This v3 supersedes the v1/v2 implementation drafts. The signed-off review scope
pack and the existing Convergence PowerPoint/PDF are unchanged.

Status: historical evidence and current-engine diagnostics, not a new calibrated
forecast. Gauteng is the provisional Lesedi boundary selected by the user.
Market shares and investment returns remain unquantified pending commercial data.
The report identifies fiscal/calendar, fuel, price and ownership boundaries.

Validation: full Python suite passed (151 tests); after adding the quarterly
completeness regression, all 11 targeted review tests passed. Governance coverage
passed with 55 open exceptions. The 12 SVG exhibits rendered successfully and were
visually inspected; no connected browser was available for HTML page-level review.
No independent evidence approval or business approval is implied.

Rebuild into a new directory to preserve previous outputs:

```powershell
.\.venv\Scripts\python.exe -m lfm.scripts.build_sa_review_evidence --output-dir output/delivered/sa_review_<new-version>
```
