
## Follow-Up Service
A general purpose service for processing appointment documents and contents for setting appointment reminders
Clone the service and execute following steps to install dependencies
1. python -m venv env
2. env\Scripts\activate
3. pip install -r requirements.txt
4. pip freeze > requirement.txt

# Brief Follow-Up Service

## Follow-Up Service

The Follow-Up service, in association with Reancare service and the admin panel, facilitates setting up reminders for patients with appointments and the delivery of responses from patients to the admin in a quick and detailed way.

---

## For GMU Client

It consists of appointment PDF upload, which contains:
- Patient name
- Arrival status
- Phone number
- Appointment type  
  *(Note: This PDF is generated using Practice Fusion.)*

This PDF is uploaded to S3, and the Short Notification Service (SNS) is activated, triggering the document processor. This, in turn, sets a reminder for the patient's phone number 20 minutes after the PDF upload.  
*(The 20-minute delay is set because the appointment cron runs every 15 minutes in the Reancare service.)*

### Admin Portal Features

The Admin Portal provides the user interface for uploading PDFs and viewing the status report.

### Workflow

1. **Admin Login & PDF Upload**  
   - The admin logs into the Admin Portal service with valid credentials.
   - The appointment PDF is uploaded in the *Appointment Follow-Up* section.

2. **Triggering Reminders**  
   - All patients with 'Pending Arrival' status receive reminders.
   - Patients with 'Cancelled' or 'In Lobby' statuses do not receive reminders.

3. **Admin Notification**  
   - The *Follow-Up* service contains a seed file with admin phone numbers.
   - A summary message is sent to the admin containing:
     - Total number of patients found in the PDF
     - Total reminders set

4. **Status Report in Admin Portal**  
   - Displays:
     - Total patient count
     - Arrived patient count
     - Not arrived patient count
     - Individual patient replies

5. **Reminder Timing**  
   - 20 minutes after PDF upload, reminders are sent to patients with 'Pending Arrival' status.

6. **Patient Replies**  
   - The reply is reflected in the status report.
   - Patients who did not reply are marked as *'Not Replied'*.

7. **Subsequent PDF Uploads**  
   - Only patients who are still in 'Pending Arrival' and have not replied will receive another reminder.
   - New patients in the second upload receive reminders and are recorded in the status report.

8. **Non-Applicable Status**  
   - Patients with 'Cancelled' or 'In Lobby' statuses have replies marked as *'Non Applicable (N/A)'*.

9. **Daily Status Report**  
   - Only one PDF status report is generated on the initial upload.
   - Later uploads edit or overwrite the existing report.

---

## For GGHN Client

For GGHN clients, the system retrieves daily appointment lists via an API call to the client's server.

### Extracted Information:
- Participation code
- Facility name (hospital name)
- Case manager

The patient's phone number is retrieved from Reancare service using the participation code.

### Workflow

1. **Daily Cron Job (6 AM Nigeria Time)**  
   - Sets and sends reminders for the day's appointments.

2. **Bot Interaction & Registration**  
   - Patients interact with the bot and provide their participation code.
   - They are registered in Reancare service via the bot wrapper service.

3. **Retrieving Phone Numbers & Sending Reminders**  
   - The Follow-Up service retrieves the phone number from Reancare using the participation code.
   - A one-time reminder is set in Reancare service.
   - After 20 minutes, a cron job runs to send the appointment message.

4. **Patient Replies**  
   - Reflected in the status report.
   - Non-respondents are marked as *'Not Replied'*.

5. **Re-Triggered Reminders**  
   - Only patients who have not replied receive another reminder.

6. **Appointment Cancellations and Manual trigger**  
   - Using admin portal admins of GGhn can manually trigger appointment reminder API which will send reminder message after 20 min 
   - They can also Cancel the cron job set to trigger appointment for any further days via admin portal.
   - Facility to view the cancel dates is also provided through admin portal.
   - Admins just have to login by their credientials.

7. **Appointment FollowUp Assesssment** 
   - An Assesssment is triggere from reancare side when bot wrapper notes the patient replied as 'No' for attending appointment service.
   - At present it consist of one single choice question.
   - Patients who reply 'No' must provide a reason.
   - The reason is sent to the case manager.

8. **Case Manager Retrieval**  
   - The case manager’s name is retrieved from appointment details.
   - Their contact information is stored in a JSON file.

---

## **Important Points in Follow-Up Service**

- Patient phone numbers must not be duplicated for multiple patients, as replies are captured using phone numbers.
- If a PDF upload contains patients marked as 'In Lobby' or 'Cancelled' and a status report is generated, subsequent uploads for the day should not have these patients marked as 'Pending Arrival'.
- Invalid data extracted from tables is stored in the *invalid data file* in the temp folder.

---

### **Storage Details**
- **MongoDB Atlas** is used to store appointment files in JSON format.
- **Cluster Zero** is used for storage.
- **For testing:** Files are stored in the local `temp` folder in the working directory.
