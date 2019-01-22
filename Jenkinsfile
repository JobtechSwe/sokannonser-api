#!groovy

// Run this pipeline on the custom Jenkins Slave ('jobtech-appdev')
// Jenkins Slaves have JDK and Maven already installed
// 'jobtech-appdev' has skopeo installed as well.
node('jobtech-appdev'){

  // The following variables need to be defined at the top level and not inside the scope of a stage - otherwise they would not be accessible from other stages.
  def version    = "1"
  //def chechoutDir = "/tmp/workspace/sokapi-pipeline"

  // Set the tag for the development image: version + build number
  def jenkinsTag  = "${version}-${BUILD_NUMBER}"
  
    def commitHash = ''
    def branch = ''

  // Checkout Source Code
  stage('Checkout Source') {
    def scmVars = checkout scm
    echo "Branch: ${scmVars.GIT_BRANCH}"
    echo "Commit Hash: ${scmVars.GIT_COMMIT}"
    commitHash = "${scmVars.GIT_COMMIT}"
    branch = "${scmVars.GIT_BRANCH}"
  }
  echo "Commithash: ${commitHash}"
    def devTag = "${jenkinsTag}"
  // Call SonarQube for Code Analysis
  stage('Code Analysis') {
    echo "Running Code Analysis"
    // requires SonarQube Scanner 2.8+
    def scannerHome = tool 'Jobtech_Sokapi_SonarScanner';
    echo "Scanner Home: ${scannerHome}"
    ////sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=jobtech_sokapi -Dsonar.sources=. -Dsonar.host.url=http://sonarqube-jt-sonarqube.dev.services.jtech.se -Dsonar.login=${sonarqube_token}"
    withSonarQubeEnv('Jobtech_SonarQube_Server') {
      sh "${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=sokapi_sonar -Dsonar.sources=."
    }
  }

  // Build the OpenShift Image in OpenShift, tag and pus to nexus.
  stage('Build and Tag OpenShift Image') {
    echo "Building OpenShift container image sokapi:${devTag}"

    // Start Binary Build in OpenShift using the file we just published
    sh "oc start-build sokapi -n ${openshiftProject} --follow"

    //sh "oc new-app jt-dev/sokapi:${devTag} --name=sokapi --allow-missing-imagestream-tags=true -n jt-dev"
    //sh "oc set triggers dc/sokapi --remove-all -n jt-dev"

    // Tag the image using the devTag
    sh "oc tag ${openshiftProject}/sokapi:latest ${openshiftProject}/sokapi:${devTag} -n ${openshiftProject}"

    //echo "Publish to Nexus sokapi_releases repository"
    //sh "oc tag jt-dev/sokapi:latest http://nexus3-jt-nexus.dev.services.jtech.se/repository/sokapi_releases/jt-dev/sokapi:${devTag} -n jt-dev"
  }

  // Deploy the built image to the Development Environment.
  stage('Deploy to Dev Env') {
    echo "Deploying container image to Development Env Project"

    //echo "DEV ANNOTATING"
    //sh "oc annotate is jt-dev/sokapi:${devTag} dokapi.image.identifier="date" --overwrite"

    // Update the Image on the Development Deployment Config
    sh "oc set image dc/sokapi sokapi=docker-registry.default.svc:5000/${openshiftProject}/sokapi:${devTag} -n ${openshiftProject}"

      // Update the Config Map which contains the users for the Tasks application
      //sh "oc delete configmap tasks-config -n jt-dev --ignore-not-found=true"
      //sh "oc create configmap tasks-config --from-file=./configuration/application-users.properties --from-file=./configuration/application-roles.properties -n jt-dev"

      // Deploy the development application.
      echo "[openshiftDeploy]"
      openshiftDeploy depCfg: 'sokapi', namespace: '${openshiftProject}', verbose: 'false', waitTime: '', waitUnit: 'sec'
      echo "[openshiftVerifyDeployment]"
      openshiftVerifyDeployment depCfg: 'sokapi', namespace: '${openshiftProject}', replicaCount: '1', verbose: 'false', verifyReplicaCount: 'false', waitTime: '15', waitUnit: 'sec'
  }

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

}
