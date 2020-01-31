// Jenkinsfile test

pipeline {
    agent none 
    stages {
        stage('Build environment') { 
            agent {
                docker {
                    image 'conda/miniconda3:latest' 
                }
            }
        }
    }
}