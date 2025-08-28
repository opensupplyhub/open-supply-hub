output "registrar_result" {
  value = jsondecode(data.aws_lambda_invocation.nlb_targets_registrar.result)
}