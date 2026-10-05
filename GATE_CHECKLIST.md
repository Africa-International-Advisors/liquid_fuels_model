# Formal-use gate

Structural migration is not model validation. All nine gates must pass before formal use.

- [x] 1. Decision clarity: stated in README.md and `src/lfm/model/__init__.py`.
- [x] 2. Assumption ownership: every current declared scalar/CSV observation has a register row;
  ownership inherited from the vintage owner. Confidence and review remain unassessed.
- [ ] 3. Registry discipline: central provider integration remains EXC-ENGINE.
- [ ] 4. Scenario discipline: local metadata exists; central scenario mapping remains EXC-SCENARIOS.
- [ ] 5. Calculation transparency: engine code relocated and CLI resolves an in-memory snapshot;
  legacy constants and methodology review remain EXC-CODE and EXC-LOGIC.
- [ ] 6. Independent peer review: not recorded.
- [x] 7. Provenance mechanism: CLI records code commit/hashes, input hashes, user, scenario and time.
- [x] 8. Limitations visible: open exceptions are logged and make every run provisional.
- [ ] 9. Business owner approval: not recorded.

`python -m lfm check` checks coverage and stale/expired declarations.
`python -m lfm check --strict` also rejects open exceptions. Neither command substitutes
for peer review or business approval. No approval has been inferred during migration.
