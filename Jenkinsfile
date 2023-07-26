pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
        S3_BUCKET = 'test-cicd-vivally/build/'
        GITHUB_REPO_URL = 'https://github.com/moneparashar/test-s3-deployment.git'
		AWS_REGION = 'us-east-1'
        AUTOSCALING_GROUP_1 = 'App1-Scaling-Group'
        AUTOSCALING_GROUP_2 = 'App2-Scaling-Group'
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
                    // def latestZipFile = sh(returnStdout: true, script: 'git ls-files -t "*.zip" | head -n1').trim()
                    def latestZipFile = sh(returnStdout: true, script: "git ls-files --full-name '*.zip' | sort -rk2,3 | awk 'NR==1{print \$NF}'").trim()
                    // def latestZipFile = sh(returnStdout: true, script: "git ls-files --full-name '*.zip' | sort -rk2 | awk 'NR==1{print $NF}'").trim()

                    // Install AWS CLI if not already installed
                    // sh 'apt-get update && apt-get install -y awscli'
                    
                    // Authenticate AWS CLI
                    sh 'aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID'
                    sh 'aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY'
                    
                    // Copy the latest zip file to S3 bucket
                    sh "aws s3 cp $latestZipFile s3://$S3_BUCKET"
                }
            }
        }
		stage('Instance Refresh') {
            steps {
					// Wait for 3 seconds before refreshing the instances
					sleep 3

					// Refresh the instances in the first autoscaling group
					withAWS(region: AWS_REGION) {
						sh "aws autoscaling start-instance-refresh --auto-scaling-group-name ${AUTOSCALING_GROUP_1} --preferences 'MinHealthyPercentage=100, InstanceWarmup=300, SkipMatching=False'"
					}

					// Refresh the instances in the second autoscaling group
					withAWS(region: AWS_REGION) {
						sh "aws autoscaling start-instance-refresh --auto-scaling-group-name ${AUTOSCALING_GROUP_2} --preferences 'MinHealthyPercentage=100, InstanceWarmup=300, SkipMatching=False'"
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
