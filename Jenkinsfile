pipeline {
    agent any  // Запускаем на любом доступном агенте
    
    environment {
        // Основные переменные окружения
        REPO_URL = 'https://github.com/ryabov3/mlflow_project.git'
        BRANCH = 'main'  // или 'master' в зависимости от вашего репозитория
        CREDENTIALS_ID = 'jenkins-github-ssh'  // ID ваших SSH-ключей в Jenkins
        PYTHON = 'python3'  // Используемая версия Python
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')  // Таймаут сборки
        retry(1)  // Количество попыток перезапуска при ошибке
        disableConcurrentBuilds()  // Запрещаем параллельные сборки
    }
    
    stages {
        // Этап 1: Получение кода из репозитория
        stage('Checkout') {
            steps {
                script {
                    try {
                        checkout([
                            $class: 'GitSCM',
                            branches: [[name: "*/${env.BRANCH}"]],
                            userRemoteConfigs: [[
                                url: "${env.REPO_URL}",
                                credentialsId: "${env.CREDENTIALS_ID}"
                            ]],
                            extensions: [
                                [$class: 'CleanBeforeCheckout'],
                                [$class: 'CloneOption', timeout: 60]
                            ]
                        ])
                    } catch (Exception e) {
                        error "Ошибка при получении кода: ${e.message}"
                    }
                }
            }
        }
        
        // Этап 2: Установка зависимостей Python
        stage('Install Dependencies') {
            steps {
                script {
                    try {
                        // Проверка наличия pip
                        sh '''
                            if ! python3.12 -m pip --version; then
                                echo "Установка pip для Python 3.12..."
                                curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
                                python3.12 get-pip.py
                            fi
                        '''
                        
                        // Установка зависимостей
                        sh '''
                            python3.12 -m pip install --upgrade pip
                            python3.12 -m pip install -r requirements.txt
                        '''
                    } catch (Exception e) {
                        error "Ошибка установки зависимостей: ${e.message}"
                    }
                }
            }
        }
        
        // Этап 4: Обучение модели
        stage('Train Model') {
            steps {
                script {
                    try {
                        // Проверяем существование MLflow сервера
                        sh """
                            if ! nc -z 127.0.0.1 5000; then
                                echo "MLflow server не запущен на 127.0.0.1:5000"
                            fi
                        """
                        
                        // Запускаем обучение
                        sh "${env.PYTHON} train.py"
                        
                        // Проверяем, что модель создана
                        sh "test -f model.pkl || exit 1"
                    } catch (Exception e) {
                        error "Ошибка обучения модели: ${e.message}"
                    }
                }
            }
        }
        
        // Этап 5: Запуск сервиса
        stage('Deploy Service') {
            steps {
                script {
                    try {
                        // Останавливаем предыдущий сервис, если запущен
                        sh 'pkill -f "python.*serve.py" || true'
                        
                        // Запускаем сервис в фоновом режиме
                        sh "nohup ${env.PYTHON} serve.py > server.log 2>&1 &"
                        
                        // Ждем запуска сервиса
                        sleep(time: 10, unit: 'SECONDS')
                    } catch (Exception e) {
                        error "Ошибка запуска сервиса: ${e.message}"
                    }
                }
            }
        }
        
        // Этап 6: Тестирование сервиса
        stage('Test Service') {
            steps {
                script {
                    try {
                        // Подготовка тестовых данных
                        def testData = '''
                        {
                            "hours_studied": 6,
                            "previous_scores": 85,
                            "sleep_hours": 7,
                            "sample_papers": 2,
                            "extracurricular": 1
                        }
                        '''
                        
                        // Отправка тестового запроса
                        def response = sh(
                            script: """
                                curl -s -X POST http://localhost:5001/predict \
                                -H "Content-Type: application/json" \
                                -d '${testData}'
                            """,
                            returnStdout: true
                        )
                        
                        // Проверка ответа
                        if (!response.contains('prediction')) {
                            error "Некорректный ответ от сервиса: ${response}"
                        }
                        
                        echo "Тестовый запрос успешен. Ответ: ${response}"
                    } catch (Exception e) {
                        error "Ошибка тестирования сервиса: ${e.message}"
                    }
                }
            }
        }
    }
    
    post {
        // Действия после успешного выполнения
        success {
            echo 'Pipeline успешно завершен!'
            slackSend(color: 'good', message: "Pipeline успешно завершен: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
        
        // Действия при неудачном выполнении
        failure {
            echo 'Pipeline завершился с ошибкой!'
            slackSend(color: 'danger', message: "Pipeline завершился с ошибкой: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
            
            // Архивируем логи для анализа
            archiveArtifacts artifacts: '**/*.log', allowEmptyArchive: true
        }
        
        // Действия в любом случае
        always {
            echo 'Завершение выполнения Pipeline'
            
            // Очистка
            sh 'pkill -f "python.*serve.py" || true'
        }
    }
}
