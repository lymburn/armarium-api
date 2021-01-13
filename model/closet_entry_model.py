class ClosetEntry:
    def __init__(self, filename: str, bucket_name: str, object_key: str, category: str):
        self.filename = filename
        self.bucket_name = bucket_name
        self.object_key = object_key
        self.category = category