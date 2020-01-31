// Jenkinsfile

pipeline {
    agent none 
    stages {
        stage('Build environment') { 
            agent {
                docker {
                    image 'conda/miniconda3:latest' 
                }
            }
            // steps {
            //     sh 'python -m py_compile 3_simple-python-pyinstaller-app/sources/add2vals.py 3_simple-python-pyinstaller-app/sources/calc.py' 
            // }
        }
        // stage('Test') {
        //     agent {
        //         docker {
        //             image 'qnib/pytest'
        //         }
        //     }
        //     steps {
        //         sh 'py.test --verbose --junit-xml test-reports/results.xml 3_simple-python-pyinstaller-app/sources/test_calc.py'
        //     }
        //     post {
        //         always {
        //             junit 'test-reports/results.xml'
        //         }
        //     }
        // }
        // stage('Deliver') {
        //     agent {
        //         docker {
        //             image 'cdrx/pyinstaller-linux:python2'
        //         }
        //     }
        //     steps {
        //         sh 'pyinstaller --onefile 3_simple-python-pyinstaller-app/sources/add2vals.py'
        //     }
        //     post {
        //         success {
        //             archiveArtifacts 'dist/add2vals'
        //         }
            // }
        // }
    }
}