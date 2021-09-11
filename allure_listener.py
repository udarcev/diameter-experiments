import allure_commons


class AllureLogListener(object):

    @allure_commons.hookimpl(hookwrapper=True)
    def start_step(self, uuid, title, params):
        print(title)
        yield
