# VPC Peering Module

A Terraform module for creating VPC peering connections between environments to enable AWS Batch jobs to connect to RDS across VPCs.

## Overview

This module implements a scalable VPC peering solution using the **requester/accepter pattern** for environments within the **same AWS account**:

- **Requester Environment** (e.g., RBA): Creates the peering connection and routes traffic to the accepter
- **Accepter Environment** (e.g., OS Hub Production): Creates routes back to the requester (peering is auto-accepted)

The module is designed to work within a single Terraform codebase that deploys to multiple environments sequentially.

## Architecture

```
┌─────────────────┐    VPC Peering    ┌─────────────────┐
│   RBA VPC       │◄─────────────────►│  OS Hub VPC     │
│  (Requester)    │                   │  (Accepter)     │
│                 │                   │                 │
│ ┌─────────────┐ │                   │ ┌─────────────┐ │
│ │AWS Batch    │ │                   │ │   RDS      │ │
│ │   Jobs      │ │                   │ │PostgreSQL  │ │
│ └─────────────┘ │                   │ └─────────────┘ │
└─────────────────┘                   └─────────────────┘
```

## How It Works

### 1. **Requester Environment Deployment**
- Creates VPC peering connection to accepter (auto-accepted in same account)
- Adds routes in private route tables to reach accepter VPC
- Creates security group rules allowing Batch jobs to connect to RDS

### 2. **Accepter Environment Deployment**
- Creates routes in private route tables to reach requester VPC
- Enables bidirectional communication

### 3. **Communication Flow**
- Batch jobs in RBA VPC can connect to RDS in OS Hub VPC
- Traffic flows through the VPC peering connection
- Security groups control access at the service level

## Requirements

1. Both VPCs must have non-overlapping CIDR blocks
2. Both environments must be deployed using the same Terraform codebase
3. Both environments must be in the same AWS account (enables auto-accept)

## Integration Steps

### Step 1: Add Variables to Your Main Variables File

Add these variables to your `deployment/terraform/variables.tf`:

```terraform
# VPC Peering Configuration
variable "requester_environment" {
  description = "The name of the environment that will be the requester (e.g., 'Rba')"
  type        = string
  default     = null
}

variable "accepter_environment" {
  description = "The name of the environment that will be the accepter (e.g., 'Production')"
  type        = string
  default     = null
}

# Accepter VPC Configuration (for cross-environment communication)
variable "accepter_vpc_id" {
  description = "VPC ID of the accepter environment"
  type        = string
  default     = null
}

variable "accepter_vpc_cidr" {
  description = "CIDR block of the accepter VPC"
  type        = string
  default     = null
}

variable "accepter_private_route_table_ids" {
  description = "List of private route table IDs in the accepter VPC"
  type        = list(string)
  default     = []
}

variable "accepter_rds_security_group_id" {
  description = "Security group ID of the RDS instance in the accepter VPC"
  type        = string
  default     = null
}
```

### Step 2: Add Module Call to Your Main Terraform

Add this module call to your `deployment/terraform/vpc_peering.tf`:

```terraform
module "vpc_peering" {
  source = "./vpc-peering"

  # Environment identification
  environment         = var.environment
  requester_environment = var.requester_environment
  accepter_environment  = var.accepter_environment

  # Current environment VPC (requester or accepter)
  requester_vpc_id                    = module.vpc.id
  requester_vpc_cidr                  = module.vpc.cidr_block
  requester_private_route_table_ids   = module.vpc.private_route_table_ids
  requester_batch_security_group_id   = aws_security_group.batch.id

  # Accepter VPC configuration
  accepter_vpc_id                    = var.accepter_vpc_id
  accepter_vpc_cidr                  = var.accepter_vpc_cidr
  accepter_private_route_table_ids   = var.accepter_private_route_table_ids
  accepter_rds_security_group_id     = var.accepter_rds_security_group_id

  # Service configuration
  rds_port = 5432

  # Feature flags
  create_security_group_rules = true
}
```

### Step 3: Configure Environment-Specific Values

#### For OS Hub Production (Accepter) Environment

In `deployment/environments/terraform-production.tfvars`:

```terraform
# VPC Peering Configuration
requester_environment = "Rba"
accepter_environment  = "Production"

# Accepter VPC (self-reference)
accepter_vpc_id                    = "vpc-production-id"
accepter_vpc_cidr                  = "10.0.0.0/16"
accepter_private_route_table_ids   = ["rtb-private-1", "rtb-private-2"]
accepter_rds_security_group_id     = "sg-rds-production"
```

#### For RBA Environment (Requester)

In `deployment/environments/terraform-rba.tfvars`:

```terraform
# VPC Peering Configuration
requester_environment = "Rba"
accepter_environment  = "Production"

# Accepter VPC (OS Hub Production)
accepter_vpc_id                    = "vpc-production-id"
accepter_vpc_cidr                  = "10.0.0.0/16"
accepter_private_route_table_ids   = ["rtb-private-1", "rtb-private-2"]
accepter_rds_security_group_id     = "sg-rds-production"
```

### Step 4: Update Secrets in CI-Deployment Repository

Add these values to your `ci-deployment` repository secrets:

