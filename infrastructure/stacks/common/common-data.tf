data "aws_vpcs" "vpcs" {
  tags = {
    Name = var.vpc_name
  }
}

data "aws_vpc" "vpc" {
  count = length(data.aws_vpcs.vpcs.ids)
  id    = tolist(data.aws_vpcs.vpcs.ids)[count.index]
}

data "aws_subnet_ids" "texas_subnet_ids" {
  vpc_id = data.aws_vpc.vpc[0].id
  tags = {
    Name = "lk8s-${var.aws_account_name}.texasplatform.uk-private-*"
  }
}

data "aws_subnet" "texas_subnet" {
  count = length(data.aws_subnet_ids.texas_subnet_ids.ids)
  id    = tolist(data.aws_subnet_ids.texas_subnet_ids.ids)[count.index]
}

data "aws_security_group" "lambda_sg" {
  name = "${var.service_prefix}-hk-sg"
}


