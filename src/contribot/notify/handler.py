def handler(event, context):
    list_id = event.get("list_id", "unknown")

    return {
        "list_id": list_id,
        "notified": True,
    }
