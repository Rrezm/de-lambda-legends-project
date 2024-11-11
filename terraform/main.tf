terraform {
    required_providers{
        aws = {
            source  = "hashicorp/aws"
            version = "~> 5.0"
        }
    }
   

    }

provider "aws" {
    region = "eu-west-2"
     default_tags {
    tags = {
      ProjectName = "Lambda Legends Data Processor"
      Team = "Lambda Legends"
      DeployedFrom = "Terraform"
      Repository = "de-lambda-legends-project"
      CostCentre = "DE"
      Environment = "dev"
      RetentionDate = "2024-11-30"
      
      }
  }


    }

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}






