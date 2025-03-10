import os
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv
from flask_cors import CORS  # Import Flask-CORS

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Example for Gmail
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')  # Your email account (from .env)
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')  # Email password (from .env)
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USER')

mail = Mail(app)

@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        # Extract form data
        to_emails = [request.form['toEmail1'], request.form['toEmail2'], request.form['toEmail3']]
        cc_emails = [request.form['CcEmail1'], request.form['CcEmail2']]
        subject = f"[Parent Request ID: {request.form['parentRequestID']}] Part Request: {request.form['partRequestSubj']}"

        # Create the email body with the user inputs
        body = f"""
        Company: {request.form['company']}
        Contact: {request.form['contact']}
        Part Request: {request.form['partRequest']}
        Attending Engineer: {request.form['attendingEngineer']}
        Model: {request.form['model']}
        Product No: {request.form['productNo']}
        Serial No: {request.form['serialNo']}
        Issue Description: {request.form['issueDescription']}
        Has the unit been repaired for this issue before: {request.form['hasUnitBeenRepaired']}
        If yes, please provide repair history (Must be Bulleted List per Date): {request.form['repairHistory']}
        Detailed Troubleshooting Performed (list in points): {request.form['troubleshootingPerformed']}
        """

       # Handle the defective part image (check if it's uploaded)
        defective_part_image = request.files.get('defectivePartImage')
        if defective_part_image:
            filename = defective_part_image.filename
            file_path = os.path.join('uploads', filename)  # Save the image locally
            defective_part_image.save(file_path)
            body += f"\nPicture/Image(s): <img src='cid:{filename}'>"

        # Handle additional parts
        additional_parts = []
        for i in range(len(request.files)):
            part_text = request.form.get(f"additionalPartText{i}")
            part_file = request.files.get(f"additionalPartFile{i}")
            
            additional_parts.append(f"Part {i+1}: {part_text}")
            if part_file:
                filename = part_file.filename
                file_path = os.path.join('uploads', filename)  # Save uploaded file
                part_file.save(file_path)
                additional_parts.append(f"File: <img src='cid:{filename}'>")

        body += "\n\n".join(additional_parts)
        
        body += f"""
        UEFI Diagnostics Performed: {request.form['uefiDiagnosticsPerformed']}
        If yes, please provide the UEFI Failure ID: {request.form['uefiFailureID']}
        If no, (Please share the reason - T/C the use of exception codes): {request.form['exceptionReason']}
        Performed Windows Update: {request.form['windowsUpdate']}
        Performed Firmware/Drivers update: {request.form['firmwareDriversUpdate']}
        Performed BIOS Update / Crisis Recovery: {request.form['biosUpdate']}
        Performed Reimaging/Reformat/Reinstallation of OS: {request.form['reimagingOS']}
        Windows OS Image: {request.form['windowsOSImage']}
        Performed Minimum Config/Hard Reset: {request.form['hardReset']}
        Is there any WISE Advisory: {request.form['wiseAdvisory']}
        Is there any 3rd Party/Non-HP Part involved: {request.form['thirdPartyPart']}
        Suggested Recommendation: {request.form['suggestedRecommendation']}
        With CSDP attachment: {request.form['csdpAttachment']}
        Email Address Coordinator (Handling CSDP): {request.form['csdpEmail']}
        Email Address of Assigned Engineer: {request.form['engineerEmail']}
        CC: {request.form['ccEmailName']} {request.form['ccEmail']}

        """

         # Prepare message with attachment
        msg = Message(subject, recipients=to_emails, cc=cc_emails, body=body, html=body)

        # Attach images to the email if available (for inline display)
        if defective_part_image:
            msg.attach(defective_part_image.filename, 'image/jpeg', defective_part_image.read(), headers={'Content-ID': f'<{defective_part_image.filename}>'})

        # Attach additional part images if available
        for i in range(len(request.files)):
            part_file = request.files.get(f"additionalPartFile{i}")
            if part_file:
                msg.attach(part_file.filename, 'image/jpeg', part_file.read(), headers={'Content-ID': f'<{part_file.filename}>'})

        # Send email
        mail.send(msg)

        return jsonify({"success": True, "message": "Email sent successfully!"})
    except Exception as e:
        print(f"Error: {str(e)}")  # Add more logging
        return jsonify({"success": False, "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
