pipeline {
    agent any

    stages {
        stage('Download') {
            steps {
                build job: 'Download', wait: true
            }
        }
        
        stage('Train') {
            steps {
                build job: 'Train', wait: true
            }
        }
        
        stage('Deploy') {
            steps {
                build job: 'Deploy', wait: false
            }
        }
        
        stage('Healthy') {
            steps {
                build job: 'Healthy', wait: true
            }
        }
    }
}
