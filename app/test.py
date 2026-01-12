from integrations.canvasClient import CanvasClient

token = "7~N7ka3aGUPXkZMxe8PBhWxYDuyuU8WKR6APCRf4W6Dv742B3v9rUrHNJCBhQZxZVY"

client = CanvasClient(user_id=1, token=token, route="canvas")

#client.getCourses()

client.getAssignment("13744073")
