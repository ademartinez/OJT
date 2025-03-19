import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Ensure the uploads directory exists
# Define separate upload folders
GENERAL_IMAGES_FOLDER = './uploads/general_images'
DEFECTIVE_PART_IMAGES_FOLDER = './uploads/defective_part_images'
# Ensure the folders exist
os.makedirs(GENERAL_IMAGES_FOLDER, exist_ok=True)
os.makedirs(DEFECTIVE_PART_IMAGES_FOLDER, exist_ok=True)

# Ensure the uploads directory exists
UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        # Get subject and message from the form data
        subject = request.form['subject']
        company = request.form['company']
        contact = request.form['contact']
        partRequest = request.form['partRequest']
        attendingEngineer = request.form['attendingEngineer']
        model = request.form['model']
        productNo = request.form['productNo']
        serialNo = request.form['serialNo']
        issueDescription = request.form['issueDescription']
        hasUnitBeenRepaired = request.form['hasUnitBeenRepaired']
        repairHistory = request.form['repairHistory']
        troubleshootingPerformed = request.form['troubleshootingPerformed']
        UEFIDiag = request.form['UEFIDiag']
        UEFIFailureID = request.form['UEFIFailureID']
        exceptionCodes = request.form['exceptionCodes']
        windowsUpdate = request.form['windowsUpdate']
        firmwareUpdate = request.form['firmwareUpdate']
        biosUpdate = request.form['biosUpdate']
        reimaging = request.form['reimaging']
        windowsOSImage = request.form['windowsOSImage']
        minConfigReset = request.form['minConfigReset']
        WISEAdvisory = request.form['WISEAdvisory']
        nonHP = request.form['nonHP']
        suggestedRec = request.form['suggestedRec']
        CSDPAttachment = request.form['CSDPAttachment']
        emailCoordinator = request.form['emailCoordinator']
        emailAssignedEngineer = request.form['emailAssignedEngineer']
        ccBody = request.form['ccBody']
        ccEmail = request.form['ccEmail']
        
        # Get recipients and CCs from the form data
        recipients = [request.form[key] for key in request.form if key.startswith('recipient')]
        ccs = [request.form[key] for key in request.form if key.startswith('cc')]

        # Get defectivePartCTCode values from the form data
        defective_part_ct_codes = [request.form[key] for key in request.form if key.startswith('defectivePartCTCode')]

        # Create the email message
        msg = MIMEMultipart('related')
        msg['Subject'] = subject
        msg['From'] = EMAIL_USER
        msg['To'] = ', '.join(recipients)
        msg['Cc'] = ', '.join(ccs)

        # Create the body with the inline images
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style> 
                body {{ 
                    font-family: Aptos;
                    }}
                pre {{
                    font-family: Aptos;                    
                    margin: 0 20px;
                    }} 
            </style>
        </head>
        <body>
        """

        body += f"""
     <p>Hi Team,<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Kindly process a replacement part to HP.</p>

     <p>Company : {company}<br>
        Contact : {contact}<br>
        Part Request:</p>

        <pre>{partRequest}</pre>

     <p>Attending Engineer: {attendingEngineer}</p>

     <p>Model                                               : {model}<br>
        Product No                                          : {productNo}<br>
        Serial No                                           : {serialNo}<br>
        Issue Description:</p>
        <pre>{issueDescription}</pre>
        
     <p>Has the unit been repaired for this issue before    : {hasUnitBeenRepaired}</p>
        """
        
        if hasUnitBeenRepaired == 'Yes':
            body += f"""
            <p>If yes, please provide repair history (Must be in Bulleted List per Date):</p>
            <ul>
            """ + "".join([f'<li>{line}</li>' for line in repairHistory.split('\n')]) + """
            </ul>
            """
        
        body += f"""
        <p>Detailed troubleshooting performed (list in points):</p>
        <ul>
        """ + "".join([f'<li>{line}</li>' for line in troubleshootingPerformed.split('\n')]) + """
        </ul>
        """ 

        # Add general images to the email body
        body += "<p>Picture/Image(s):</p>"
        for index, key in enumerate(request.files):
            if not key.startswith("defectivePartCTCodeImage"):  # Skip defectivePartCTCodeImage files
                body += f'<img src="cid:image{index}" alt="User Image {index + 1}" style="max-width: 400px; height: auto;" /><br>'

        body += """
        <p>Defective Part CT Code:</p>
        """

        # Add defectivePartCTCode values paired with their images to the email body
        if defective_part_ct_codes:
            for index, code in enumerate(defective_part_ct_codes):
                body += f"<p>{code}<br>"
                if f"defectivePartCTCodeImage{index}" in request.files:  # Check if the image exists for the index
                    body += f'<img src="cid:defectivePartCTCodeImage{index}" alt="Defective Part CT Code Image {index + 1}" style="max-width: 400px; height: auto;" /></p>'

        body += f"""
     <p>UEFI Diagnostics Performed                                          : {UEFIDiag}<br>
        If yes, please provide the UEFI Failure ID                          : {UEFIFailureID}<br>
        If no, (Please share the reason - T/C the use of exception codes)   : {exceptionCodes}<br>
        Performed Windows Update                                            : {windowsUpdate}<br>
        Performed Firmware/Drivers Update                                   : {firmwareUpdate}<br>
        Performed BIOS Update/Crisis Recovery                               : {biosUpdate}<br>
        Performed Reimaging/Reformat/Reinstallation of OS                   : {reimaging}<br>
        Windows OS Image                                                    : {windowsOSImage}<br>
        Performed Minimum Config/Hard Reset                                 : {minConfigReset}<br>
        Is there any WISE Advisory                                          : {WISEAdvisory}<br>
        Is there any 3rd Party/Non-HP Part involved                         : {nonHP}<br>
        Suggested Recommendation                                            : {suggestedRec}</p>

     <p>With CSDP Attachment                                                : {CSDPAttachment}<br>
        Email Address Coordinator (Handling CSDP)                           : {emailCoordinator}<br>
        Email Address of Assigned Engineer                                  : {emailAssignedEngineer}<br>
        CC: {ccBody} {ccEmail}</p>
      
     <p>Regards,</p>
     <p>{attendingEngineer}</p>
        </body>
        </html>

        """

        msg.attach(MIMEText(body, 'html'))

        # Attach the images inline
        for key, file in request.files.items():
            if key.startswith("defectivePartCTCodeImage"):  # Save defectivePartCTCodeImage files
                file_path = os.path.join(DEFECTIVE_PART_IMAGES_FOLDER, file.filename)
                file.save(file_path)
                with open(file_path, 'rb') as f:
                    img = MIMEImage(f.read())
                    index = key.replace("defectivePartCTCodeImage", "")  # Extract the index from the key
                    img.add_header('Content-ID', f'<defectivePartCTCodeImage{index}>')
            else:  # Save general images
                file_path = os.path.join(GENERAL_IMAGES_FOLDER, file.filename)
                file.save(file_path)
                with open(file_path, 'rb') as f:
                    img = MIMEImage(f.read())
                    index = key.replace("image", "")  # Extract the index for general images
                    img.add_header('Content-ID', f'<image{index}>')
            img.add_header('Content-Disposition', 'inline', filename=file.filename)  # Ensure inline display
            msg.attach(img)
        
        # Send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, recipients + ccs, msg.as_string())
        
        return jsonify({'message': 'Email sent successfully!'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error to the console for debugging
        return jsonify({'message': f'Failed to send email: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)