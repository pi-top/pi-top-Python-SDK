def test_formatter_prints_without_a_terminal(capfd, monkeypatch):
    from pitopcli.formatter import StdoutFormat

    monkeypatch.delenv("COLUMNS", raising=False)
    monkeypatch.delenv("LINES", raising=False)

    StdoutFormat.print_header("pi-top Devices")
    StdoutFormat.print_section("Hub")
    StdoutFormat.print_subsection("Peripherals")

    out = capfd.readouterr().out
    assert "pi-top Devices" in out
    assert "Hub" in out
