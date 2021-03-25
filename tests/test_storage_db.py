import base64
import storage.aws_s3 as aws_s3


def test_aws_img_read_write():
    bucket_name = aws_s3.create_bucket()

    # Smallest size of 256 x 256
    with open("test_files/small_img.jpg", "rb") as image_file:
        encoded_img_str = str(base64.b64encode(image_file.read()))
        upload_str = encoded_img_str[2:-1]

    aws_s3.upload_image(upload_str, bucket_name, "test-small-img")
    image_data = aws_s3.get_image_data(bucket_name, "test-small-img")
    assert upload_str == image_data, "Data strings not equal"
    print(
        f"Successful upload and download for smallest image size: {upload_str == image_data}")

    # Near largest size of 4k
    with open("test_files/large_img.jpg", "rb") as image_file:
        encoded_img_str = str(base64.b64encode(image_file.read()))
        upload_str = encoded_img_str[2:-1]

    aws_s3.upload_image(upload_str, bucket_name, "test-large-img")
    image_data = aws_s3.get_image_data(bucket_name, "test-large-img")
    assert upload_str == image_data, "Data strings not equal"
    print(
        f"Successful upload and download for largest image size: {upload_str == image_data}")

    aws_s3.empty_and_delete_bucket(bucket_name)
