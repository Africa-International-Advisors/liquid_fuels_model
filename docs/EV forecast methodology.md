**EV forecast methodology**



The core projection uses a logistic (Boltzmann) S-curve to model EV adoption over time. This is governed by three parameters for each scenario, pulled from named ranges: 

* Max penetration = 30% \& 90% 
* High-value year (midpoint) = 2040
* Slope (steepness) = 3 
* Penetration rate(t) = 1/(1 + EXP(midpoint -t)/slope)



New vehicle demand is forecast using a simple linear regression of GDP/capita (constant 2015ZAR) against historical new vehicle sales. 

* Slope : 37.31
* Intercept: 2,387,744
* R-squared : 51%
* Formula: New vehicle demand = 37.31(GDP/capita) - 2,387,744



The Cumulative EV stock build-up accumulates each year as: 

* EV Stock(t) = EV Stock(t-1) + New Vehicle Demand(t)\*Penetration Rate(t)  



The current model does not assume vehicle scrappage, may overstate fleet size over time 

The model assumes a exponential increase post 1% penetration 



The model does not take into consideration the penetration charging infrastructure which is a big factor in buyer confidence and the adoption of EV. Furthermore the price of gasoline is not factored into consideration, as the price of gasoline increase people will need alternative fuel. SSEG penetration in households may also be an indicative factor to consider. Charging infrastructure access is identified as the strongest short-to-medium-term barrier , without ambitious public charging rollout BEV adoption remains negligible. 



Justification for the model: 
1) Logistic form is mathematically sound and well adopted by literature for electric vehicle penetration 

2\) The 2040 midpoint is broadly consistent with literature of similar regions, substantial BEV fleet penetration is post 2030 even in optimistic EU scenarios 

3\) EV stock build-up, this omits the fleet retirement/ vehicle scrappage 



