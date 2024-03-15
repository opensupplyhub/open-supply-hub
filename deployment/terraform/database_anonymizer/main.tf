module "database_anonymizer" {
  source = "git::git@github.com:terraform-aws-modules/terraform-aws-lambda.git?ref=v7.2.2"

  function_name = "database-anonymizer"
  handler       = "database_anonymizer.lambda_handler"
  runtime       = "python3.8"
  timeout       = 900

  source_path = "${path.module}/src/"

  vpc_subnet_ids = [
    "subnet-0afc4b6653f5c140e",
    "subnet-02e90cb2b988c7a57"
  ]

  vpc_security_group_ids = [
    "sg-08a14530e8c5bd1ea",
    "sg-03966450014448ded",
    "sg-0f24a8c67c95e6827"
  ]

  attach_network_policy              = true
  replace_security_groups_on_destroy = true

  replacement_security_group_ids = [
    "sg-08a14530e8c5bd1ea",
    "sg-03966450014448ded",
    "sg-0f24a8c67c95e6827"
  ]

  attach_policy = true
  policy        = "arn:aws:iam::aws:policy/AmazonRDSFullAccess"

  environment_variables = {
    SOURCE_DATABASE_IDENTIFIER     = var.rds_database_identifier
    SOURCE_DATABASE_PASSWORD       = var.rds_database_password
    SOURCE_DATABASE_USER           = var.rds_database_username
    SOURCE_DATABASE_NAME           = var.rds_database_name
    DESTINATION_AWS_ACCOUNT        = var.destination_aws_account
    ANONYMIZER_DATABASE_IDENTIFIER = var.anonymizer_db_identifier
  }
    
  timeouts = {
    create = "20m"
    update = "20m"
    delete = "20m"
  }
}
