import asyncio  
from playwright.async_api import async_playwright  
from datetime import datetime  
import os  
import shutil  
import gspread  
import pandas as pd  
from oauth2client.service_account import ServiceAccountCredentials  
  
# ==============================  
# CONFIGURAÇÕES GERAIS  
# ==============================  
DOWNLOAD_DIR = "/tmp"  
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1LZ8WUrgN36Hk39f7qDrsRwvvIy1tRXLVbl3-wSQn-Pc/edit#gid=734921183"  
CREDENTIALS_FILE = "hxh.json"  
  
# Planilhas e abas  
SHEETS_CONFIG = {  
    "Base Pending": "https://docs.google.com/spreadsheets/d/1LZ8WUrgN36Hk39f7qDrsRwvvIy1tRXLVbl3-wSQn-Pc/edit#gid=734921183",  
    "Base Handedover": "https://docs.google.com/spreadsheets/d/1LZ8WUrgN36Hk39f7qDrsRwvvIy1tRXLVbl3-wSQn-Pc/edit#gid=734921183"  
}  
  
# Login  
LOGIN_DATA = {  
    "ops_id": "Ops113074",  
    "password": "@Shopee123"  
}  
  
# URLs  
LOGIN_URL = "https://spx.shopee.com.br/"  
EXPORT_URL = "https://spx.shopee.com.br/#/hubLinehaulTrips/trip"  
TASK_CENTER_URL = "https://spx.shopee.com.br/#/taskCenter/exportTaskCenter"  
  
# ==============================  
# Funções de Arquivo  
# ==============================  
def ensure_download_dir():  
    """Garante que o diretório de downloads exista."""  
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)  
  
def rename_downloaded_file(download_dir: str, download_path: str, prefix: str) -> str | None:  
    """  
    Renomeia o arquivo baixado com o formato PROD-XX.csv ou WS-XX.csv.  
    """  
    try:  
        hour = datetime.now().strftime("%H")  
        new_file_name = f"{prefix}-{hour}.csv"  
        new_file_path = os.path.join(download_dir, new_file_name)  
          
        # Remove o arquivo antigo se existir  
        if os.path.exists(new_file_path):  
            os.remove(new_file_path)  
          
        # Move e renomeia  
        shutil.move(download_path, new_file_path)  
        print(f"📁 Arquivo salvo como: {new_file_path}")  
        return new_file_path  
    except Exception as e:  
        print(f"❌ Erro ao renomear arquivo: {e}")  
        return None  
  
# ==============================  
# Funções de Google Sheets  
# ==============================  
def get_gspread_client():  
    """Cria e retorna o cliente gspread com autenticação."""  
    scope = [  
        "https://www.googleapis.com/auth/spreadsheets",  
        "https://www.googleapis.com/auth/drive"  
    ]  
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)  
    return gspread.authorize(creds)  
  
def update_google_sheet(sheet_name: str, csv_file_path: str):  
    """  
    Atualiza a aba do Google Sheets com o conteúdo do CSV.  
    """  
    try:  
        if not os.path.exists(csv_file_path):  
            print(f"❌ Arquivo não encontrado: {csv_file_path}")  
            return  
  
        client = get_gspread_client()  
        sheet = client.open_by_url(SHEETS_CONFIG[sheet_name])  
        worksheet = sheet.worksheet(sheet_name)  
  
        # Lê o CSV e preenche valores vazios  
        df = pd.read_csv(csv_file_path).fillna("")  
  
        # Limpa e atualiza  
        worksheet.clear()  
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())  
  
        print(f"✅ Dados enviados para '{sheet_name}' com sucesso.")  
  
    except Exception as e:  
        print(f"❌ Erro ao atualizar '{sheet_name}': {e}")  
  
