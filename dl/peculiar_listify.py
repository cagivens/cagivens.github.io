# Author:   Caleb Givens
# Date:     1/15/2025
# 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.window import WindowTypes
from selenium.webdriver.firefox.options import Options

import tkinter
from tkinter import filedialog

from tqdm import tqdm

import time

debug = True

def build_csv(data: dict):
    rows = 0
    result = ''
    dict_keys = list(data.keys())

    # Measuring data dictionary
    for key in data:
        if rows < len((data[key])):
            rows = len((data[key]))

    # Building CSV file as string
    for lpn_list in data:
        result += f'{lpn_list},'
    result += '\n'

    j = 0
    for i in tqdm(range(rows), desc='Building CSV'):
        for key in dict_keys:
            if len((data[key])) > j:
                result += f'{(data[key])[j]},'
        j += 1
        result += '\n'
    return result


def get_fcsku(driver: webdriver) -> list:
    # Instantiating FCSku array
    fcsku_array = []

    # Sorting by descending estimated age
    driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[1]/div/div[1]/table/thead/tr[2]/th[2]/span/a').click()
    driver.find_element(By.XPATH, '/html/body/div[4]/div/div[1]/button/i').click()
    time.sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[1]/div/div[1]/table/thead/tr[2]/th[2]/span/a').click()

    # Scraping FCSku IDs from target Peculiar Inventory Bucket
    table_rows = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[1]/div/div[1]/table/tbody').find_elements(By.TAG_NAME, 'tr')
    for web_element in table_rows:
        web_element.find_element(By.TAG_NAME, 'button').click()
        
        # Sorting drawer slide by descending average age
        drawer_slide = driver.find_element(By.ID, 'drawer-slide')
        drawer_slide.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[3]/div/div[2]/div/div/table/thead/tr/th[1]/span/a/i').click()
        drawer_slide.find_element(By.XPATH, '/html/body/div[5]/div/div[1]/button').click()

        # Storing FCSku IDs from drawer-slide web element
        for row in drawer_slide.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr'):
            age = row.find_elements(By.CLASS_NAME, 'textCol')[0].text.replace('d', '').split(' ')[0]
            if int(age) >= 5:
                fcsku = row.find_elements(By.CLASS_NAME, 'textCol')[1].text
                fcsku_array += [fcsku]
                print(f'] Discovered FCSku: {fcsku}')
    return fcsku_array

def research_items(driver: webdriver, fcresearch: str, gravis: str, fc_skus: list) -> dict:
    results = {'CLE3':[], 'ABE3':[], 'UNSELLABLE':[]}
    erroneous_fcsku = []

    # Preparing GRAVIS
    driver.switch_to.window(gravis)
    driver.find_element(By.ID, 'mat-input-0').send_keys('j')
    driver.find_element(By.XPATH, '/html/body/my-app/home/div/div[2]/return-id-search/div/button').click()

    # Preparing FC Research
    driver.switch_to.window(fcresearch)
    driver.find_element(By.XPATH, '//*[@id="search"]').send_keys('j')
    driver.find_element(By.XPATH, '/html/body/div[3]/div/form/span/span/input').click()

    iterations = 1
    # Researching
    for i in tqdm(range(len(fc_skus)), desc='] Researching Items'):

        item = fc_skus[i]
        exists_in_inventory = False
        has_completed_grading = False


        # Searching for the FCSku in FC Research
        driver.find_element(By.XPATH, '//*[@id="search"]').send_keys(item)
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/form/span/span/input').click()

        # Waiting for Inventory table to be loaded
        time_start = time.time()
        research_error = False
        while True:
            try:
                driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/div[6]/div/div[2]/div/div/div[1]/div[2]/table/tbody')
                break
            except:
                if time.time() - time_start > 10:
                    research_error = True
                    erroneous_fcsku += [item]
                    break
                else:
                    continue
        
        # If there was an error locating the LPN of the item, then skip it for now
        if research_error:
            continue
        
        # Getting item LPN
        tableInventoryElement = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/div[6]/div/div[2]/div/div/div[1]/div[2]/table/tbody')
        lpn = tableInventoryElement.find_elements(By.TAG_NAME, 'td')[4].text
        disposition = tableInventoryElement.find_elements(By.TAG_NAME, 'td')[6].text
        owner = tableInventoryElement.find_elements(By.TAG_NAME, 'td')[7].text

        # Researching the item in GRAVIS
        driver.switch_to.window(gravis)
        driver.find_element(By.ID, 'mat-input-1').send_keys(Keys.CONTROL + 'a')
        driver.find_element(By.ID, 'mat-input-1').send_keys(Keys.BACK_SPACE)
        driver.find_element(By.ID, 'mat-input-1').send_keys(lpn)
        driver.find_element(By.XPATH, '/html/body/my-app/mat-toolbar/span[2]/return-id-search/div/button').click()

        try:
            subdest = driver.find_element(By.XPATH, '/html/body/my-app/return-unit-data/div/mat-sidenav-container/mat-sidenav-content/div/div[3]/socrates-last-activity/div/mat-card/div/mat-card-content/table/tbody/tr[2]/td[2]/div/disposition/div/attribute[2]/div').text
        except:
            subdest = 'unknown'            
        #print(f'{iterations} - {lpn}: (Sub-Dest: {subdest}) (Disposition: {disposition}) (Owner: {owner})')
        iterations += 1

        if subdest != 'unknown' and subdest != 'Not Available':
            if 'Unsellable' in subdest:
                results['UNSELLABLE'] += [lpn]
            elif 'Sellable' in subdest or 'CLE3' in subdest:
                results['CLE3'] += [lpn]
            else:
                results['ABE3'] += [lpn]
        else:
            if 'SELLABLE' in disposition:
                results['CLE3'] += [lpn]
            else:
                results['UNSELLABLE'] += [lpn]


        driver.switch_to.window(fcresearch)
    for item in erroneous_fcsku:
        print(f'] ' + '\033[93m' + 'ERROR: Could not find LPN associated with FCSKU [{item}]' + '\033[0m')
    return results

