"""Device selection and config loading — the parts that broke on real machines.

`config.yaml` ships `device: cuda`, and on a machine without a GPU that used to
put the model on CPU and the inputs on CUDA. The model itself needs a downloaded
transformer, so it is not built here; what is checked is the logic around it.
"""

import logging

import pytest

torch = pytest.importorskip("torch")

from src.utils import resolve_device
from src.utils import load_config, setup_logging


def test_auto_picks_a_device_that_exists():
    device = resolve_device("auto")
    assert device.type in ("cuda", "cpu")
    if not torch.cuda.is_available():
        assert device.type == "cpu"


def test_none_behaves_like_auto():
    assert resolve_device(None).type == resolve_device("auto").type


def test_asking_for_cuda_without_cuda_falls_back_and_warns(caplog):
    if torch.cuda.is_available():
        pytest.skip("this machine has CUDA, so there is nothing to fall back from")
    with caplog.at_level(logging.WARNING):
        device = resolve_device("cuda")
    assert device.type == "cpu", "the config shipping device: cuda must not break a CPU machine"
    assert any("CUDA" in r.message or "cuda" in r.message for r in caplog.records), \
        "falling back silently hides why inference is slow"


def test_an_explicit_cpu_request_is_honoured():
    assert resolve_device("cpu").type == "cpu"


def test_config_yaml_in_the_repo_loads_and_names_a_model():
    config = load_config("config.yaml")
    assert isinstance(config, dict) and config, "config.yaml should not be empty"
    assert any(key in config for key in ("model", "model_path", "model_name")), \
        f"no model named in config.yaml: {sorted(config)}"


def test_a_missing_config_is_an_empty_dict_not_a_crash(tmp_path):
    assert load_config(str(tmp_path / "absent.yaml")) == {}


def test_logging_setup_is_idempotent():
    root = logging.getLogger()
    setup_logging()
    count = len(root.handlers)
    setup_logging()
    assert len(root.handlers) == count, "calling setup twice must not double every log line"
