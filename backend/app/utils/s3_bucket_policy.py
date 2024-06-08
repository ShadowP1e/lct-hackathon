def get_policy(bucket_name: str) -> str:
    return """
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "*"
                },
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::%s/*"
            }
        ]
    }
    """ % bucket_name