def scrape_dwelling_inventory():
    # Instantiating Webdriver and result array
    driver: webdriver = None
    peculiar_handle = ''
    gravis_handle = ''
    fcr_handle = ''

    print('] Initializing')
    if not debug:
        options = Options()
        options.add_argument('-headless')
        driver = webdriver.Firefox(options=options)
        driver.implicitly_wait(1)
    else:
        driver = webdriver.Firefox()
        driver.implicitly_wait(2)

    # Setting target URLs
    fc_console = 'https://fcmenu-iad-regionalized.corp.amazon.com/PIT4'
    peculiar_overview = 'http://peculiar-inventory-na.aka.corp.amazon.com/PIT4/overview'

    # Logging into FC Console and navigating to Peculiar Inventory
    driver.get(fc_console)
    badge_number = input('] Please scan your badge -> ')
    driver.find_element(By.ID, 'badgeBarcodeId').send_keys(badge_number)
    driver.find_element(By.ID, "badgeBarcodeId").submit()
    time.sleep(1)

    # Opening Peculiar Inventory
    driver.get(peculiar_overview)
    peculiar_handle = driver.current_window_handle

    # Opening Gravis
    driver.switch_to.new_window(WindowTypes.TAB)
    driver.get('https://na-cretfc-tools-iad.iad.proxy.amazon.com/gravis/')
    gravis_handle = driver.current_window_handle
    
    # Opening FC Research
    driver.switch_to.new_window(WindowTypes.TAB)
    driver.get('https://fcresearch-na.aka.amazon.com/PIT4/search')
    fcr_handle = driver.current_window_handle

    # Scraping Inbound Inventory Bucket for FCSku's
    print('] Scraping Inbound Bucket')
    driver.switch_to.window(peculiar_handle)
    driver.get('http://peculiar-inventory-na.aka.corp.amazon.com/PIT4/report/Inbound?timeWindow=MoreThanFiveDay')
    fc_skus = get_fcsku(driver)

    # Scraping Reverse Logistics bucket
    print('] Scraping Reverse Logistics Bucket')
    driver.get('http://peculiar-inventory-na.aka.corp.amazon.com/PIT4/report/ReverseLogistics?timeWindow=MoreThanFiveDay')
    fc_skus += get_fcsku(driver)
    #scrape_bucket(driver, peculiar_handle, fcr_handle, gravis_handle, result)

    # Researching LPNs to determine if they currently exist in inventory
    driver.switch_to.window(fcr_handle)
    result = research_items(driver, fcr_handle, gravis_handle, fc_skus)
    
    driver.quit()
    return result

csv = build_csv(scrape_dwelling_inventory())

root = tkinter.Tk()
root.withdraw()

print('] Writing to file')
f = filedialog.asksaveasfile(mode='w', defaultextension='.csv')
f.write(csv)
f.close()

input('Web scraping complete!\nPress any button to exit... ')