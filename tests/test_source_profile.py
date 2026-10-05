from lfm.scripts import profile_data_sources as profile


def test_dated_snapshot_is_not_mistaken_for_a_time_series():
    assert profile.shape({"csv":"fleet.csv"},[{"period":"2023"},{"period":"2023"}]) == "Dated snapshot"
    assert profile.shape({"csv":"fleet.csv"},[{"period":"2023"},{"period":"2024"}]) == "Time series"
    assert profile.shape({"value":2.0}) == "Scalar"
    assert profile.shape({"value":{"slope":2.0}}) == "Structured parameters / assumptions"


def test_successful_retry_retains_the_original_failure(monkeypatch):
    outcomes=iter([{"result":"HTTP error","http_status":502,"seconds":0.5,"detail":"Bad gateway"},
                   {"result":"Reachable; expected sample","http_status":200,"seconds":0.2,"detail":"Sample only"}])
    monkeypatch.setattr(profile,"probe",lambda target:next(outcomes))
    result=profile.probe_with_retry({"url":"https://example.org"})
    assert result["attempts"]==2
    assert "502" in result["detail"]
    assert "intermittent" in result["result"]


def test_macro_enabled_workbook_is_checked_as_excel():
    assert profile.expected_type("https://example.org/balance.xlsm") == "Excel"
