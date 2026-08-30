pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "thereserita02/meditrack:latest"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'dev',
                url: 'https://github.com/Rita02-brad/meditrack-devops.git'
            }
        }

        stage('Test') {
            steps {
                sh 'pip3 install -r requirements.txt'
                sh 'python3 -m pytest test_app.py'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $DOCKER_IMAGE .'
            }
        }

        stage('Push To Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {

                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                    sh 'docker push $DOCKER_IMAGE'
                }
            }
        }
    }
}
