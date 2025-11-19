@Library('jenkins-devops-cicd-library')
import groovy.json.*

pipeline {
    agent {
        label 'windows-2016-tcoe-pool'
    }
    
    environment {
        // Credentials for Dynatrace login
        arti_creds = credentials('eldapssouser')
        USERNAME = "${arti_creds_USR}"
        PASSWORD = "${arti_creds_PSW}"
        
        // Email recipients
        email_to_recipients = 'kenneth.rebello@asia.bnpparibas.com'
        // Add CC recipients if needed:
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
                        if (-not (Test-Path -Path "$workspacePath\\sod_automation.py")) {
                            Write-Error "sod_automation.py not found in the workspace!"
                            exit 1
                        }
                    '''
                }
            }
        }
        
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
                    powershell '''
                        $WarningPreference = "SilentlyContinue"
                        $ErrorActionPreference = "Continue"
                        
                        Write-Output "Creating virtual environment..."
                        python -m venv sodvenv
                        
                        Write-Output "Activating virtual environment..."
                        .\\sodvenv\\Scripts\\activate
                        
                        Write-Output "Upgrading pip..."
                        python -m pip install --upgrade pip
                        
                        Write-Output "Installing requirements..."
                        pip install -r requirements.txt
                        
                        Write-Output "Installed packages:"
                        pip list
                        
                        Write-Output "Python packages installed successfully"
                    '''
                }
            }
        }
        
        stage('Execute SOD Automation Script') {
            steps {
                script {
                    def pspyoutput = powershell(script: """
                        \$WarningPreference = "SilentlyContinue"
                        \$ErrorActionPreference = "Continue"
                        
                        # Set environment variables
                        \$env:USERNAME = "${env.USERNAME}"
                        \$env:PASSWORD = '${env.PASSWORD}'
                        \$env:MS_EDGE_DRIVER_PATH = "${env.MS_EDGE_DRIVER_PATH}"
                        
                        # Activate virtual environment
                        .\\sodvenv\\Scripts\\activate
                        
                        # Run the SOD automation script
                        Write-Output "Starting SOD Automation..."
                        python sod_automation.py
                        
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
                echo "=========================================="
                echo "Archiving artifacts and sending email..."
                echo "=========================================="
                
                // Archive screenshot
                if (fileExists('Screenshots/screenshot.png')) {
                    archiveArtifacts artifacts: 'Screenshots/screenshot.png', allowEmptyArchive: true
                    echo "✓ Screenshot archived successfully"
                } else {
                    echo "⚠ Warning: Screenshot not found at Screenshots/screenshot.png"
                }
                
                // Archive HTML email report
                if (fileExists('SOD_Email_Report.html')) {
                    archiveArtifacts artifacts: 'SOD_Email_Report.html', allowEmptyArchive: true
                    echo "✓ Email report archived successfully"
                } else {
                    echo "⚠ Warning: Email report not found"
                }
                
                // Read the HTML report content for email
                def emailBody = ""
                if (fileExists('SOD_Email_Report.html')) {
                    emailBody = readFile('SOD_Email_Report.html')
                    echo "✓ Email report content loaded"
                }
                
                // Send email via Jenkins
                if (emailBody) {
                    try {
                        mail(
                            to: "${env.email_to_recipients}",
                            // Uncomment below to add CC recipients:
                            // cc: "${env.email_cc_recipients}",
                            subject: "${env.MAIL_SUBJECT}",
                            body: emailBody,
                            mimeType: "text/html"
                        )
                        echo "✓ Email sent successfully to: ${env.email_to_recipients}"
                        echo "  Subject: ${env.MAIL_SUBJECT}"
                    } catch (Exception e) {
                        echo "✗ Failed to send email: ${e.message}"
                    }
                } else {
                    echo "✗ No email report content found - skipping email"
                }
                
                // Clean workspace but keep important files
                cleanWs deleteDirs: true, patterns: [
                    [pattern: '.env', type: 'EXCLUDE'],
                    [pattern: 'requirements.txt', type: 'EXCLUDE'],
                    [pattern: 'sod_automation.py', type: 'EXCLUDE']
                ]
                
                echo "=========================================="
            }
        }
        
        success {
            script {
                echo ""
                echo "=========================================="
                echo "✓ SOD AUTOMATION COMPLETED SUCCESSFULLY"
                echo "=========================================="
                echo "Status: ${env.SOD_STATUS}"
                echo "Subject: ${env.MAIL_SUBJECT}"
                echo "Email sent via Jenkins to: ${env.email_to_recipients}"
                echo "Build artifacts archived"
                echo "=========================================="
                echo ""
            }
        }
        
        failure {
            script {
                echo ""
                echo "=========================================="
                echo "✗ SOD AUTOMATION JOB FAILED"
                echo "=========================================="
                
                // Send failure notification email
                try {
                    mail(
                        to: "${env.email_to_recipients}",
                        subject: "FAILED: FTS Scheduling SOD - Build #${env.BUILD_NUMBER}",
                        body: """
                            <html>
                            <body style="font-family: Arial, sans-serif;">
                            <h2 style="color: red;">⚠ SOD Automation Job FAILED</h2>
                            <p>The SOD automation script encountered an error and could not complete.</p>
                            <p><b>Build Number:</b> #${env.BUILD_NUMBER}</p>
                            <p><b>Build URL:</b> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                            <p><b>Console Output:</b> <a href="${env.BUILD_URL}console">View Console</a></p>
                            <p>Please check the console output for error details.</p>
                            <hr>
                            <p><b>Thanks and Regards,</b><br>
                            Scheduling Team<br>
                            BNP Paribas CIB IT Production</p>
                            </body>
                            </html>
                        """,
                        mimeType: "text/html"
                    )
                    echo "✓ Failure notification email sent"
                } catch (Exception e) {
                    echo "✗ Failed to send failure notification: ${e.message}"
                }
                
                echo "=========================================="
                echo ""
            }
        }
        
        aborted {
            script {
                echo ""
                echo "=========================================="
                echo "⚠ SOD Automation Job was Aborted"
                echo "=========================================="
                echo ""
            }
        }
    }
}