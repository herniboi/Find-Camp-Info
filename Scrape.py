from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
import re
import csv
import inquirer
import os

def phone_format(text):
    res = re.sub(r'\W+', '', text)
    return "(" + res[:3] + ") " + res[3:6] + "-" + res[6:]

def get_camp_info(driver):
    data = []
    has_contact_info = False

    # get camp name
    camp_name = driver.find_element(By.XPATH, "//div[@class = 'title fix']").text

    # get contact name and phone number
    text = driver.find_element(By.XPATH, "//div[@class = 'sidebar-contact fix']/p[1]").text
    split_text = text.splitlines()
    contact_name = " "
    phone_number = " "
    if len(split_text) == 0:
        pass
    elif len(split_text) == 1:
        if any(char.isdigit() for char in split_text[0]):
            contact_name = " "
            phone_number = phone_format(split_text[0])
            has_contact_info = True
        else:
            contact_name = split_text[0]
            phone_number = " "
    else: 
        contact_name = split_text[0]
        phone_number = phone_format(split_text[1])
        has_contact_info = True

    # get emails
    email = driver.find_element(By.XPATH, "//div[@class = 'sidebar-contact fix']/a[2]").text
    if email != "":
        has_contact_info = True

    
    # get camp director name
    text = driver.find_element(By.XPATH, "//div[@class = 'sidebar-contact fix']/p[2]").text
    director_name = " " 
    if text != "Director(s):":
        director_name = text.split(' ', 1)[-1]

    # get camp location
    text = driver.find_element(By.XPATH, "//aside[@class='col-sm-3 sidebar']/address").text
    text_lines = text.splitlines()
    location = text_lines[0] + ", " + text_lines[1]

    # if camp has no contact_info, dont add to list
    if has_contact_info == False:
        return None

    # write to file
    data.append(camp_name)
    data.append(contact_name)
    data.append(phone_number)
    data.append(email)
    data.append(director_name)
    data.append(location)

    return data

def find_camps(driver, elements):
    # scrape list 1 page at a time
    data = []
    for i in range(len(elements)):
        elements = driver.find_elements(By.XPATH, "//div[@class = 'col-sm-4']/a")
        elements[i].click()
        try:
            e = driver.find_element(By.XPATH, "//div[@class = 'title fix']").text
            if e:
                temp = get_camp_info(driver)
                if temp != None:
                    data.append(temp)
        except:    
            pass
        driver.back()
    return data

def main():
    # take input for zip code and radius
    zip = input("What zipcode would you like to search from?: ")
    questions = [
    inquirer.List('radius',
                    message="What is the radius of the search?",
                    choices=['5 miles', '10 miles', '15 miles', '20 miles', '30 miles', '50 miles', '75 miles', '100 miles', 'Any Distance'],
                ),
    ]
    answers = inquirer.prompt(questions)

    # create webdriver object
    driver = webdriver.Chrome()
    
    # get site
    driver.implicitly_wait(5)
    driver.get("https://find.acacamps.org")

    # select camp type
    driver.find_element(By.XPATH, "//label[@for='day_and_overnight']").click()
    driver.find_element(By.XPATH, "//a[@class='buttons camp-type-next']").click()

    # set location settings -> easily changeable
    driver.find_element(By.XPATH, "//div[@class='arrow center-title3 collapsed']").click()
    driver.find_element(By.XPATH, "//label[@for='location_type_distance']/span").click()
    driver.find_element(By.XPATH, "//input[@id='facet_postal_code']").send_keys(zip)
    Select(driver.find_element(By.XPATH, "//select[@id='facet_distance']")).select_by_visible_text(answers["radius"])
    driver.find_element(By.XPATH, "//section[@class='see-result-area text-center fix']/a").click()

    driver.find_element(By.XPATH, "//label[@for='accredited']/span").click()
    # scrape list 1 page at a time
    fields = ["Camp Name", "Contact Name", "Phone Number", "Email", "Director(s)", "Location"]
    with open("camps.csv", 'w', newline='') as csvfile: 
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)

        while True:
            elements = driver.find_elements(By.XPATH, "//div[@class = 'col-sm-4']/a")
            csvwriter.writerows(find_camps(driver, elements))
            try:
                driver.find_element(By.XPATH, "//a[@class = 'pagination-link next']").click()
            except:
                break


    #finish
    driver.close()

    os.system("start EXCEL.EXE camps.csv")

main()