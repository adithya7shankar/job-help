from tracker_models import JobApplication
import datetime

# In-memory storage for job applications
job_applications = []

def add_new_application():
    """Prompts the user for job application details and adds it to the list."""
    print("\n--- Add New Job Application ---")
    company_name = input("Company Name: ")
    job_title = input("Job Title: ")
    
    application_date_str = ""
    while True:
        application_date_str = input("Application Date (YYYY-MM-DD): ")
        try:
            datetime.datetime.strptime(application_date_str, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

    source_of_listing = input("Source of Listing (e.g., LinkedIn, Referral): ")
    job_id = input("Job ID (optional, press Enter to skip): ")
    job_description_link = input("Link to Job Description (optional): ")
    location = input("Location (e.g., City, State, Remote; optional): ")
    salary_expectation = input("Salary Expectation (optional): ")
    
    print("\nAvailable Statuses:")
    for i, status_option in enumerate(JobApplication.PREDEFINED_STATUSES):
        print(f"{i + 1}. {status_option}")
    
    status_choice_idx = -1
    while True:
        try:
            choice = input(f"Initial Status (select 1-{len(JobApplication.PREDEFINED_STATUSES)}, default is 'Wishlist/To Apply'): ")
            if not choice: # Default to Wishlist/To Apply
                status = "Wishlist/To Apply"
                break
            status_choice_idx = int(choice) - 1
            if 0 <= status_choice_idx < len(JobApplication.PREDEFINED_STATUSES):
                status = JobApplication.PREDEFINED_STATUSES[status_choice_idx]
                break
            else:
                print("Invalid choice. Please select a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            
    notes = input("Initial Notes (optional): ")

    new_app = JobApplication(
        company_name=company_name,
        job_title=job_title,
        application_date_str=application_date_str,
        source_of_listing=source_of_listing,
        job_id=job_id,
        job_description_link=job_description_link,
        location=location,
        salary_expectation=salary_expectation,
        status=status,
        notes=notes
    )
    job_applications.append(new_app)
    print(f"\nApplication for '{job_title}' at '{company_name}' added successfully!")

def list_all_applications():
    """Displays all tracked job applications."""
    print("\n--- All Tracked Job Applications ---")
    if not job_applications:
        print("No job applications tracked yet.")
        return

    for i, app in enumerate(job_applications):
        print(f"\n--- Application #{i+1} ---")
        print(app)

def update_application_status():
    """Allows updating the status of an existing application."""
    if not job_applications:
        print("No applications to update.")
        return

    print("\n--- Update Application Status ---")
    list_all_applications_summary() # Show a summary to pick from

    while True:
        try:
            app_index_str = input("Enter the number of the application to update (or 0 to cancel): ")
            app_index = int(app_index_str) -1
            if app_index == -1: # User entered 0 to cancel
                return
            if 0 <= app_index < len(job_applications):
                selected_app = job_applications[app_index]
                break
            else:
                print("Invalid application number.")
        except ValueError:
            print("Please enter a valid number.")
    
    print("\nAvailable Statuses:")
    for i, status_option in enumerate(JobApplication.PREDEFINED_STATUSES):
        print(f"{i + 1}. {status_option}")
    
    while True:
        try:
            status_choice_idx = int(input(f"New Status for '{selected_app.job_title}' (select 1-{len(JobApplication.PREDEFINED_STATUSES)}): ")) - 1
            if 0 <= status_choice_idx < len(JobApplication.PREDEFINED_STATUSES):
                new_status = JobApplication.PREDEFINED_STATUSES[status_choice_idx]
                selected_app.update_status(new_status)
                break
            else:
                print("Invalid choice. Please select a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def add_note_to_application():
    """Adds a note to an existing application."""
    if not job_applications:
        print("No applications to add notes to.")
        return

    print("\n--- Add Note to Application ---")
    list_all_applications_summary()

    while True:
        try:
            app_index_str = input("Enter the number of the application to add a note to (or 0 to cancel): ")
            app_index = int(app_index_str) -1
            if app_index == -1: # User entered 0 to cancel
                return
            if 0 <= app_index < len(job_applications):
                selected_app = job_applications[app_index]
                break
            else:
                print("Invalid application number.")
        except ValueError:
            print("Please enter a valid number.")
    
    note_text = input(f"Enter note for '{selected_app.job_title}': ")
    selected_app.add_note(note_text)
    print("Note added successfully.")


def list_all_applications_summary():
    """Displays a summarized list of applications for selection."""
    if not job_applications:
        # This case should be handled by the calling function
        return
    print("\n--- Current Applications ---")
    for i, app in enumerate(job_applications):
        print(f"{i+1}. {app.job_title} at {app.company_name} (Status: {app.status})")


def main_menu():
    """Displays the main menu and handles user choices."""
    while True:
        print("\n--- Job Application Tracker Menu ---")
        print("1. Add New Application")
        print("2. List All Applications")
        print("3. Update Application Status")
        print("4. Add Note to Application")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            add_new_application()
        elif choice == '2':
            list_all_applications()
        elif choice == '3':
            update_application_status()
        elif choice == '4':
            add_note_to_application()
        elif choice == '5':
            print("Exiting Job Application Tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
