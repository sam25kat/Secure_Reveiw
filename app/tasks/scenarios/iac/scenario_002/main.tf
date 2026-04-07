provider "aws" {
  region = var.region
}

resource "aws_dynamodb_table" "api_data" {
  name           = "api-data-table"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  range_key      = "timestamp"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  tags = {
    Name        = "api-data-table"
    Environment = "production"
  }
}

resource "aws_lambda_function" "api_handler" {
  function_name = "api-handler"
  runtime       = "python3.11"
  handler       = "handler.lambda_handler"
  filename      = "lambda.zip"
  role          = aws_iam_role.lambda_exec.arn
  memory_size   = 256
  timeout       = 30

  environment {
    variables = {
      TABLE_NAME  = aws_dynamodb_table.api_data.name
      ENVIRONMENT = "production"
    }
  }

  tags = {
    Name        = "api-handler"
    Environment = "production"
  }
}

resource "aws_api_gateway_rest_api" "api" {
  name        = "serverless-api"
  description = "Serverless REST API for data processing"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.proxy.id
  http_method             = aws_api_gateway_method.proxy.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api_handler.invoke_arn
}

resource "aws_api_gateway_deployment" "api" {
  depends_on  = [aws_api_gateway_integration.lambda]
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = "prod"
}
