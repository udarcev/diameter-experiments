from allure import step

import kafka_consumer.async_kafka as kafka
import server.async_server as server
from tests.common.TestParent import TestParent


class TestParentKafka(TestParent):
    def setup(self):
        with step("Запуск диаметр клиента"):
            server.init_server()
            self.cers()
        with step("Запуск kafka consumer"):
            kafka.init_kafka()

    def teardown(self):
        with step("Остановка диаметр клиента"):
            server.finalize_server()
        with step("Остановка kafka consumer"):
            kafka.finalize_kafka()
