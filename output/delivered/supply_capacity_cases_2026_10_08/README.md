# Future refinery capacity sensitivities

[Chart](future_capacity.png) | [Resolved data and input hashes](data.json)

Restores the previous conditional SAPREF illustration and adds a Natref availability
stress case. The chart compares the historical reported footprint with three
illustrative 2036 endpoints on one scale, in thousand barrels/day:

- Low: 250, excluding Natref's 108 from the 2025 reported 358 footprint.
- Medium: 358, holding the reported footprint unchanged.
- High: 758, retaining Natref and adding the existing 400 SAPREF proposal.

The inherited high-case assumption is 2029 FID plus 48 months construction, giving
2033 assumed availability. No Natref closure date or closure prediction is asserted.
The horizon and SAPREF proposal reuse `review_capacity_scenarios.yaml`; new categorical
case choices are registered in `review_supply_worlds.yaml`, unreviewed and provisional.

These are partial capacity sensitivities, not calibrated L/M/H fuel production forecasts.
Sasol's 150 kbpd crude-equivalent footprint remains unchanged; the gas/MRG liquids penalty
is not yet quantified. No PetroSA restart is added. Astron is held unchanged and Enref's
reported contribution remains zero. Source dashes are excluded contributions, not proof
that physical equipment has disappeared. The chart does not apply ramp-up or utilisation.

Next conversion: plant availability and utilisation, product yields and gas balance
produce fuel-output paths; cross these with demand, then route/capture assumptions and
required/achievable tank turns before choosing an investment. No terminal return is implied.

Owner: Manish; Nigel review. Resolve before engine adoption, scenario approval or formal
investment use, under EXC-SUPPLY-REVIEW-2026-10-06 (expires 12 November 2026).
