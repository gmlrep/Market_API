from sqlalchemy import and_


SQLALCHEMY_QUERY_MAPPER = {
    "eq": "__eq__",
    "ne": "__ne__",
    "lt": "__lt__",
    "lte": "__le__",
    "gt": "__gt__",
    "gte": "__ge__",
}


def dict_to_sqlalchemy_filter_options(model_class, search_options_dict):
    sqlalchemy_filter_options = []
    copied_dict = search_options_dict.copy()
    for key in list(search_options_dict.keys()):
        attr = getattr(model_class, key, None)
        if attr is None:
            continue
        option_from_dict = copied_dict.pop(key)
        if type(option_from_dict) in [int, float]:
            sqlalchemy_filter_options.append(attr == option_from_dict)
        elif type(option_from_dict) in [str]:
            sqlalchemy_filter_options.append(attr.like("%" + option_from_dict + "%"))
        elif type(option_from_dict) in [bool]:
            sqlalchemy_filter_options.append(attr.is_(option_from_dict))

    for custom_option in copied_dict:
        if "__" not in custom_option:
            continue
        key, command = custom_option.split("__", 1)
        attr = getattr(model_class, key, None)
        if attr is None:
            continue
        option_from_dict = copied_dict[custom_option]
        if command == "in":
            sqlalchemy_filter_options.append(
                attr.in_([option for option in option_from_dict])
            )
        elif command in SQLALCHEMY_QUERY_MAPPER:
            sqlalchemy_filter_options.append(
                getattr(attr, SQLALCHEMY_QUERY_MAPPER[command])(option_from_dict)
            )
        elif command == "isnull":
            bool_command = "__eq__" if option_from_dict else "__ne__"
            sqlalchemy_filter_options.append(getattr(attr, bool_command)(None))

    return and_(True, *sqlalchemy_filter_options)


# typo-compatible alias used by link_cutter-style BaseRepository
dict_to_sclachemy_filter_options = dict_to_sqlalchemy_filter_options
