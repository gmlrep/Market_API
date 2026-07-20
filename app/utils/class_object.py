def singleton(class_):
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    get_instance._instances = instances
    get_instance._wrapped_cls = class_
    return get_instance
