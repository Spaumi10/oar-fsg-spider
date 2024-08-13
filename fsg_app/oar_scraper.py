import re
import sqlite3

from selenium import webdriver
from selenium.webdriver.common.by import By

# Setup webdriver
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)

# TODO
"""
You could use a list of the division numbers and loop through them. One problem
with this is that each division will have different rules. You could use a conditional
check though. List is [722, 723, 724, 4730]
"""

# Starting division number.
division_num = 722

url = f"https://secure.sos.state.or.us/oard/displayDivisionRules.action?selectedDivision={division_num}"
driver.implicitly_wait(4)
driver.get(url)

rules = driver.find_elements(By.CLASS_NAME, "rule_div")

fsg_data = []

# Obtain crime rankings, statute, crime name, and ranking factors.
rank_i = 1
for rule in rules:
    if rank_i != 1:
        # Get rankings.
        ranking_text = rule.find_element(
            By.XPATH, f'//*[@id="content"]/div[{rank_i}]/p[1]/strong[2]'
        ).text
        ranking_list = ranking_text.split()
        if ranking_list[-1].isdecimal():
            ranking = ranking_list[-1]

        # Get ORS and crime name
        # Ranking 11 has special path structure.
        if ranking == "11":
            crime_line = rule.find_element(
                By.XPATH, f'//*[@id="content"]/div[2]/p[3]'
            ).text
            ors = re.search(r"\b\d{2,3}\.\d{3}", crime_line)
            crime_name = re.search(
                r"\d{2,3}\.\d{3}\s*—\s*([a-zA-Z\s]+?)(?=\*?\s*—)", crime_line
            )
            crime_name = crime_name.group(1).strip()
            ors = ors[0]
            # print(ors, "-", crime_name)

            new_crime = {'ranking': ranking, 'name': crime_name, 'statute': ors}
            fsg_data.append(new_crime)

        else:
            ors_i = 1
            crime_line = rule.find_elements(
                By.XPATH, f'//*[@id="content"]/div[{rank_i}]/p/span'
            )
            for line in crime_line:
                # Exception for a odd line (ORS 163.115 Attempted Murder II)
                if "ORS 163.115" in line.text:
                    # TODO add code. 
                    continue
                # Exception for odd line (ORS 164.405 & 164.415 Rob1 and Rob2)
                if ("ORS 164.405" or "ORS 164.415") in line.text:
                    # TODO add code 
                    continue
                # Exception for ORS 163.187 (Strangulation), ranking 6.
                if "ORS 163.187" in line.text and ors_i == 5:
                    #TODO add code
                    continue

                if "ORS" in line.text:
                    ors = re.search(r"\b\d{2,3}\.\d{3}", line.text)
                    crime_name = re.search(r"[–—]\s*([A-Z\s\-.,()&/]+)", line.text)
                    if ors and crime_name:
                        crime_name = crime_name.group(1).strip()
                        ors = ors[0]
                        # print(ors, "-", crime_name)

                new_crime = {'ranking': ranking, 'name': crime_name, 'statute': ors}
                fsg_data.append(new_crime)
    rank_i += 1

driver.quit()
