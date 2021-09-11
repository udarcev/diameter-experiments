import os


def last_part_for_msisdn(start: int, end: int):
    number = range(start, end)
    while True:
        for i in number:
            if len(str(i)) != 4:
                last_part_for_msisdn_ = f'{"0" * (4 - len(str(i))) + str(i)}'
                yield last_part_for_msisdn_
            else:
                last_part_for_msisdn_ = str(i)
                yield last_part_for_msisdn_


# Костыль для параллельного запуска
worker_name = os.getenv('PYTEST_XDIST_WORKER', '0')
worker_number = worker_name.replace('gw', '')
number_generator = last_part_for_msisdn(100 * int(worker_number), 10000)
