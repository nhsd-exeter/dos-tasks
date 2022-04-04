locals {
  standard_tags = {
    "Programme"   = var.programme
    "Service"     = "core-dos"
    "Product"     = "core-dos"
    "Environment" = var.profile
  }
}