```bash
# OS Hub Production VPC Details
OSHUB_PRODUCTION_VPC_ID="vpc-xxxxxxxxx"
OSHUB_PRODUCTION_VPC_CIDR="10.0.0.0/16"
OSHUB_PRODUCTION_PRIVATE_RT_IDS="rtb-xxxxxxxxx,rtb-yyyyyyyyy"
OSHUB_PRODUCTION_RDS_SG_ID="sg-xxxxxxxxx"

# RBA VPC Details
RBA_VPC_ID="vpc-xxxxxxxxx"
RBA_VPC_CIDR="10.1.0.0/16"
RBA_PRIVATE_RT_IDS="rtb-xxxxxxxxx,rtb-yyyyyyyyy"
RBA_BATCH_SG_ID="sg-xxxxxxxxx"
```

### Step 5: Update GitHub Actions Workflow

Modify your `.github/workflows/deploy_to_aws.yml` to merge these values:

```yaml
- name: Merge tfvars with secrets
  run: |
    # For OS Hub Production
    if [ "${{ env.ENVIRONMENT }}" = "Production" ]; then
      cat >> terraform.tfvars << EOF
    
    # VPC Peering Configuration
    requester_environment = "Rba"
    accepter_environment  = "Production"
    
    # Accepter VPC (self-reference)
    accepter_vpc_id                    = "${{ secrets.OSHUB_PRODUCTION_VPC_ID }}"
    accepter_vpc_cidr                  = "${{ secrets.OSHUB_PRODUCTION_VPC_CIDR }}"
    accepter_private_route_table_ids   = ["${{ secrets.OSHUB_PRODUCTION_PRIVATE_RT_IDS }}"]
    accepter_rds_security_group_id     = "${{ secrets.OSHUB_PRODUCTION_RDS_SG_ID }}"
    EOF
    fi
    
    # For RBA
    if [ "${{ env.ENVIRONMENT }}" = "Rba" ]; then
      cat >> terraform.tfvars << EOF
    
    # VPC Peering Configuration
    requester_environment = "Rba"
    accepter_environment  = "Production"
    
    # Accepter VPC (OS Hub Production)
    accepter_vpc_id                    = "${{ secrets.OSHUB_PRODUCTION_VPC_ID }}"
    accepter_vpc_cidr                  = "${{ secrets.OSHUB_PRODUCTION_VPC_CIDR }}"
    accepter_private_route_table_ids   = ["${{ secrets.OSHUB_PRODUCTION_PRIVATE_RT_IDS }}"]
    accepter_rds_security_group_id     = "${{ secrets.OSHUB_PRODUCTION_RDS_SG_ID }}"
    EOF
    fi
```

## Module Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| environment | Current environment being deployed | `string` | n/a | yes |
| requester_environment | Name of the requester environment | `string` | n/a | yes |
| accepter_environment | Name of the accepter environment | `string` | n/a | yes |
| requester_vpc_id | VPC ID of the requester environment | `string` | `null` | no |
| requester_vpc_cidr | CIDR block of the requester VPC | `string` | `null` | no |
| requester_private_route_table_ids | Private route table IDs in requester VPC | `list(string)` | `[]` | no |
| requester_batch_security_group_id | Security group ID for batch jobs in requester VPC | `string` | `null` | no |
| accepter_vpc_id | VPC ID of the accepter environment | `string` | `null` | no |
| accepter_vpc_cidr | CIDR block of the accepter VPC | `string` | `null` | no |
| accepter_private_route_table_ids | Private route table IDs in accepter VPC | `list(string)` | `[]` | no |
| accepter_rds_security_group_id | Security group ID for RDS in accepter VPC | `string` | `null` | no |
| rds_port | Port number for RDS PostgreSQL | `number` | `5432` | no |
| create_security_group_rules | Whether to create security group rules | `bool` | `true` | no |

## Deployment Workflow

### 1. Deploy OS Hub Production (Accepter)
- Module creates routes back to requester VPCs
- No peering connection resources created

### 2. Deploy RBA Environment (Requester)
- Module creates VPC peering connection (auto-accepted)
- Module creates routes and security group rules

### 3. Both environments can now communicate
- No manual acceptance needed (same account)
- Routes are automatically established

## Security Considerations

- **Network Isolation**: VPCs remain logically separate
- **Security Groups**: Fine-grained control over service access
- **Private Subnets**: All communication through private network
- **No Public Access**: Peering connection is internal only
- **Auto-Accept**: Same account enables automatic peering acceptance

## Scaling to New Environments

To add a new requester environment (e.g., "NewEnv"):

1. **Create new tfvars file** with requester configuration
2. **Update OS Hub Production** to include new environment routes
3. **Deploy new environment** - no code changes required

The module automatically handles:
- VPC peering connection creation (auto-accepted)
- Route table updates
- Security group rule creation
- Environment-specific configuration

## Troubleshooting

### Common Issues

1. **CIDR Overlap**: Ensure VPCs have different CIDR blocks
2. **Route Table Issues**: Verify private route tables are correctly specified
3. **Security Group Rules**: Check that rules are created for the correct security groups
4. **Peering Status**: Should be "active" automatically (same account)

### Debugging Commands

```bash
# Check VPC peering status
aws ec2 describe-vpc-peering-connections --vpc-peering-connection-ids pcx-xxxxxxxxx

# Check route tables
aws ec2 describe-route-tables --route-table-ids rtb-xxxxxxxxx

# Check security group rules
aws ec2 describe-security-group-rules --filters Name=group-id,Values=sg-xxxxxxxxx
```

## Next Steps

1. Test the connection with a simple Batch job
2. Monitor network traffic and performance
3. Consider adding CloudWatch alarms for peering connection status
4. Plan for additional requester environments if needed

## License

This module is part of the Open Supply Hub project and follows the same licensing terms.
