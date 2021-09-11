import allure_commons
import pytest

from allure_listener import AllureLogListener
from avp.BaseGenerator import generator_dict


@pytest.fixture(autouse=True)
def close_all_sessions(request):
    yield
    from server.async_server import send_request
    if request.node.name in generator_dict:
        for session in generator_dict[request.node.name]:
            if session.status:
                send_request(session.test_message(terminate=True), session.generator_name)
                session.status = False


def pytest_addoption(parser):
    parser.addoption("--capture", action="store", default="tee-sys")


def pytest_configure(config):
    allure_log_listener = AllureLogListener()  # allure_listener
    config.pluginmanager.register(allure_log_listener)
    allure_commons.plugin_manager.register(allure_log_listener)
