import streamlit as st
import requests
import time

# Apollo API Config
APOLLO_API_KEY = "j8O04kuJrcqHGXETikf5LA"
APOLLO_URL = "https://api.apollo.io/api/v1/mixed_people/search"

# Google Custom Search Config
GOOGLE_API_KEY = "AIzaSyAW9QNpEHRJY9Lg1WxzQqqAbIEByY14mTA"
SEARCH_ENGINE_ID = "554a681123a2e48b5"

# Titles to search for (prioritize BD-related roles first)
TARGET_TITLES = [
    "Head of Business Development",
    "Head of Partnerships",
    "Business Development Lead",
    "Business Development",
    "Director of Partnerships",
    "Head of Growth",
    "CEO",
    "Chief Executive Officer"
]

SENIORITY_FILTER = ["c_suite", "vp", "head", "director", "manager"]

# Streamlit App
st.image("logo.png", width=200)
st.title("Domain to Decision Maker")
st.markdown("**An RBV internal tool**")
st.markdown("Enter a list of company domains to get their top contact and LinkedIn profile.")

user_input = st.text_area("Paste domains here (one per line):")

def find_linkedin_profile(query, company=False, index=1):
    search_url = (
        f"https://www.googleapis.com/customsearch/v1"
        f"?key={GOOGLE_API_KEY}"
        f"&cx={SEARCH_ENGINE_ID}"
        f"&q={requests.utils.quote(query)}"
        f"&num=10"
    )
    try:
        res = requests.get(search_url).json()
        urls = [item["link"] for item in res.get("items", [])]
        if company:
            urls = [u for u in urls if "/company/" in u]
        else:
            urls = [u for u in urls if "/in/" in u]
        if index == 0:
            return urls
        elif 0 < index <= len(urls):
            return urls[index - 1]
        else:
            return None
    except Exception as e:
        return None

def get_best_contacts(domain):
    payload = {
        "q_organization_domains_list": [domain],
        "person_titles": TARGET_TITLES,
        "include_similar_titles": False,
        "person_seniorities": SENIORITY_FILTER,
        "page": 1,
        "per_page": 5
    }
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": APOLLO_API_KEY
    }
    try:
        res = requests.post(APOLLO_URL, headers=headers, json=payload)
        if res.status_code == 200:
            people = res.json().get("people", [])
            results = []
            for i, p in enumerate(people[:2]):
                name = f"{p.get('first_name')} {p.get('last_name')}"
                title = p.get("title")
                linkedin = find_linkedin_profile(f"{name} {domain}")
                results.append({
                    "domain": domain,
                    "name": name,
                    "title": title,
                    "linkedin": linkedin or "Not found"
                })
            return results
        return [{"domain": domain, "name": "", "title": "", "linkedin": "Not found"}]
    except Exception as e:
        return [{"domain": domain, "name": "", "title": "", "linkedin": "Error"}]

if st.button("Find Contacts"):
    domains = [d.strip() for d in user_input.strip().splitlines() if d.strip()]
    if not domains:
        st.warning("Please enter at least one domain.")
    else:
        st.info(f"Searching {len(domains)} companies...")
        results = []
        for d in domains:
            with st.spinner(f"Searching {d}..."):
                contact_list = get_best_contacts(d)
                results.extend(contact_list)
                time.sleep(1)

        st.success("Done! Here are the results:")
        for r in results:
    st.write(f"Website: {r['domain']}")
    if r['name'] and r['title']:
        st.write(f"Best Contact: {r['name']}")
        st.write(f"Title: {r['title']}")
        if r['linkedin'] and r['linkedin'] not in ["Not found", "Error"]:
            st.write(f"LinkedIn: {r['linkedin']}")
        else:
            st.write("LinkedIn: Not found")
    else:
        st.write("No contact found.")
    st.markdown("---")
