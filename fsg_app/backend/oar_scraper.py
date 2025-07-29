import json
import re

from selenium import webdriver
from selenium.webdriver.common.by import By

# Setup webdriver
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)


# Starting division number. Could add more if needed.
division_num = [722]

fsg_data = []

# For getting crime data.
for division in division_num:
    url = f"https://secure.sos.state.or.us/oard/displayDivisionRules.action?selectedDivision={division}"
    # It is at 10, so I can solve CAPTCHA.
    driver.implicitly_wait(15)
    driver.get(url)

    rules = driver.find_elements(By.CLASS_NAME, "rule_div")

    # Obtain crime rankings, statute, crime name, and ranking factors.
    rank_i = 1
    for rule in rules:
        # For division 722
        if division == 722:
            # Get rankings.
            ranking_text = rule.find_element(
                By.XPATH, f'//*[@id="content"]/div[{rank_i}]/p[1]/strong[2]'
            ).text
            ranking_list = ranking_text.split()
            if ranking_list[-1].isdecimal():
                ranking = ranking_list[-1]
                # print(ranking)
            else:
                # Skips first rule 213-018-0000
                rank_i += 1
                continue

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
                felony_class = re.search(r"[–—]\s\(([A-Z])\)", crime_line)
                felony_class = felony_class.group(1)
                ranking_language = None
                # print(ors, "-", crime_name, felony_class)

                fsg_data.append(
                    {
                        "crime_name": crime_name,
                        "ors": ors,
                        "felony_class": felony_class,
                        "ranking": ranking,
                        "ranking_language": ranking_language,
                    }
                )

            else:
                # TODO refactor to a function the ors, crime_name, felony_class search and assignment.
                ors_i = 1
                crime_line = rule.find_elements(
                    By.XPATH, f'//*[@id="content"]/div[{rank_i}]/p/span'
                )
                for line in crime_line:
                    # Exception for a odd line (ORS 163.115 Attempted Murder II)
                    if "ORS 163.115" in line.text:
                        fsg_data.append(
                            {
                                "crime_name": "ATTEMPTED MURDER II",
                                "ors": "163.115",
                                "felony_class": "A",
                                "ranking": "9",
                                "ranking_language": None,
                            }
                        )

                        continue

                    # Exception for odd line (ORS 164.405 & 164.415 Robb1 and Robb2)
                    # TODO this isn't working. It isn't getting them.
                    elif "ORS 164.405" in line.text or "ORS 164.415" in line.text:
                        ors = re.search(r"\b\d{2,3}\.\d{3}", line.text)
                        crime_name = re.search(
                            r"(\b\d{2,3}\.\d{3})\s(\w+\s\w+)\s", line.text
                        )
                        felony_class = re.search(r"[–—-]+\s*\(([A-Z])\)", line.text)
                        if ors and crime_name and felony_class:
                            crime_name = crime_name.group(2).strip()
                            ors = ors[0]
                            felony_class = felony_class.group(1)
                            ranking = 9
                            ranking_language = None
                            print(ors, "-", crime_name, "class", felony_class)

                        else:
                            print(f"Line missing data: {line.text}")

                        # continue

                    # Exception for ORS 163.187 (Strangulation), ranking 6.
                    elif "ORS 163.187" in line.text and ranking == "6":
                        fsg_data.append(
                            {
                                "crime_name": "STRANGULATION (FELONY)",
                                "ors": "ORS 163.187(4)(a) - (b) and (d) – (g)",
                                "ranking": "6",
                                "felony_class": "C",
                                "ranking_language": None,
                            }
                        )

                        continue

                    # For all non-excepted ORSs.
                    elif re.search(r"ORS\s\d", line.text):
                        ors = re.search(r"\b\d{2,3}\.\d{3}[\(\)\w]*", line.text)
                        crime_name = re.search(r"[–—]\s*([A-Z\s\-.,()&/]+)", line.text)
                        felony_class = re.search(r"[–—-]+\s*\(([A-Z])\)", line.text)
                        ranking_language = re.search(
                            r"(\([ABC]\)\.\s\(*)([\w\s\d\(\)\$,]*\.*)(; otherwise)*",
                            line.text,
                        )
                        # ranking_language = re.search(
                        #     r"(\([ABC]\)\.\s\(*)([\w\s\d\(\)\$]*\.*)(; otherwise)*",
                        #     line.text,
                        # )
                        if ors and crime_name and felony_class:
                            crime_name = crime_name.group(1).strip()
                            ors = ors[0]
                            felony_class = felony_class.group(1)
                            if ranking_language:
                                ranking_language = ranking_language.group(2).strip()
                            else:
                                ranking_language = None
                            # print(
                            #     ors,
                            #     "-",
                            #     crime_name,
                            #     "class",
                            #     felony_class,
                            #     "--",
                            #     ranking_language,
                            # )

                        else:
                            print(f"Line missing data: {line.text}")

                    else:
                        # If line didn't meet any criteria; prevents duplicate entries.
                        continue

                    fsg_data.append(
                        {
                            "crime_name": crime_name,
                            "ors": ors,
                            "felony_class": felony_class,
                            "ranking": ranking,
                            "ranking_language": ranking_language,
                        }
                    )
        rank_i += 1

        if division == 724:
            # Get rankings.
            ranking_text = rule.find_element(
                By.XPATH, f'//*[@id="content"]/div[{rank_i}]/p[1]/strong[2]'
            ).text
            ranking_list = ranking_text.split()
            if ranking_list[2].isdecimal():
                ranking = ranking_list[-1]
                # print(ranking)

            # Get ORS and crime name
            # TODO need to finish the parsing for division 724. THIS ISN"T WORKING YET!
            ors_i = 2
            crime_line = rule.find_elements(
                By.XPATH, f'//*[@id="content"]/div[{rank_i}]/p/span'
            )
            ors = re.search(r"\b\d{2,3}\.\d{3}", crime_line)
            crime_name = re.search(
                r"\d{2,3}\.\d{3}\s*—\s*([a-zA-Z\s]+?)(?=\*?\s*—)", crime_line
            )
            crime_name = crime_name.group(1).strip()
            ors = ors[0]
            felony_class = re.search(r"[–—]\s\(([A-Z])\)", crime_line)
            felony_class = felony_class.group(1)
            # print(ors, "-", crime_name, felony_class)

            fsg_data.append(
                {
                    "crime_name": crime_name,
                    "ors": ors,
                    "felony_class": felony_class,
                    "ranking": ranking,
                    "ranking_language": ranking_language,
                }
            )


# print(f"Final Data: {fsg_data}")
driver.quit()

# content > div > p:nth-child(17)
# Write data to json
# json_data = json.dumps(fsg_data)
with open("data/fsg_data.json", "w") as f:
    json.dump(fsg_data, f, indent=2)
