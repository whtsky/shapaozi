# -*- coding: utf-8 -*-


def infohash_to_dict(data):
    data.pop('_id')
    if "files" in data:
        data["file_count"] = len(data["files"])
    else:
        data["file_count"] = 1
    return data


def infohash_simplified(data):
    data = infohash_to_dict(data)
    try:
        data.pop("files")
    except KeyError:
        pass
    return data
