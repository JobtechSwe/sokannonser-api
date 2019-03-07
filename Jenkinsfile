pipeline {
    agent any
    environment {
        scannerHome = tool 'Jobtech_Sokapi_SonarScanner'
        version = "1"
        buildTag = "${version}.${BUILD_NUMBER}"
    }
    stages{
        stage('Checkout code'){
            agent any
            steps{
                checkout scm: [
                    $class: 'GitSCM'
                ]               
            }
        }
        stage('Code analysis'){
            agent any
            steps {
                withSonarQubeEnv('Jobtech_SonarQube_Server'){
                sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=sokapi -Dsonar.sources=."
                }
            }
        }
        stage('Build and Tag Openshift Image'){
            agent any
            steps{
                openshiftBuild(namespace:'${openshiftProject}', bldCfg: 'sokapi', showBuildLogs: 'true')
                openshiftTag(namespace:'${openshiftProject}', srcStream: 'sokapi', srcTag: 'latest', destStream: 'sokapi', destTag:'${buildTag}')
            }
        }
        stage('Deploy to Staging'){
            agent any
            when{
                environment name: 'GIT_BRANCH', value: 'jenkins'
            }
            steps{
                sh "oc set image dc/staging-sokapi staging-sokapi=docker-registry.default.svc:5000/${openshiftProject}/sokapi:${buildTag} -n ${openshiftProject}"
                openshiftDeploy(depCfg: 'staging-sokapi', namespace: '${openshiftProject}', verbose: 'false', waitTime: '', waitUnit: 'sec')
                openshiftVerifyDeployment(depCfg: 'staging-sokapi', namespace: '${openshiftProject}', replicaCount: '1', verbose: 'false', verifyReplicaCount: 'false', waitTime: '15', waitUnit: 'sec')
            }
        }
        stage('Deploy to Prod?'){
            agent none
            when{
                environment name: 'GIT_BRANCH', value: 'jenkins'
            }
            steps{
                input "Deploy to prod"
            }
        }
        stage('Final Deploy'){
            agent any
            steps{
                sh "oc set image dc/sokapi sokapi=docker-registry.default.svc:5000/${openshiftProject}/sokapi:${buildTag} -n ${openshiftProject}"
                openshiftDeploy(depCfg: 'sokapi', namespace: '${openshiftProject}', verbose: 'false', waitTime: '', waitUnit: 'sec')
                openshiftVerifyDeployment(depCfg: 'sokapi', namespace: '${openshiftProject}', replicaCount: '1', verbose: 'false', verifyReplicaCount: 'false', waitTime: '15', waitUnit: 'sec')
            }
        }
    }
    post {
        success {
            sh 'echo "success"'
            //slackSend color: 'good', message: "${GIT_URL}, Branch: ${GIT_BRANCH}, Commit: ${GIT_COMMIT} successfully built to project ${openshiftProject} build: ${buildTag}."
        }
        failure {
            sh 'echo "fail"'
            //slackSend color: 'bad', channel: '#narval-sokapi', message: "${GIT_URL} ${GIT_BRANCH} ${GIT_COMMIT} failed to build to ${openshiftProject} build ${buildTag}."
        }
        unstable {
            sh 'echo "unstable"'
            //slackSend color: 'bad', message: "${GIT_URL} ${GIT_BRANCH} ${GIT_COMMIT} unstable build for ${openshiftProject} build ${buildTag}."
        }
    }
}

// The rest is preserved for future use

  // // Run Unit Tests on Development Environment.
  // //stage('Dev Env Unit Tests') {
  //   //echo "Running Dev Unit Tests"
  //   //sh "python -m pytest -svv -ra -m unit tests/"
  // //}

  // // Run Unit Tests on Development Environment.
  // //stage('Dev Env Integration Tests') {
  //   //echo "Running Dev Integration Tests"
  //   //sh "python -m pytest -svv -ra -m integration tests/"
  // //}

  //  // Deploy the built image to the Test Environment.
  // //stage('Deploy to Test env') {
  //   //echo "Deploying image to Test Env Project"

  //     // Update the Image on the Development Deployment Config
  //     sh "oc set image dc/sokapi sokapi=docker-registry.default.svc:5000/jt-dev/sokapi:${devTag} -n jt-test"

  //     // Deploy the test application.
  //     openshiftDeploy depCfg: 'sokapi', namespace: 'jt-test', verbose: 'false', waitTime: '', waitUnit: 'sec'
  //     openshiftVerifyDeployment depCfg: 'sokapi', namespace: 'jt-test', replicaCount: '1', verbose: 'false', verifyReplicaCount: 'false', waitTime: '', waitUnit: 'sec'
  // }

  // // Run Integration Tests on Test Environment.
  // stage('Test Env Integration Tests') {
  //   echo "Running Test env Integration Tests"
  //   sh "python -m pytest -svv -ra -m integration tests/"
  // }

  // A/B Deployment into Production
  // -------------------------------------
  // Do not activate the new version yet.
  // stage('A/B Production Deployment') {
  //       input "Deploy to Production?"
  //       // Update the Image on the Production Deployment Config B
  //       sh "oc set image dc/sokapi-b sokapi-b=docker-registry.default.svc:5000/jt-dev/sokapi:${devTag} -n jt-prod"

  //       // Deploy B the inactive application.
  //       openshiftDeploy depCfg: 'sokapi-b', namespace: 'jt-prod', verbose: 'false', waitTime: '', waitUnit: 'sec'
  //       openshiftVerifyDeployment depCfg: 'sokapi-b', namespace: 'jt-prod', replicaCount: '1', verbose: 'false', verifyReplicaCount: 'true', waitTime: '', waitUnit: 'sec'

  //       input "Deploy to SOKAPI-A Production?"
  //       echo "Dploying to SOKAPI-A"
  //       // Update the Image on the Production Deployment Config A
  //       sh "oc set image dc/sokapi-a sokapi-a=docker-registry.default.svc:5000/jt-dev/sokapi:${devTag} -n jt-prod"

  //       // Deploy A the inactive application.
  //       sh "oc tag jt-dev/sokapi:${devTag} jt-prod/sokapi:${prodTag} -n jt-prod"
  //       openshiftDeploy depCfg: 'sokapi-a', namespace: 'jt-prod', verbose: 'false', waitTime: '', waitUnit: 'sec'
  //       openshiftVerifyDeployment depCfg: 'sokapi-a', namespace: 'jt-prod', replicaCount: '1', verbose: 'false', verifyReplicaCount: 'true', waitTime: '', waitUnit: 'sec'

    //   }


