# Provincial demand forecasting — method task, 6 October 2026

Status: queued after source reconciliation. Owner: Manish (data and model development); Nigel (scenario decisions). SCR links: pages 4 and 7; national accounting on page 5.

## Keep three outputs separate

1. **Recent-period estimate:** bridge the gap from complete 2022 provincial observations to the latest date. Search for observed provincial data first. Label any inferred province/product/year separately from observed data; preserve incomplete periods.
2. **Baseline forecast:** project petrol and diesel demand by province from a reconciled history, with uncertainty. Ten annual observations alone are a weak basis for complex seasonal models; use quarterly history only after coverage and revisions pass review.
3. **Lever scenarios:** state alternatives for mileage, fleet fuel mix, efficiency, road/rail activity, agriculture, manufacturing, mining, diesel power and fuel prices. Translate activity into litres through calibrated relationships. Avoid counting overlapping activity/efficiency effects twice.

## Method comparison and decision

- Establish naive, drift and exponential-smoothing benchmarks before ARIMA. Compare parsimonious ARIMA/SARIMA and SARIMAX with sourced external drivers. Do not select a complex model from in-sample fit alone.
- Review COVID, reporting revisions and refinery/economic breaks; preserve event annotations. Missing values are not zero. Seasonal models require enough complete seasonal cycles.
- Use rolling-origin backtests at the intended horizon, train-only preprocessing and drivers available at each forecast origin. Assess absolute error, bias, stability and interval coverage. Report performance by province/product alongside national results.
- Reconcile provincial forecasts to a compatible national demand total. Demand forecasts and the production/import/export/stock balance remain separate calculations. Forecast growth must not silently close an accounting residual.
- Compare tool suitability after the data contract is agreed: [statsmodels](https://www.statsmodels.org/stable/gettingstarted.html) for transparent statistical benchmarks; [sktime](https://www.sktime.net/) for consistent forecasting evaluation; [Darts](https://unit8co.github.io/darts/) for covariates, probabilistic alternatives and reconciliation. No library or specification has been selected.

## Reviewable handback and closure

Return a source/coverage table, observed-versus-estimated flags, revision log, national reconciliation, benchmark backtest and model-choice memo. Show baseline, low/high lever cases and uncertainty separately. Keep assumptions in vintaged YAML/CSV and declare consumed model inputs in the register; engine code belongs in `src/lfm/model/`, scripts in `src/lfm/scripts/`. Presentation builders consume outputs and do not implement forecasting.

Expiry trigger: revisit the method when new complete provincial data or a material revision arrives. A passing test does not establish source validation or business approval.

Related records: [6 October feedback and focus](feedback_focus_2026-10-06.md), [Manish handover](manish_handover_2026-10-06.md), [stand-up minutes](../meetings/2026-10-06_vopak_standup.docx).
