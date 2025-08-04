# Create vpc
resource "aws_vpc" "vpc" {
  cidr_block = "10.10.0.0/16"

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# Create internet gateway and attach to your vpc
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

# Subnet
resource "aws_subnet" "public-subnet" {
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = "10.10.0.0/24"
  availability_zone = "eu-north-1a"

  tags = {
    Name = "${var.project_name}-public-subnet"
  }
}

resource "aws_route_table" "public-route-table" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

# Associate your public route table with your public subnet
resource "aws_route_table_association" "public-route-table-association" {
  subnet_id      = aws_subnet.public-subnet.id
  route_table_id = aws_route_table.public-route-table.id
}