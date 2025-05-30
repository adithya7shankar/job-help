import datetime

class JobApplication:
    """
    Represents a single job application.
    """

    PREDEFINED_STATUSES = [
        "Wishlist/To Apply",
        "Applied",
        "Online Assessment",
        "HR Screening",
        "Technical Interview (Round 1)",
        "Technical Interview (Round 2+)", # Combining multiple tech rounds for simplicity here
        "Hiring Manager Interview",
        "On-site/Final Interview",
        "Offer Extended",
        "Offer Accepted",
        "Offer Declined",
        "Rejected",
        "Withdrew Application"
    ]

    def __init__(self, company_name, job_title, application_date_str,
                 source_of_listing="", job_id="", job_description_link="",
                 location="", salary_expectation="", status="Wishlist/To Apply",
                 notes=""):
        self.company_name = company_name
        self.job_title = job_title
        self.job_id = job_id # Optional
        
        try:
            self.application_date = datetime.datetime.strptime(application_date_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"Warning: Invalid application_date format for {job_title} at {company_name}. Please use YYYY-MM-DD. Setting to None.")
            self.application_date = None
            
        self.source_of_listing = source_of_listing
        self.job_description_link = job_description_link # Link, or could be text
        self.location = location # Could be a string like "City, State, Country" or "Remote"
        self.salary_expectation = salary_expectation # Optional, string for now
        
        if status not in self.PREDEFINED_STATUSES:
            print(f"Warning: Status '{status}' is not a predefined status. Defaulting to 'Wishlist/To Apply'.")
            self.status = "Wishlist/To Apply"
        else:
            self.status = status
            
        self.last_activity_date = datetime.date.today() # Initialize with creation date
        self.notes = notes # General notes area
        self.resume_version = None # To be linked later
        self.cover_letter_version = None # To be linked later

    def __str__(self):
        return (f"Company: {self.company_name}\n"
                f"Title: {self.job_title}\n"
                f"Job ID: {self.job_id or 'N/A'}\n"
                f"Application Date: {self.application_date}\n"
                f"Status: {self.status}\n"
                f"Location: {self.location or 'N/A'}\n"
                f"Source: {self.source_of_listing or 'N/A'}\n"
                f"Description Link: {self.job_description_link or 'N/A'}\n"
                f"Salary Expectation: {self.salary_expectation or 'N/A'}\n"
                f"Last Activity: {self.last_activity_date}\n"
                f"Notes: {self.notes[:50] + '...' if self.notes and len(self.notes) > 50 else self.notes or 'N/A'}\n"
                f"--------------------")

    def update_status(self, new_status):
        if new_status in self.PREDEFINED_STATUSES:
            self.status = new_status
            self.last_activity_date = datetime.date.today()
            print(f"Status for '{self.job_title}' at '{self.company_name}' updated to '{new_status}'.")
        else:
            print(f"Error: '{new_status}' is not a valid predefined status.")

    def add_note(self, note):
        if self.notes:
            self.notes += f"\n[{datetime.date.today()}] {note}"
        else:
            self.notes = f"[{datetime.date.today()}] {note}"
        self.last_activity_date = datetime.date.today()

if __name__ == '__main__':
    # Example Usage:
    app1 = JobApplication(
        company_name="Tech Solutions Inc.",
        job_title="Software Engineer",
        application_date_str="2025-05-30",
        source_of_listing="LinkedIn",
        job_id="TSI-SE-123",
        job_description_link="http://example.com/job/123",
        location="Remote",
        salary_expectation="120k-140k USD",
        status="Applied"
    )
    print(app1)

    app1.add_note("Completed initial online assessment.")
    app1.update_status("Online Assessment")
    print("\nAfter update:")
    print(app1)

    app2 = JobApplication(
        company_name="Innovate AI Corp.",
        job_title="Machine Learning Engineer",
        application_date_str="2025-05-28",
        source_of_listing="Company Careers Page",
        status="Wishlist/To Apply"
    )
    print(app2)
    app2.update_status("Applied") # Valid status
    app2.update_status("Coffee Chat") # Invalid status example
    print(app2)
