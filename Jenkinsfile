pipeline {
  agent any
  stages {
    stage('Checkout code') {
      steps {
        git(url: 'https://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@github.com/VR-SE-DB-Project/Web.git', branch: 'main', credentialsId: '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')
      }
    }

    stage('build') {
      parallel {
        stage('log') {
          environment {
            DOCKERHUB_USER = 'junjao800@gmail.com'
            DOCKERHUB_PASSWORD = 'JUNjao0972958325'
          }
          steps {
            sh '''ls -la
docker login -u $DOCKERHUB_USER -p $DOCKERHUB_PASSWORD'''
          }
        }

        stage('Build and Push Docker Images') {
          environment {
            imageTag = 'sachimiji/vracer:latest'
          }
          steps {
            script {
              sh './restart_docker.sh'
              echo 'Build and push done'
            }

          }
        }

      }
    }

    stage('check docker') {
      parallel {
        stage('check docker') {
          steps {
            sh '''docker ps -a


'''
          }
        }

        stage('error') {
          steps {
            sh '''
docker logs web_main_web_1

docker logs web_main_db_1
'''
          }
        }

        stage('checke db') {
          steps {
            sh '''docker exec web_main_db_1 id postgres



'''
          }
        }

      }
    }

  }
  environment {
    DOCKER_HOST = 'unix:///var/run/docker.sock'
  }
}