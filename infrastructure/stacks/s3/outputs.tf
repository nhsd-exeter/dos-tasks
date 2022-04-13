output "s3_bucket_id" {
  description = "ID value of the HK bucket"
  value       = module.housekeeping_bucket.s3_bucket_id
}

output "s3_bucket_arn" {
  description = "ARN value of the HK bucket"
  value       = module.housekeeping_bucket.s3_bucket_arn
}
