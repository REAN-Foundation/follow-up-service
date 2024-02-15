from enum import Enum

class AppStatusEnum(str, Enum):
    Patient_In_Lobby = "In lobby"
    Patient_Seen = "Seen"
    Patient_Cancelled = "Cancelled"
    Pending_Arrival = "Pending arrival"

class PatientReplyEnum(str, Enum):
    Patient_Replied_Yes = "Yes"
    Patient_Replied_No = "No"
    Invalid_Patient_Reply = "Not replied"
   