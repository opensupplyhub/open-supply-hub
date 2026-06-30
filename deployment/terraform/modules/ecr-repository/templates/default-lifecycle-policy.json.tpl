{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Expire untagged images older than 7 days",
            "selection": {
                "tagStatus": "untagged",
                "countType": "sinceImagePushed",
                "countNumber": 7,
                "countUnit": "days"
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}