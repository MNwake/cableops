from typing import Any


class ResponseHandler:
    @staticmethod
    def success(message: str, data: Any = None) -> dict:
        response = {
            "type": "success",
            "message": message
        }
        if data:
            response["data"] = data
        return response

    @staticmethod
    def error(message: str) -> dict:
        return {
            "type": "error",
            "item_type": message
        }

    @staticmethod
    def update(item_type: str, data: Any = None) -> dict:
        response = {
            "type": "update",
            "item_type": item_type
        }
        if data:
            response["data"] = data
        return response