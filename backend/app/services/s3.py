from minio import Minio
from minio.error import S3Error

from core.config import config
from utils.url import remove_query_params


class MinioClient:
    def __init__(self):
        self.client = Minio(
            f"{config.MINIO_DOMAIN}:{config.MINIO_PORT}",
            access_key=config.MINIO_USER,
            secret_key=config.MINIO_PASSWORD,
            secure=False
        )

    def create_bucket(self, bucket_name):
        try:
            self.client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully")
        except S3Error as err:
            print(err)

    def delete_bucket(self, bucket_name):
        try:
            self.client.remove_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' deleted successfully")
        except S3Error as err:
            print(err)

    def list_files(self, bucket_name):
        try:
            objects = self.client.list_objects(bucket_name, recursive=True)
            files = [obj.object_name for obj in objects]
            return files
        except S3Error as err:
            print(err)
            return []

    def get_file_path(self, bucket_name, file_name):
        try:
            url = self.client.presigned_get_object(bucket_name, file_name)
            url = remove_query_params(url)
            return url
        except S3Error as err:
            print(err)
            return None

    def delete_file(self, bucket_name, file_name):
        try:
            self.client.remove_object(bucket_name, file_name)
            print(f"File '{file_name}' deleted successfully from bucket '{bucket_name}'")
        except S3Error as err:
            print(err)

    def upload_file(self, bucket_name, file_data, object_name):
        try:
            file_data.seek(0)
            length = len(file_data.getvalue())
            self.client.put_object(bucket_name, object_name, file_data, length)
            print(f"File '{object_name}' uploaded successfully to bucket '{bucket_name}'")
            url = self.client.presigned_get_object(bucket_name, object_name)
            url = remove_query_params(url)
            return url
        except S3Error as err:
            print(err)

    def set_bucket_policy(self, bucket_name: str, policy):
        try:
            self.client.set_bucket_policy(bucket_name, policy)
            print("The access policy has been successfully set for the bucket", bucket_name)
        except S3Error as e:
            print("Error setting access policy:", e)
