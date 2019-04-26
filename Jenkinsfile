pipeline {
    agent any
    environment {
        scannerHome = tool 'Jobtech_Sokapi_SonarScanner'
        version = "1"
        buildTag = "${version}.${BUILD_NUMBER}"
    }
    stages{
        stage('Checkout code'){
            steps{
                checkout scm: [
                    $class: 'GitSCM'
                ]               
            }
        }
        stage('Code analysis'){
            steps {
                withSonarQubeEnv('Jobtech_SonarQube_Server'){
                sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=sokapi -Dsonar.sources=."
                }
            }
        }
        stage('Build and Tag Openshift Image'){
            steps{
                sh 'echo "${GIT_BRANCH}"'
                openshiftBuild(namespace:'${openshiftProject}', bldCfg: 'open-api', showBuildLogs: 'true')
                openshiftTag(namespace:'${openshiftProject}', srcStream: 'open-api', srcTag: 'latest', destStream: 'open-api', destTag:'${buildTag}')
                openshiftBuild(namespace:'${openshiftProject}', bldCfg: 'jobtechjobs-api', showBuildLogs: 'true')
                openshiftTag(namespace:'${openshiftProject}', srcStream: 'jobtechjobs-api', srcTag: 'latest', destStream: 'jobtechjobs-api', destTag:'${buildTag}')
                openshiftBuild(namespace:'${openshiftProject}', bldCfg: 'bulk-api', showBuildLogs: 'true')
                openshiftTag(namespace:'${openshiftProject}', srcStream: 'bulk-api', srcTag: 'latest', destStream: 'bulk-api', destTag:'${buildTag}')
            }
        }
        stage('Deploy to Staging'){
            when{
                environment name: 'GIT_BRANCH', value: 'origin/master'
            }
            steps{
                sh "oc set image dc/staging-sokapi staging-sokapi=docker-registry.default.svc:5000/${openshiftProject}/sokapi:${buildTag} -n ${openshiftProject}"
                openshiftDeploy(depCfg: 'staging-sokapi', namespace: '${openshiftProject}', verbose: 'false', waitTime: '', waitUnit: 'sec')
                openshiftVerifyDeployment(depCfg: 'staging-sokapi', namespace: '${openshiftProject}', replicaCount: '1', verbose: 'false', verifyReplicaCount: 'false', waitTime: '15', waitUnit: 'sec')
                slackSend color: 'good', channel: '#narval-sokapi', message: "${GIT_URL}, Branch: ${GIT_BRANCH}, Commit: ${GIT_COMMIT} successfully built to project ${openshiftProject} Staging build: ${buildTag}. You cannot build again from ${GIT_BRANCH} until build has been promoted or aborted. ${BUILD_URL}input"
            }
        }
        stage('Deploy to Prod?'){
            when{
                environment name: 'GIT_BRANCH', value: 'origin/master'
            }
            steps{
                input "Deploy to prod (You cannot build again until build has been promoted or aborted)?"
            }
        }
        stage('Final Deploy to api'){
            when{
                anyOf{
                environment name: 'GIT_BRANCH', value: 'origin/develop'
                environment name: 'GIT_BRANCH', value: 'origin/master'                   
                }
            }
            steps{
                sh 'echo "Deploying from ${GIT_BRANCH}"'
                sh "oc set image dc/open-api open-api=docker-registry.default.svc:5000/${openshiftProject}/open-api:${buildTag} -n ${openshiftProject}"
                openshiftDeploy(depCfg: 'open-api', namespace: '${openshiftProject}', verbose: 'false', waitTime: '', waitUnit: 'sec')
                openshiftVerifyDeployment(depCfg: 'open-api', namespace: '${openshiftProject}', replicaCount: '1', verbose: 'false', verifyReplicaCount: 'false', waitTime: '15', waitUnit: 'sec')
                sh "oc set image dc/jobtechjobs-api jobtechjobs-api=docker-registry.default.svc:5000/${openshiftProject}/jobtechjobs-api:${buildTag} -n ${openshiftProject}"
                openshiftDeploy(depCfg: 'jobtechjobs-api', namespace: '${openshiftProject}', verbose: 'false', waitTime: '', waitUnit: 'sec')
                openshiftVerifyDeployment(depCfg: 'jobtechjobs-api', namespace: '${openshiftProject}', replicaCount: '1', verbose: 'false', verifyReplicaCount: 'false', waitTime: '15', waitUnit: 'sec')
                sh "oc set image dc/bulk-api sokapi=docker-registry.default.svc:5000/${openshiftProject}/bulk-api:${buildTag} -n ${openshiftProject}"
                openshiftDeploy(depCfg: 'bulk-api', namespace: '${openshiftProject}', verbose: 'false', waitTime: '', waitUnit: 'sec')
                openshiftVerifyDeployment(depCfg: 'bulk-api', namespace: '${openshiftProject}', replicaCount: '1', verbose: 'false', verifyReplicaCount: 'false', waitTime: '15', waitUnit: 'sec')
            }
        }
    }
    post {
        success {
            slackSend color: 'good', message: "${GIT_URL}, Branch: ${GIT_BRANCH}, Commit: ${GIT_COMMIT} successfully built to project ${openshiftProject} build: ${buildTag}."
        }
        failure {
            slackSend color: 'FF0000', channel: '#narval-sokapi', message: "${GIT_URL} ${GIT_BRANCH} ${GIT_COMMIT} FAILED to build to ${openshiftProject} build ${buildTag}. ${BUILD_URL}console"
        }
        unstable {
            slackSend color: 'FFFF00', message: "${GIT_URL} ${GIT_BRANCH} ${GIT_COMMIT} unstable build for ${openshiftProject} build ${buildTag}. ${BUILD_URL}console"
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


