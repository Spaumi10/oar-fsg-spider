import json
import re

from selenium import webdriver
from selenium.webdriver.common.by import By

# Setup webdriver
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)


# Obtains person crime ORSs.
url = "https://secure.sos.state.or.us/oard/displayDivisionRules.action?selectedDivision=712"
driver.implicitly_wait(3)  # content > div > p:nth-child(17)
driver.get(url)
rule = driver.find_elements(By.CLASS_NAME, "rule_div")[0]

# Get text of person felonies subsection.
text = rule.find_element(By.XPATH, '//*[@id="content"]/div/p[17]').text

# Get person felonies ORSs.
# person_felony_ors = re.findall(r"\b\d{2,3}\w*\.\d{3}(?:\(\d\))*(?:\(\w\)*)*", text)
results = []

person_felony_matches = re.findall(
    r"ORS\s+(\d{2,3}\w*\.\d{3}(?:\(\d+\))*(?:\([a-z]\))*)", text
)

# Add main statutes (remove "ORS " prefix)
for match in person_felony_matches:
    results.append(match)

# Find "and" references and expand them
sections = text.split(";")
for section in sections:
    if "ORS" not in section:
        continue

    # Get the base statute number
    ors_match = re.search(r"ORS\s+(\d{2,3}\w*\.\d{3})(\(\d+\))*", section)
    if ors_match:
        base_number = ors_match.group(1)
        main_subsection = ors_match.group(2) or ""

        # Find "and (1)(d)" type references
        full_and = re.findall(r"and\s+(\(\d+\)\([a-z]\))", section)
        for ref in full_and:
            results.append(f"{base_number}{ref}")

        # Find "and (c)" type references
        simple_and = re.findall(r"and\s+(\([a-z]\))", section)
        for ref in simple_and:
            expanded = f"{base_number}{main_subsection}{ref}"
            if expanded not in results:
                results.append(expanded)

# print(f"Final Data: {fsg_data}")
driver.quit()

with open("data/person_felony_ors.json", "w") as f:
    json.dump(results, f)
