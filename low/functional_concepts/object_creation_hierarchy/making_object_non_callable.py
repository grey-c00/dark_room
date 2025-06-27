class NonCallableClass:
    def __new__(cls, *args, **kwargs):
        print("controlling object creation")
        # you will have to return the instance, or else every time None will be returned
        return super().__new__(cls,  *args, **kwargs)

    def __init__(self):
        print("Initialing NonCallableClass")

    # def __call__(self, *args, **kwargs):
    #     raise NotImplemented("Not implement error")

    def print_something(self):
        print("printing something")


non_callable_obj = NonCallableClass()
non_callable_obj.print_something()
non_callable_obj()

