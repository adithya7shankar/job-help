import requests
from bs4 import BeautifulSoup

import csv
import urllib.parse
import os

def read_existing_career_urls(filepath):
    """Reads the company_career_urls_output.csv file."""
    existing_data = []
    company_names_set = set()
    if not os.path.exists(filepath):
        # If the file doesn't exist, create it with headers
        try:
            with open(filepath, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Company', 'URL'])
            print(f"'{filepath}' did not exist. Created it with headers.")
        except Exception as e:
            print(f"Error creating '{filepath}': {e}")
        return existing_data, company_names_set
        
    try:
        with open(filepath, mode='r', encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file)
            if 'Company' not in reader.fieldnames or 'URL' not in reader.fieldnames:
                print(f"Warning: '{filepath}' is missing 'Company' or 'URL' header. Treating as empty and attempting to fix.")
                # Attempt to re-create with headers if problematic
                try:
                    with open(filepath, mode='w', encoding='utf-8', newline='') as fix_file:
                        writer = csv.writer(fix_file)
                        writer.writerow(['Company', 'URL'])
                    print(f"Re-created '{filepath}' with correct headers because existing headers were missing.")
                except Exception as e_fix:
                    print(f"Error re-creating '{filepath}' with headers: {e_fix}")
                return existing_data, company_names_set # Return empty after attempting fix

            for row in reader:
                company_name = row.get('Company', '').strip()
                url = row.get('URL', '').strip()
                if company_name:
                    existing_data.append({'Company': company_name, 'URL': url})
                    company_names_set.add(company_name.lower())
    except Exception as e:
        print(f"Error reading '{filepath}': {e}")
    return existing_data, company_names_set

def read_new_companies_list(filepath):
    """Reads the HiringTechCompanies - TheList.csv file."""
    new_companies = []
    try:
        with open(filepath, mode='r', encoding='utf-8', newline='') as file:
            reader = csv.reader(file)
            next(reader) # Skip metadata line
            actual_header = next(reader) # Actual header
            
            company_col_idx = -1
            try:
                company_col_idx = actual_header.index('Company')
            except ValueError:
                print(f"Error: 'Company' column not found in header of '{filepath}': {actual_header}")
                return new_companies

            for row in reader:
                if len(row) > company_col_idx:
                    company_name = row[company_col_idx].strip()
                    # Basic cleaning: take only the name before a parenthesis if one exists
                    if '(' in company_name:
                        company_name = company_name.split('(', 1)[0].strip()
                    if company_name:
                        new_companies.append(company_name)
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
    except StopIteration:
        print(f"Error: CSV file '{filepath}' seems to be empty or has too few rows for headers.")
    except Exception as e:
        print(f"An error occurred while reading '{filepath}': {e}")
    return new_companies

def merge_and_update_career_urls(output_filepath, new_companies_list_filepath):
    """
    Merges new companies into the output CSV and identifies those needing URLs.
    """
    existing_data, existing_company_names_set = read_existing_career_urls(output_filepath)
    new_company_names_list = read_new_companies_list(new_companies_list_filepath)

    # Add new unique companies to the existing data list
    for new_name in new_company_names_list:
        if new_name.lower() not in existing_company_names_set:
            existing_data.append({'Company': new_name, 'URL': ''})
            existing_company_names_set.add(new_name.lower()) # Add to set to avoid duplicates from new list itself

    # Sort by company name for consistency, can be optional
    existing_data.sort(key=lambda x: x['Company'].lower())

    # Write the consolidated list back to the output file
    try:
        with open(output_filepath, mode='w', encoding='utf-8', newline='') as file:
            if not existing_data: 
                 writer = csv.writer(file)
                 writer.writerow(['Company', 'URL']) 
            else:
                # Ensure fieldnames are based on the actual keys present, default to 'Company', 'URL'
                fieldnames = list(existing_data[0].keys()) if existing_data else ['Company', 'URL']
                if 'Company' not in fieldnames: fieldnames.insert(0, 'Company') # Ensure Company is first
                if 'URL' not in fieldnames: fieldnames.append('URL') # Ensure URL is present
                # Filter out any other potential keys if they are not 'Company' or 'URL' for simplicity
                fieldnames = [f for f in fieldnames if f in ['Company', 'URL']]


                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                # Filter rows to only write 'Company' and 'URL'
                filtered_rows = [{k: row[k] for k in fieldnames if k in row} for row in existing_data]
                writer.writerows(filtered_rows)
        print(f"Successfully updated '{output_filepath}' with new companies.")
    except Exception as e:
        print(f"Error writing to '{output_filepath}': {e}")

    # Now, re-process the updated file to list companies needing URLs
    companies_with_urls = []
    companies_needing_urls = []
    for item in existing_data:
        # Check if 'Company' key exists and is not empty before trying to access 'URL'
        if item.get('Company') and not item.get('URL'):
            companies_needing_urls.append(item['Company'])
        elif item.get('Company') and item.get('URL'):
             companies_with_urls.append(item)
            
    print("\n--- Companies with URLs (from consolidated list) ---")
    if companies_with_urls:
        for item in companies_with_urls:
            print(f"Company: {item.get('Company')}, URL: {item.get('URL')}")
    else:
        print("No companies with pre-filled URLs found in the consolidated list.")

    print("\n--- Companies needing career page URLs (from consolidated list) ---")
    if companies_needing_urls:
        for i, company_name in enumerate(companies_needing_urls):
            print(f"{i+1}. {company_name}")
    else:
        print("No companies found that need a career page URL in the consolidated list.")
        
    return companies_with_urls, companies_needing_urls

def scrape_specific_job_page(specific_url, keyword_hint="machine learning"): # Renamed from scrape_uber_jobs
    """
    Scrapes a specific job page URL (e.g. Uber).
    The keyword_hint is used for very basic filtering if needed, but the URL is primary.
    Note: HTML structure and selectors are highly likely to need adjustment.
    """
    base_url = specific_url 
    params = {} 

    print(f"Attempting to fetch job page: {base_url} (related to '{keyword_hint}')...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive",
        "DNT": "1", # Do Not Track
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        # Using base_url directly as it now contains the query
        response = requests.get(base_url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    job_links = []

    # --- PARSING LOGIC (HIGHLY LIKELY TO BE INCORRECT AND NEED ADJUSTMENT) ---
    print("Attempting to parse job page. Selectors are speculative and may not work for all sites.")

    # This generic parsing logic is unlikely to work well for diverse job pages.
    # It's a placeholder and would need to be made site-specific or much more intelligent.
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        link_text_lower = a_tag.get_text(separator=" ", strip=True).lower()
        hint_parts = keyword_hint.lower().split(" ")
        
        is_relevant_by_text = True
        if keyword_hint:
             is_relevant_by_text = any(part in link_text_lower for part in hint_parts if len(part) > 2)

        # Basic filtering for links that might be job postings
        if is_relevant_by_text and ('job' in href or 'career' in href or 'position' in href or 'opening' in href):
            full_url = href
            parsed_base_url = urllib.parse.urlparse(base_url)
            if href.startswith('/'):
                full_url = f"{parsed_base_url.scheme}://{parsed_base_url.netloc}{href}"
            
            if full_url not in job_links:
                job_links.append(full_url)
                print(f"Found potential job link: {full_url}")

    if not job_links:
        print(f"No specific job links found on {base_url} using current generic selectors.")
        # print(f"Page content (first 500 chars): {response.text[:500]}") # For debugging
    return job_links

if __name__ == "__main__":
    output_csv_file = 'company_career_urls_output.csv'
    new_companies_input_csv = 'HiringTechCompanies - TheList.csv'
    
    print(f"Merging companies from '{new_companies_input_csv}' into '{output_csv_file}'...")
    
    companies_with_urls, companies_needing_urls = merge_and_update_career_urls(
        output_filepath=output_csv_file,
        new_companies_list_filepath=new_companies_input_csv
    )
    
    print(f"\nConsolidated list in '{output_csv_file}' is ready.")
    print("Next steps would be to find career page URLs for the companies listed as 'needing URLs'.")
