pipeline {
    agent any
    
    environment {
        PYTHON = 'python3.12'
    }
    
    stages {
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Download and Preprocess Data') {
            steps {
                sh '${PYTHON} download.py'
            }
        }
        
        stage('Train Model') {
            steps {
                sh '${PYTHON} train.py'
            }
        }
        
        stage('Deploy Model') {
            steps {
                sh 'nohup ${PYTHON} serve.py > server.log 2>&1 &'
                echo 'Model service started on port 5001'
            }
        }
        
        stage('Test Service') {
            steps {
                script {
                    sleep(time: 5, unit: 'SECONDS')  # Даем сервису время запуститься
                    
                    // Пример тестового запроса
                    def test_data = '''
                    {
                        "hours_studied": 6,
                        "previous_scores": 85,
                        "sleep_hours": 7,
                        "sample_papers": 2,
                        "extracurricular": 1
                    }
                    '''
                    
                    def response = sh(script: """
                        curl -X POST http://localhost:5001/predict \
                        -H "Content-Type: application/json" \
                        -d '${test_data}' | python -m json.tool
                    """, returnStdout: true)
                    
                    echo "Service response: ${response}"
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed'
        }
    }
}
