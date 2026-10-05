"""Fetchers for published source data.

Each module here knows how to find, download and read one external
publication (an industry annual report, a statistics release) and turn it
into tidy rows. Nothing in here is model logic: the output is written to
``assumptions/<vintage>/timeseries/`` by a script under ``scripts/`` and the
model reads it through the assumption provider like any other input.
"""
