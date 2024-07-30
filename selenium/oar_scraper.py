from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

# TODO
"""
You could use a list of the division numbers and loop through them. One problem
with this is that each division will different rules. You could use a conditional
check though. List is [722, 723, 724, 4730]
"""

# Starting division number.
division_num = 722

url = f"https://secure.sos.state.or.us/oard/displayDivisionRules.action?selectedDivision={division_num}"
driver.implicitly_wait(5)
driver.get(url)

rules = driver.find_elements(By.CLASS_NAME, "rule_div")
