import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import time
import os
import shutil
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import re

DOWNLOAD_DIR = "/tmp"

def rename_downloaded_file(download_dir, download_path):
    try:
        current_hour = datetime.now().strftime("%H")
        new_file_name = f"PROD-{current_hour}.csv"
        new_file_path = os.path.join(download_dir, new_file_name)
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
        shutil.move(download_path, new_file_path)
        print(f"Arquivo salvo como: {new_file_path}")
        return new_file_path
    except Exception as e:
        print(f"Erro ao renomear o arquivo: {e}")
        return None
    
def rename_downloaded_file2(download_dir, download_path2):
    try:
        current_hour = datetime.now().strftime("%H")
        new_file_name2 = f"WS-{current_hour}.csv"
        new_file_path2 = os.path.join(download_dir, new_file_name2)
        if os.path.exists(new_file_path2):
            os.remove(new_file_path2)
        shutil.move(download_path2, new_file_path2)
        print(f"Arquivo salvo como: {new_file_path2}")
        return new_file_path2
    except Exception as e:
        print(f"Erro ao renomear o arquivo: {e}")
        return None

def rename_downloaded_file3(download_dir, download_path3):
    try:
        current_hour = datetime.now().strftime("%H")
        new_file_name3 = f"IN-{current_hour}.csv"
        new_file_path3 = os.path.join(download_dir, new_file_name3)
        if os.path.exists(new_file_path3):
            os.remove(new_file_path3)
        shutil.move(download_path3, new_file_path3)
        print(f"Arquivo salvo como: {new_file_path3}")
        return new_file_path3
    except Exception as e:
        print(f"Erro ao renomear o arquivo: {e}")
        return None

def update_packing_google_sheets(csv_file_path):
    try:
        if not os.path.exists(csv_file_path):
            print(f"Arquivo {csv_file_path} não encontrado.")
            return
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("hxh.json", scope)
        client = gspread.authorize(creds)
        sheet1 = client.open_by_url("https://docs.google.com/spreadsheets/d/1LZ8WUrgN36Hk39f7qDrsRwvvIy1tRXLVbl3-wSQn-Pc/edit?gid=734921183#gid=734921183")
        worksheet1 = sheet1.worksheet("Base Pending")
        df = pd.read_csv(csv_file_path)
        df = df.fillna("")
        worksheet1.clear()
        worksheet1.update([df.columns.values.tolist()] + df.values.tolist())
        print(f"Arquivo enviado com sucesso para a aba 'Base Pending'.")
        time.sleep(5)
    except Exception as e:
        print(f"Erro durante o processo: {e}")

def update_packing_google_sheets2(csv_file_path2):
    try:
        if not os.path.exists(csv_file_path2):
            print(f"Arquivo {csv_file_path2} não encontrado.")
            return
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("hxh.json", scope)
        client = gspread.authorize(creds)
        sheet1 = client.open_by_url("https://docs.google.com/spreadsheets/d/1LZ8WUrgN36Hk39f7qDrsRwvvIy1tRXLVbl3-wSQn-Pc/edit?gid=734921183#gid=734921183")
        worksheet1 = sheet1.worksheet("Base Handedover")
        df = pd.read_csv(csv_file_path2)
        df = df.fillna("")
        worksheet1.clear()
        worksheet1.update([df.columns.values.tolist()] + df.values.tolist())
        print(f"Arquivo enviado com sucesso para a aba 'Base Handedover'.")
        time.sleep(5)
    except Exception as e:
        print(f"Erro durante o processo: {e}")

async def main():        
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--no-sandbox", "--disable-dev-shm-usage", "--window-size=1920,1080"])
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()
        try:
            # LOGIN
            await page.goto("https://spx.shopee.com.br/")
            await page.wait_for_selector('xpath=//*[@placeholder="Ops ID"]', timeout=15000)
            await page.locator('xpath=//*[@placeholder="Ops ID"]').fill('Ops113074')
            await page.locator('xpath=//*[@placeholder="Senha"]').fill('@Shopee123')
            await page.locator('xpath=/html/body/div[1]/div/div[2]/div/div/div[1]/div[3]/form/div/div/button').click()
            await page.wait_for_timeout(15000)
            try:
                await page.locator('.ssc-dialog-close').click(timeout=5000)
            except:
                print("Nenhum pop-up foi encontrado.")
                await page.keyboard.press("Escape")

            
            # NAVEGAÇÃO E DOWNLOAD 1
            await page.goto("https://spx.shopee.com.br/#/hubLinehaulTrips/trip")
            await page.wait_for_timeout(8000)
            #await page.get_by_role("button", name="Exportar").nth(1).click()   
            await page.get_by_role("button", name="Exportar").nth(0).click()
            #await page.locator("//button[contains(normalize-space(),'Exportar')]").click()  #botao de exportar
            await page.wait_for_timeout(10000)

            # 👉 Botão de download 1
            await page.goto("https://spx.shopee.com.br/#/taskCenter/exportTaskCenter")
            await page.wait_for_timeout(10000)
            # await page.locator('xpath=/html/body/div[1]/div/div[2]/div[1]/div[2]/div[2]/span/div/div').click()
            await page.wait_for_timeout(8000)
            await page.locator("//button[contains(normalize-space(),'Baixar')]").nth(0).click()
            #await page.get_by_role("button", name="Baixar").nth(0).click()
            download = await download_info.value
            download_path = os.path.join(DOWNLOAD_DIR, download.suggested_filename)
            await download.save_as(download_path)
            new_file_path = rename_downloaded_file(DOWNLOAD_DIR, download_path)

            #####################################################################
            
            # NAVEGAÇÃO E DOWNLOAD 2
            await page.goto("https://spx.shopee.com.br/#/hubLinehaulTrips/trip")
            await page.wait_for_timeout(8000)
            await page.locator('xpath=/html[1]/body[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/span[1]').click()
            await page.wait_for_timeout(8000)
            #await page.get_by_role("button", name="Exportar").nth(1).click()   
            await page.get_by_role("button", name="Exportar").nth(0).click()
            #await page.locator("//button[contains(normalize-space(),'Exportar')]").click()  #botao de exportar
            await page.wait_for_timeout(10000)

            # 👉 Botão de download 2
            await page.goto("https://spx.shopee.com.br/#/taskCenter/exportTaskCenter")
            await page.wait_for_timeout(10000)
            #async with page.expect_download() as download_info:
            #await page.locator('xpath=/html/body/div[1]/div/div[2]/div[1]/div[2]/div[2]/span/div/div').click()
            await page.wait_for_timeout(8000)
            await page.get_by_role("button", name="Baixar").nth(0).click()
            download = await download_info.value
            download_path2 = os.path.join(DOWNLOAD_DIR, download.suggested_filename)
            await download.save_as(download_path2)
            new_file_path2 = rename_downloaded_file2(DOWNLOAD_DIR, download_path2)           

            #####################################################################
            
            # Atualizar Google Sheets (opcional)
            if new_file_path:
                update_packing_google_sheets(new_file_path)
                update_packing_google_sheets2(new_file_path2)
                update_packing_google_sheets3(new_file_path3)
                print("Dados atualizados com sucesso.")
        except Exception as e:
            print(f"Erro durante o processo: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())  
