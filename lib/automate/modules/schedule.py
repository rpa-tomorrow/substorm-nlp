from __future__ import print_function
import lib.utils.tools.time_convert as tc
import spacy
import logging

from lib import Error
from lib.automate.google import Google
from lib.automate.modules import Module, NoSenderError
from lib.utils.contacts import get_emails, prompt_contact_choice, followup_contact_choice
from datetime import datetime, timedelta

# Module logger
log = logging.getLogger(__name__)


class Schedule(Module):
    verbs = ["book", "schedule", "meeting"]

    def __init__(self):
        super(Schedule, self).__init__()
        self.nlp_model = None

    def prepare(self, nlp_model_names, text, sender):
        if self.nlp_model is None:
            self.nlp_model = spacy.load(nlp_model_names["schedule"])
        to, start, end, body = self.nlp(text)
        return self.prepare_processed(to, start, end, body, sender)

    def prepare_processed(self, to, start, end, body, sender):
        self.to = to
        self.start = start
        self.end = end
        self.body = body
        self.sender = sender
        self.followup_type = None
        # stores the available choices when the user needs to clarify the correct attendee
        self.uncertain_attendee = None
        self.unknown_attendee = None

        # print("to = ", to, " start = ", start, " end = ", end,  " body = ", body, " sender = ", sender)

        if not sender:
            raise NoSenderError("No sender found!")

        if not isinstance(start, datetime):
            self.followup_type = "start"
            return "Could not parse date to schedule start time.\nPlease enter date in YYYYMMDD HH:MM format"

        if not body:
            self.followup_type = "body"
            return "Found no event summary. What is the event about"

        settings = sender["email"]
        username = settings.get("username")

        google = Google(username)
        calendar = google.calendar(settings)
        self.calendar = calendar

        # Parse Time
        start_time = tc.local_to_utc_time(self.start).isoformat()
        end_time = tc.local_to_utc_time(self.end).isoformat()


        # Parse attendees (try to resolve email addresses)
        parsed_attendees = get_emails(self.to, sender)
        attendees = parsed_attendees["emails"]
        for (name, candidates) in parsed_attendees["uncertain"]:
            self.uncertain_attendee = (name, candidates)
            self.followup_type = "to_uncertain"
            return prompt_contact_choice(name, candidates)

        for name in parsed_attendees["unknown"]:
            self.followup_type = "to_unknown"
            self.unknown_attendee = name
            return f"Found no contact named {name}. Do you want to continue scheduling the meeting anyway? [Y/n]"

        attendees = [settings["address"]] + attendees
        event = calendar.event(start_time, end_time, attendees, self.body)
        self.event = event

        print("event = ", event)

        # Get or create user credentials
        creds = self.credentials(username)

        # Create Event using Google calendar API
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        self.service = service

        # Check if we are busy
        me_busy = calendar.freebusy(start_time, end_time, ["primary"])
        to_busy = calendar.freebusy(start_time, end_time, to)
        other = f"{', '.join(to_busy[:-1])} and {to_busy[-1]}" if len(to_busy) > 1 else "".join(to_busy)
        if me_busy and to_busy:
            self.followup_type = "both_busy"
            return f"You as well as {other} seem to be busy. Do you want to book the meeting anyway? [Y/n]"
        elif me_busy:
            self.followup_type = "self_busy"
            return "You seem to be busy during this meeting. Do you want to book it anyway? [Y/n]"
        elif to_busy:
            self.followup_type = "to_busy"
            return f"{other} seem to be busy during this meeting. Do you want to book it anyway? [Y/n]"

    def execute(self):
        event = self.calendar.send_event(self.event)
        return "Event created, see link: %s" % (event.get("htmlLink"))

    def followup(self, answer):
        """
        Follow up method after the module have had to ask a question to clarify some parameter, or just
        want to check that it interpreted everything correctly.
        """
        if self.followup_type == "start":
            try:
                start = datetime.fromisoformat(answer)
            except Exception:
                start = None
            return self.prepare_processed(self.to, start, self.body, self.sender)
        elif self.followup_type == "body":
            return self.prepare_processed(self.to, self.start, answer, self.sender)
        elif self.followup_type == "self_busy" or self.followup_type == "both_busy" or self.followup_type == "to_busy":
            if answer == "" or answer.lower() == "y" or answer.lower() == "yes":
                return None
            elif answer.lower() == "n" or answer.lower() == "no":
                raise ActionInterruptedByUserError("Interrupted due to busy attendees.")
            else:
                return self.prepare_processed(self.to, self.start, self.body, self.sender)
        elif self.followup_type == "to_uncertain":
            try:
                choice = int(answer) - 1
            except Exception:
                return self.prepare_processed(self.to, self.start, self.body, self.sender)
            name, candidates = self.uncertain_attendee
            if choice >= 0 and choice < len(candidates):
                self.to.remove(name)  # update to so recursive call continues resolving new attendees
                self.to.append(candidates[choice][1])  # add email of chosen attendee
            return self.prepare_processed(self.to, self.start, self.body, self.sender)
        elif self.followup_type == "to_unknown":
            if answer == "" or answer.lower() == "y" or answer.lower() == "yes":
                self.to.remove(self.unknown_attendee)
                return self.prepare_processed(self.to, self.start, self.body, self.sender)
            elif answer.lower() == "n" or answer.lower() == "no":
                raise ActionInterruptedByUserError("Interrupted due to unknown attendee.")
            else:
                return self.prepare_processed(self.to, self.start, self.body, self.sender)
        else:
            raise NotImplementedError("Did not find any valid followup question to answer.")

    def nlp(self, text):

        doc = self.nlp_model(text)

        to = []
        start = []
        end = []
        body = []

        for token in doc:
            if token.dep_ == "TO":
                to.append(token.text)
            elif token.dep_ == "START":
                start.append(token.text)
            elif token.dep_ == "END":
                end.append(token.text)
            elif token.dep_ == "BODY":
                body.append(token.text)
            log.debug("%s %s", token.text, token.dep_)


        time1 = datetime.now()
        if len(start) == 0:
            time1 = time1 + timedelta(seconds=5)
        else:
            time1 = tc.parse_time(start)

        time2 = datetime.now()
        time2 = tc.parse_time(end)

        _body = " ".join(body)

        return (to, time1, time2, _body)


class ActionInterruptedByUserError(Error):
    pass
