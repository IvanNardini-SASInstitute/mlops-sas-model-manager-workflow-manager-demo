// Jenkinsfile testing
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
        // stage('Test') { 
        //     agent {
        //         docker {
        //             image 'qnib/pytest' 
        //         }
        //     }
        //     steps {
        //         sh 'py.test --verbose --junit-xml test-reports/results.xml project/2_jupyter_lab/experiment_rfor/score.py'
        //     }
        //     post {
        //         always {
        //             junit 'test-reports/results.xml' 
        //         }
        //     }
        // }
    }
}