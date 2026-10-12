"""Presentation-neutral views of the existing annual analytical outputs."""

def power_scenario_endpoints(analytics):
    """Return the opening power estimate and closing cases from the model bridge."""
    def value(cell):
        return cell['value'] if isinstance(cell, dict) else cell
    segments={row[0]:row for row in analytics['sheets']['Segments']['rows']}
    bridge={row[0]:row for row in analytics['sheets']['Driver bridge']['rows']}
    opening=value(segments['Utility and private power'][3])
    return [opening]+[opening+value(bridge[case][4]) for case in ('Base','Low imports','High imports')]
