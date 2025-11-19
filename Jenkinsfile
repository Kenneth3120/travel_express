@Library('jenkins-devops-cicd-library')
import groovy.json.*

pipeline {
    agent {
        label 'windows-2016-tcoe-pool'  // Use appropriate Windows agent label
    }
    
    environment {
        // Credentials for Dynatrace login
        arti_creds = credentials('eldapssouser')  // Replace with your credential ID
        USERNAME = "${arti_creds_USR}"
        PASSWORD = "${arti_creds_PSW}"
        
        // Email recipients (optional - can be hardcoded in Python script)
        email_to_recipients = 'kenneth.rebello@asia.bnpparibas.com'
        // Add CC recipients if needed
        // email_cc_recipients = 'user1@bnpparibas.com, user2@bnpparibas.com'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Verify Checkout') {
            steps {
                script {
                    powershell '''
                        $workspacePath = "$env:WORKSPACE"
                        Write-Output "Listing contents of workspace: $workspacePath"
                        Get-ChildItem -Path $workspacePath
                    '''
                    powershell '''
                        $workspacePath = "$env:WORKSPACE"
                        if (-not (Test-Path -Path "$workspacePath\\requirements.txt")) {
                            Write-Error "requirements.txt not found in the workspace!"
                            exit 1
                        }
                        if (-not (Test-Path -Path "$workspacePath\\.env")) {
                            Write-Warning ".env file not found. Will use Jenkins credentials."
                        }
                    '''
                }
            }
        }
        
        // Download Edge driver
        stage('Download Edge Driver') {
            steps {
                dir("${env.WORKSPACE_TMP}\\downloads") {
                    withCredentials([string(credentialsId: 'articredtkn', variable: 'ARTI_CRED_TKN')]) {
                        powershell '''
                            $version = (Get-Item "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe").VersionInfo.FileVersion
                            $downloadUrl = "https://artifactory.cib.echonet/artifactory/edgedriver-generic-remote/$version/edgedriver_win64.zip"
                            $headers = @{ Authorization = "Bearer $env:ARTI_CRED_TKN" }
                            Write-Host "Downloading Edge driver from: $downloadUrl"
                            Invoke-WebRequest -Uri $downloadUrl -OutFile "edgedriver_win64.zip" -Headers $headers
                        '''
                    }
                }
            }
        }
        
        stage('Extract Edge Driver') {
            steps {
                dir("${env.WORKSPACE_TMP}\\edgedriver") {
                    unzip zipFile: "${env.WORKSPACE_TMP}\\downloads\\edgedriver_win64.zip", dir: '.'
                }
            }
        }
        
        stage('Set Edge Driver Path') {
            steps {
                script {
                    def msedgedriverPath = "${env.WORKSPACE_TMP}\\edgedriver"
                    
                    // Find the actual msedgedriver.exe file
                    def driverExePath = powershell(script: """
                        Get-ChildItem -Path '${msedgedriverPath}' -Filter 'msedgedriver.exe' -Recurse | Select-Object -First 1 -ExpandProperty FullName
                    """, returnStdout: true).trim()
                    
                    if (driverExePath) {
                        env.MS_EDGE_DRIVER_PATH = driverExePath
                        echo "Edge driver found at: ${env.MS_EDGE_DRIVER_PATH}"
                    } else {
                        error "msedgedriver.exe not found in ${msedgedriverPath}"
                    }
                }
            }
        }
        
        stage('Configure Pip and Install Requirements') {
            steps {
                script {
                    withCredentials([string(credentialsId: "towerppipusr", variable: 'ARTI_CRED_TKN_USR')]) {
                        withCredentials([string(credentialsId: 'articredtkn', variable: 'ARTI_CRED_TKN')]) {
                            powershell '''
                                $WarningPreference = "SilentlyContinue"
                                $ErrorActionPreference = "Continue"
                                
                                # Configure pip for artifactory
                                $artitknuser = "$env:ARTI_CRED_TKN_USR"
                                $artitkn = "$env:ARTI_CRED_TKN"
                                pip config set global.trusted-host "artifactory.cib.echonet"
                                pip config set global.index-url "https://${artitknuser}:${artitkn}@artifactory.cib.echonet/artifactory/api/pypi/pypi/simple/"
                                
                                # Create virtual environment
                                python -m venv sodvenv
                                
                                # Activate and install requirements
                                .\\sodvenv\\Scripts\\activate
                                python -m ensurepip
                                pip install --upgrade pip
                                pip install -r requirements.txt
                                
                                Write-Output "Python packages installed successfully"
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Execute SOD Automation Script') {
            steps {
                script {
                    def pspyoutput = powershell(script: """
                        \$WarningPreference = "SilentlyContinue"
                        \$ErrorActionPreference = "Continue"
                        
                        # Set environment variables for Python script
                        \$env:USERNAME = "${env.USERNAME}"
                        \$env:PASSWORD = '${env.PASSWORD}'
                        \$env:MS_EDGE_DRIVER_PATH = "${env.MS_EDGE_DRIVER_PATH}"
                        
                        # Activate virtual environment
                        .\\sodvenv\\Scripts\\activate
                        
                        # Run the SOD automation script
                        Write-Output "Starting SOD Automation..."
                        python SOD_Automation.py
                        
                        # Deactivate virtual environment
                        .\\sodvenv\\Scripts\\deactivate
                    """, returnStdout: true).trim()
                    
                    echo "Python script output:\\n${pspyoutput}"
                    env.SOD_AUTOMATION_OUTPUT = pspyoutput
                }
            }
        }
        
        stage('Parse Status and Set Mail Subject') {
            steps {
                script {
                    def DATE_TAG = powershell(script: '''
                        (Get-Date).ToString('dd MMMM yyyy')
                    ''', returnStdout: true).trim()
                    echo "DATE_TAG: ${DATE_TAG}"
                    
                    def dayofweek = powershell(script: '''
                        (Get-Date).DayOfWeek.ToString()
                    ''', returnStdout: true).trim()
                    echo "Day of week: ${dayofweek}"
                    
                    def pspyoutput = env.SOD_AUTOMATION_OUTPUT
                    
                    // Extract status from Python output
                    def statusLine = pspyoutput.tokenize('\n').find { it.startsWith('STATUS :') }?.trim()
                    def status = statusLine?.split(':')[1]?.trim() ?: 'UNKNOWN'
                    echo "Extracted Status: ${status}"
                    
                    // Set mail subject based on day of week
                    if (dayofweek == 'Monday') {
                        env.MAIL_SUBJECT = "FTS Scheduling SOW ${DATE_TAG} - ${status}"
                    } else {
                        env.MAIL_SUBJECT = "FTS Scheduling SOD ${DATE_TAG} - ${status}"
                    }
                    echo "Email Subject: ${env.MAIL_SUBJECT}"
                    
                    // Store status for post actions
                    env.SOD_STATUS = status
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "Archiving artifacts and cleaning up..."
                
                // Archive screenshot if it exists
                if (fileExists('Screenshots/screenshot.png')) {
                    archiveArtifacts artifacts: 'Screenshots/screenshot.png', allowEmptyArchive: true
                    echo "Screenshot archived successfully"
                } else {
                    echo "Warning: Screenshot not found at Screenshots/screenshot.png"
                }
                
                // Archive HTML email report if it exists
                if (fileExists('SOD_Email_Report.html')) {
                    archiveArtifacts artifacts: 'SOD_Email_Report.html', allowEmptyArchive: true
                    echo "Email report archived successfully"
                }
                
                // Clean workspace but keep important files
                cleanWs deleteDirs: true, patterns: [
                    [pattern: '.env', type: 'EXCLUDE'],
                    [pattern: 'requirements.txt', type: 'EXCLUDE']
                ]
            }
        }
        
        success {
            script {
                echo "=========================================="
                echo "SOD Automation Job Completed Successfully"
                echo "Status: ${env.SOD_STATUS}"
                echo "Subject: ${env.MAIL_SUBJECT}"
                echo "Email sent via Outlook from Python script"
                echo "=========================================="
            }
        }
        
        failure {
            script {
                echo "=========================================="
                echo "SOD Automation Job FAILED"
                echo "=========================================="
                
                // Optional: Send failure notification email
                // Uncomment if you want Jenkins to send failure emails
                /*
                mail(
                    to: "${env.email_to_recipients}",
                    subject: "FAILED: ${env.MAIL_SUBJECT}",
                    body: """
                        <html>
                        <body>
                        <p>Hello,</p>
                        <p>The SOD Automation job has FAILED.</p>
                        <p><b>Error Details:</b></p>
                        <pre>${env.SOD_AUTOMATION_OUTPUT}</pre>
                        <p>Please check the Jenkins console output for more details.</p>
                        <p>Regards,<br>Scheduling Team</p>
                        </body>
                        </html>
                    """,
                    mimeType: "text/html"
                )
                */
            }
        }
        
        aborted {
            script {
                echo "SOD Automation Job was Aborted"
            }
        }
    }
}