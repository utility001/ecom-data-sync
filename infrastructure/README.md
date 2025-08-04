# Infrastructure

Contains the terraform code to provision AWS networking, IAM, Secrets Manager, and Redshift resources for EcomDataSync

## Folders

```

.
├── README.md
├── backend.tf # Remote s3 state configuration
├── iam.tf # Airflow IAM user configuraton 
├── providers.tf 
├── redshift.tf # Reshift cluster
├── variables.tf # Variabls
└── vpc.tf # vpc

```
