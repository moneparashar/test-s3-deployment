pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
        S3_BUCKET = 'cf-templates-1krz2x79gf5ml-us-east-1/build/'
        GITHUB_REPO_URL = 'https://github.com/moneparashar/test-s3-deployment.git'
    }

    stages {
        stage('Checkout') {
            steps {
                // Clone the GitHub repository
                git branch: 'main', url: GITHUB_REPO_URL
            }
        }

        stage('Copy to S3') {
            steps {
                script {
                    // Get the latest zip file in the repository
                    def latestZipFile = sh(returnStdout: true, script: 'ls -t *.zip | head -n1').trim()
                    
                    // Install AWS CLI if not already installed
                    sh 'apt-get update && apt-get install -y awscli'
                    
                    // Authenticate AWS CLI
                    sh 'aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID'
                    sh 'aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY'
                    
                    // Copy the latest zip file to S3 bucket
                    sh "aws s3 cp $latestZipFile s3://$S3_BUCKET/"
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
