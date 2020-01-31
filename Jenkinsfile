// Jenkinsfile test

pipeline {
    agent none 
    stages {
        stage('Build') { 
            agent {
                docker {
                    image 'conda/miniconda3:latest' 
                }
            }
            steps {        
                sh 'conda --version'
            }
        }
    }
}