class ClosetEntry:
    def __init__(self, base64_encoded_image: str, filename: str, description: str, bucket_name: str, object_key: str, category: str):
        self.base64_encoded_image = base64_encoded_image
        self.filename = filename
        self.description = description
        self.bucket_name = bucket_name
        self.object_key = object_key
        self.category = category