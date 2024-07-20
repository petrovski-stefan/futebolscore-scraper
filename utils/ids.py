def get_ids(start_id: int | None, end_id: int | None) -> range | list[str] | None:
    if start_id and end_id and start_id < end_id:
        return range(start_id, end_id + 1)
    else:
        print("Error entering the arguments. Try again!")
