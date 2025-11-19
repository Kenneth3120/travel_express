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
        // Uncomment to add CC recipients:
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
                        Write-Output "==================================="
                        Write-Output "Workspace: $workspacePath"
                        Write-Output "==================================="
                        Get-ChildItem -Path $workspacePath | Format-Table Name, Length, LastWriteTime
                    '''
                    powershell '''
                        $workspacePath = "$env:WORKSPACE"
                        
                        # Check for required files
                        $requiredFiles = @("requirements.txt", "sod_automation.py")
                        $missingFiles = @()
                        
                        foreach ($file in $requiredFiles) {
                            if (-not (Test-Path -Path "$workspacePath\\$file")) {
                                $missingFiles += $file
                            }
                        }
                        
                        if ($missingFiles.Count -gt 0) {
                            Write-Error "Missing required files: $($missingFiles -join ', ')"
                            exit 1
                        }
                        
                        Write-Output "✓ All required files present"
                    '''
                }
            }
        }
        
        stage('Download Edge Driver') {
            steps {
                dir("${env.WORKSPACE_TMP}\\downloads") {
                    withCredentials([string(credentialsId: 'articredtkn', variable: 'ARTI_CRED_TKN')]) {
                        powershell '''
                            Write-Output "Detecting Edge version..."
                            $version = (Get-Item "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe").VersionInfo.FileVersion
                            Write-Output "Edge version: $version"
                            
                            $downloadUrl = "https://artifactory.cib.echonet/artifactory/edgedriver-generic-remote/$version/edgedriver_win64.zip"
                            $headers = @{ Authorization = "Bearer $env:ARTI_CRED_TKN" }
                            
                            Write-Output "Downloading Edge driver from: $downloadUrl"
                            Invoke-WebRequest -Uri $downloadUrl -OutFile "edgedriver_win64.zip" -Headers $headers
                            Write-Output "✓ Edge driver downloaded"
                        '''
                    }
                }
            }
        }
        
        stage('Extract Edge Driver') {
            steps {
                dir("${env.WORKSPACE_TMP}\\edgedriver") {
                    unzip zipFile: "${env.WORKSPACE_TMP}\\downloads\\edgedriver_win64.zip", dir: '.'
                    powershell '''
                        Write-Output "✓ Edge driver extracted"
                        Get-ChildItem -Recurse | Format-Table Name, Length
                    '''
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
                        echo "✓ Edge driver found at: ${env.MS_EDGE_DRIVER_PATH}"
                    } else {
                        error "✗ msedgedriver.exe not found in ${msedgedriverPath}"
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
                        
                        Write-Output "==================================="
                        Write-Output "Python Environment Setup"
                        Write-Output "==================================="
                        
                        Write-Output "Python version:"
                        python --version
                        
                        Write-Output "`nCreating virtual environment..."
                        python -m venv sodvenv
                        
                        Write-Output "Activating virtual environment..."
                        .\\sodvenv\\Scripts\\activate
                        
                        Write-Output "Upgrading pip..."
                        python -m pip install --upgrade pip --quiet
                        
                        Write-Output "`nInstalling requirements..."
                        pip install -r requirements.txt
                        
                        Write-Output "`nInstalled packages:"
                        pip list
                        
                        Write-Output "`n✓ Python environment ready"
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
                        
                        Write-Output "==================================="
                        Write-Output "Executing SOD Automation Script"
                        Write-Output "==================================="
                        
                        # Set environment variables
                        \$env:USERNAME = "${env.USERNAME}"
                        \$env:PASSWORD = '${env.PASSWORD}'
                        \$env:MS_EDGE_DRIVER_PATH = "${env.MS_EDGE_DRIVER_PATH}"
                        
                        # Activate virtual environment
                        .\\sodvenv\\Scripts\\activate
                        
                        # Run the SOD automation script
                        python sod_automation.py
                        
                        # Deactivate virtual environment
                        .\\sodvenv\\Scripts\\deactivate
                        
                        Write-Output "`n==================================="
                        Write-Output "Script Execution Complete"
                        Write-Output "==================================="
                    """, returnStdout: true).trim()
                    
                    echo "Script Output:\n${pspyoutput}"
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
                    echo "Date: ${DATE_TAG}"
                    
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
                echo ""
                echo "==================================="
                echo "POST BUILD ACTIONS"
                echo "==================================="
                
                // Archive screenshot
                if (fileExists('Screenshots/screenshot.png')) {
                    archiveArtifacts artifacts: 'Screenshots/screenshot.png', allowEmptyArchive: true
                    echo "✓ Screenshot archived"
                } else {
                    echo "⚠ Screenshot not found at Screenshots/screenshot.png"
                }
                
                // Archive HTML email report
                if (fileExists('SOD_Email_Report.html')) {
                    archiveArtifacts artifacts: 'SOD_Email_Report.html', allowEmptyArchive: true
                    echo "✓ Email report archived"
                } else {
                    echo "⚠ Email report not found"
                }
                
                // Read the HTML report content for email
                def emailBody = ""
                if (fileExists('SOD_Email_Report.html')) {
                    emailBody = readFile('SOD_Email_Report.html')
                    echo "✓ Email report content loaded (${emailBody.length()} characters)"
                }
                
                // Send email via Jenkins
                if (emailBody) {
                    try {
                        mail(
                            to: "${env.email_to_recipients}",
                            // Uncomment to add CC:
                            // cc: "${env.email_cc_recipients}",
                            subject: "${env.MAIL_SUBJECT}",
                            body: emailBody,
                            mimeType: "text/html"
                        )
                        echo "✓ Email sent successfully"
                        echo "  To: ${env.email_to_recipients}"
                        echo "  Subject: ${env.MAIL_SUBJECT}"
                    } catch (Exception e) {
                        echo "✗ Failed to send email: ${e.message}"
                    }
                } else {
                    echo "✗ No email report content found - skipping email"
                }
                
                // Clean workspace
                echo "Cleaning workspace..."
                cleanWs deleteDirs: true, patterns: [
                    [pattern: '.env', type: 'EXCLUDE'],
                    [pattern: 'requirements.txt', type: 'EXCLUDE'],
                    [pattern: 'sod_automation.py', type: 'EXCLUDE'],
                    [pattern: 'Jenkinsfile', type: 'EXCLUDE']
                ]
                echo "✓ Workspace cleaned"
                
                echo "==================================="
            }
        }
        
        success {
            script {
                echo ""
                echo "╔═══════════════════════════════════════╗"
                echo "║  ✓ SOD AUTOMATION SUCCESS             ║"
                echo "╚═══════════════════════════════════════╝"
                echo ""
                echo "  Status: ${env.SOD_STATUS}"
                echo "  Subject: ${env.MAIL_SUBJECT}"
                echo "  Email: Sent to ${env.email_to_recipients}"
                echo "  Artifacts: Archived"
                echo ""
                echo "═══════════════════════════════════════"
            }
        }
        
        failure {
            script {
                echo ""
                echo "╔═══════════════════════════════════════╗"
                echo "║  ✗ SOD AUTOMATION FAILED              ║"
                echo "╚═══════════════════════════════════════╝"
                echo ""
                
                // Send failure notification email
                try {
                    def failureBody = """
                        <html>
                        <body style="font-family: Arial, sans-serif; margin: 20px;">
                        <h2 style="color: #d32f2f;">⚠ SOD Automation Job FAILED</h2>
                        <p>The SOD automation script encountered an error and could not complete successfully.</p>
                        
                        <table style="border-collapse: collapse; margin: 20px 0;">
                            <tr>
                                <td style="padding: 8px; font-weight: bold;">Build Number:</td>
                                <td style="padding: 8px;">#${env.BUILD_NUMBER}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; font-weight: bold;">Build URL:</td>
                                <td style="padding: 8px;"><a href="${env.BUILD_URL}">${env.BUILD_URL}</a></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; font-weight: bold;">Console Output:</td>
                                <td style="padding: 8px;"><a href="${env.BUILD_URL}console">View Console Log</a></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; font-weight: bold;">Timestamp:</td>
                                <td style="padding: 8px;">${new Date().format('yyyy-MM-dd HH:mm:ss')}</td>
                            </tr>
                        </table>
                        
                        <p>Please check the console output for detailed error information.</p>
                        
                        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ccc;">
                        <p><b>Thanks and Regards,</b><br>
                        Scheduling Team<br>
                        BNP Paribas CIB IT Production</p>
                        </body>
                        </html>
                    """
                    
                    mail(
                        to: "${env.email_to_recipients}",
                        subject: "FAILED: FTS Scheduling SOD - Build #${env.BUILD_NUMBER}",
                        body: failureBody,
                        mimeType: "text/html"
                    )
                    echo "✓ Failure notification email sent"
                } catch (Exception e) {
                    echo "✗ Failed to send failure notification: ${e.message}"
                }
                
                echo "═══════════════════════════════════════"
            }
        }
        
        aborted {
            script {
                echo ""
                echo "╔═══════════════════════════════════════╗"
                echo "║  ⚠ SOD AUTOMATION ABORTED             ║"
                echo "╚═══════════════════════════════════════╝"
                echo ""
            }
        }
    }
}