# ==============================  
# Fluxo Principal (Playwright)  
# ==============================  
async def main():  
    ensure_download_dir()  
  
    async with async_playwright() as p:  
        # Inicia navegador  
        browser = await p.chromium.launch(  
            headless=False,  
            args=[  
                "--no-sandbox",  
                "--disable-dev-shm-usage",  
                "--window-size=1920,1080"  
            ]  
        )  
        context = await browser.new_context(accept_downloads=True)  
        page = await context.new_page()  
  
        try:  
            # 1. LOGIN  
            print("🔐 Acessando página de login...")  
            await page.goto(LOGIN_URL, timeout=30000)  
            await page.wait_for_selector('xpath=//*[@placeholder="Ops ID"]', timeout=15000)  
  
            await page.fill('xpath=//*[@placeholder="Ops ID"]', LOGIN_DATA["ops_id"])  
            await page.fill('xpath=//*[@placeholder="Senha"]', LOGIN_DATA["password"])  
            await page.click('xpath=/html/body/div[1]/div/div[2]/div/div/div[1]/div[3]/form/div/div/button')  
            await page.wait_for_timeout(15000)  
  
            # Fecha pop-up, se aparecer  
            try:  
                await page.locator('.ssc-dialog-close').click(timeout=5000)  
            except:  
                print("💡 Nenhum pop-up encontrado. Pressionando Escape.")  
                await page.keyboard.press("Escape")  
  
            # 2. DOWNLOAD 1: Base Pending  
            print("📥 Baixando 'Base Pending'...")  
            await page.goto(EXPORT_URL, timeout=20000)  
            await page.wait_for_timeout(8000)  
  
            # Clica no botão Exportar  
            await page.get_by_role("button", name="Exportar").nth(0).click()  
            await page.wait_for_timeout(10000)  
  
            # Vai para a página de exportação  
            await page.goto(TASK_CENTER_URL, timeout=20000)  
            await page.wait_for_timeout(8000)  
  
            # Espera o download  
            async with page.expect_download() as download_info:  
                await page.get_by_role("button", name="Baixar").nth(0).click()  
            download = await download_info.value  
            download_path = os.path.join(DOWNLOAD_DIR, download.suggested_filename)  
            await download.save_as(download_path)  
  
            # Renomeia  
            new_file_path = rename_downloaded_file(DOWNLOAD_DIR, download_path, "PROD")  
            if new_file_path:  
                update_google_sheet("Base Pending", new_file_path)  
  
            # 3. DOWNLOAD 2: Base Handedover  
            print("📥 Baixando 'Base Handedover'...")  
            await page.goto(EXPORT_URL, timeout=20000)  
            await page.wait_for_timeout(8000)  
  
            # Clica no filtro (ex: "Trip Status" ou outro)  
            await page.locator(  
                'xpath=/html[1]/body[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/span[1]'  
            ).click()  
            await page.wait_for_timeout(8000)  
  
            # Exporta  
            await page.get_by_role("button", name="Exportar").nth(0).click()  
            await page.wait_for_timeout(10000)  
  
            # Vai para a página de exportação  
            await page.goto(TASK_CENTER_URL, timeout=20000)  
            await page.wait_for_timeout(8000)  
  
            # Espera o download  
            async with page.expect_download() as download_info:  
                await page.get_by_role("button", name="Baixar").nth(0).click()  
            download2 = await download_info.value  
            download_path2 = os.path.join(DOWNLOAD_DIR, download2.suggested_filename)  
            await download2.save_as(download_path2)  
  
            # Renomeia  
            new_file_path2 = rename_downloaded_file(DOWNLOAD_DIR, download_path2, "WS")  
            if new_file_path2:  
                update_google_sheet("Base Handedover", new_file_path2)  
  
            print("✅ Todos os dados foram atualizados com sucesso.")  
  
        except Exception as e:  
            print(f"❌ Erro durante o processo: {e}")  
  
        finally:  
            await browser.close()  
  
# ==============================  
# EXECUÇÃO  
# ==============================  
if __name__ == "__main__":  
    asyncio.run(main())
