pipeline {
    agent { node { label 'res-phy-prd-rpi-1' } }
    environment {
        WEBHOOK_URL = 'https://chat.internal.subterfuge.biz/hooks/ixsizrcwa7y35gtwn6mw3mr37a'
    }
    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }
        stage('Debug') {
            steps {
                sh 'pwd'
                sh 'ls -la'
                sh 'java -version'
                sh 'terraform -version'
                sh 'curl --version'
            }
        }
        stage('Plan') {
            steps {
                script {
                    dir('/code/aldrovanda/terraform') {
                        withCredentials([
                            string(credentialsId: 'digital-ocean', variable: 'TF_VAR_DIGITAL_OCEAN_TOKEN'),
                            string(credentialsId: 'cloudflare-api', variable: 'TF_VAR_CLOUDFLARE_KEY'),
                            string(credentialsId: 'cloudflare-zone', variable: 'TF_VAR_CLOUDFLARE_ZONE')
                        ]) {
                            sh """
                            set -e
                            export TF_VAR_DIGITAL_OCEAN_TOKEN=$TF_VAR_DIGITAL_OCEAN_TOKEN
                            export TF_VAR_CLOUDFLARE_KEY=$TF_VAR_CLOUDFLARE_KEY
                            export TF_VAR_CLOUDFLARE_ZONE=$TF_VAR_CLOUDFLARE_ZONE
                            terraform init || { echo 'Terraform init failed'; exit 1; }
                            terraform plan || { echo 'Terraform plan failed'; exit 1; }
                            """
                        }
                    }
                }
            }
        }
        stage('Apply') {
            steps {
                script {
                    dir('/code/aldrovanda/terraform') {
                        withCredentials([
                            string(credentialsId: 'digital-ocean', variable: 'TF_VAR_DIGITAL_OCEAN_TOKEN'),
                            string(credentialsId: 'cloudflare-api', variable: 'TF_VAR_CLOUDFLARE_KEY'),
                            string(credentialsId: 'cloudflare-zone', variable: 'TF_VAR_CLOUDFLARE_ZONE')
                        ]) {
                            sh """
                            set -e
                            export TF_VAR_DIGITAL_OCEAN_TOKEN=$TF_VAR_DIGITAL_OCEAN_TOKEN
                            export TF_VAR_CLOUDFLARE_KEY=$TF_VAR_CLOUDFLARE_KEY
                            export TF_VAR_CLOUDFLARE_ZONE=$TF_VAR_CLOUDFLARE_ZONE
                            terraform init || { echo 'Terraform init failed'; exit 1; }
                            terraform apply --auto-approve || { echo 'Terraform apply failed'; exit 1; }
                            """
                        }
                    }
                }
            }
        }
    }
    post {
        success {
            script {
                def message = "Pipeline succeeded for Aldrovanda Honeypot Build"
                sh """
                curl -k -X POST -H 'Content-Type: application/json' -d '{"text": "${message}"}' ${env.WEBHOOK_URL}
                """
            }
        }
        failure {
            script {
                def message = "Pipeline failed for Aldrovanda Honeypot Build"
                sh """
                curl -k -X POST -H 'Content-Type: application/json' -d '{"text": "${message}"}' ${env.WEBHOOK_URL}
                """
            }
        }
        always {
            cleanWs()
        }
    }
}