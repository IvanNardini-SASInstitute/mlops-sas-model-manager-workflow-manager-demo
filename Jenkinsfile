// Jenkinsfile test

pipeline {
    agent none 
    stages {
        stage('Build') { 
            agent {
                docker {
                    image 'python:2-alpine' 
                }
            }
            steps {        
                sh 'python -m py_compile project/2_jupyter_lab/experiment_rfor/score.py'
            }
        }
    }
}