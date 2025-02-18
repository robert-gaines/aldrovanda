terraform {
    backend "local" {
        path = "/mnt/configuration/aldrovanda_tfstate/tfstate.json"
    }
}