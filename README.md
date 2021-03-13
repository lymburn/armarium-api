# Armarium Outfit Recommendation and Virtual Closet iOS App

# Documentation for ML Functions
## Graph Structure
- Graph used for outfit generation has the following structure:
    - (top, bottom) - shoes - bag - accessory
        - Usually shorthanded as: (tb)sga
    - Each item has its own node, with the exception of tops and bottoms, which are combined as a tuple
    - Object keys are used as node names to simplify file access
    - There is an implied direction to the graph, with (top, bottom) as source nodes in outfit generation, and accessory as target nodes



# Documentation for Storage and Database Functions
## Naming Things
### Database Tables:
- Files table:
	- Filename is the system filename, description is the user description for the file
	- For graphs, the graph_name is the object_key and uses closet_name as the filename in object key generation
	- Category is one of the following: 'top', 'bottom', 'shoes', 'bag', 'accessory', or 'graph'
		- Should be standarized across frontend, backend, and graph generation dictionaries
- RecommendedOutfits clothing item columns contain AWS S3 object keys instead of the filename from Files
- Assumptions:
	- Filenames are unique per closet (Database functions still return a list of items, to catch edge cases / functionality we have yet to standardize)
	- Closet names are unique per user

### AWS S3 Bucket Naming Rules:
- https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html
- Bucket names should be unique within the region / globally unique
- Bucket names must be 3 - 63 characters long
- Bucket names can consist only of lowercase letters, numbers, and hyphens (-)
- Begin and end with a letter or number
- Cannot begin with 'xn--'

### AWS Object Key Naming Guidelines:
- https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingMetadata.html
- Key needs to unique identify item in bucket
- Safe characters: 0-9, a-z (+ uppercase), and some special characters (/!-_.*'())
- Max 1024 bytes long
- Armarium uses UUID V4 as part of object key string
    - Using V4 not V1 to ensure higher security, since V1 is generated using MAC addr and timer
    - Using uuid b/c it is more random and secure than the random library


## Working with Boto & AWS S3
### Functions that interact w AWS S3 (Wrappers for Boto3 Client and Bucket methods)
- S3 Buckets: Only need 1 bucket for now, since buckets can store unlimited items
    - Must empty bucket (delete all items) before bucket can be deleted
- S3 Objects:
	- Images are stored as base64encoded byte strings, though a decode + re-encode process is done on the original string received from the app's HTTP request
        - NOTE: Instead of passing data following the format: "b'data'", the client and server are simply passing the data as a string: "data"
	- Graphs are serialized into JSON via NetworkX

