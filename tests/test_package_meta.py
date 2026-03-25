import chronovault as cv


def test_package_exposes_version() -> None:
    assert isinstance(cv.__version__, str)
    assert cv.__version__
