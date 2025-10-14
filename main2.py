import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import os
import shutil
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

DOWNLOAD_DIR = "/tmp"

# ==============================
# Funções de renomear arquivos
# ==============================
def rename_downloaded_file(download_dir, download_path):
    try:
        current_hour = datetime.now().strftime("%H")
        new_file_name = f"PEND-{current_hour}.csv"
        new_file_path = os.path.join(download_dir, new_file_name)
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
        shutil.move(download_path, new_file_path)
        print(f"Arquivo salvo como: {new_file_path}")
        return new_file_path
    except Exception as e:
        print(f"Erro ao renomear o arquivo: {e}")
        return None

# ==============================
# Funções de renomear arquivos
# ==============================
def rename_downloaded_file2(download_dir, download_path2):
    try:
        current_hour = datetime.now().strftime("%H")
        new_file_name2 = f"PROD-{current_hour}.csv"
        new_file_path2 = os.path.join(download_dir, new_file_name2)
        if os.path.exists(new_file_path2):
            os.remove(new_file_path2)
        shutil.move(download_path2, new_file_path2)
        print(f"Arquivo salvo como: {new_file_path2}")
        return new_file_path
    except Exception as e:
        print(f"Erro ao renomear o arquivo: {e}")
        return None


# ==============================
# Funções de atualização Google Sheets
# ==============================
def update_packing_google_sheets(csv_file_path):
    try:
        if not os.path.exists(csv_file_path):
            print(f"Arquivo {csv_file_path} não encontrado.")
            return
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("hxh.json", scope)
        client = gspread.authorize(creds)
        sheet1 = client.open_by_url(
            "https://docs.google.com/spreadsheets/d/1LZ8WUrgN36Hk39f7qDrsRwvvIy1tRXLVbl3-wSQn-Pc/edit#gid=734921183"
        )
        worksheet1 = sheet1.worksheet("Base Pending")
        df = pd.read_csv(csv_file_path).fillna("")
        worksheet1.clear()
        worksheet1.update([df.columns.values.tolist()] + df.values.tolist())
        print(f"Arquivo enviado com sucesso para a aba 'Base Pending'.")
    except Exception as e:
        print(f"Erro durante o processo: {e}")

# ==============================
# Funções de atualização Google Sheets
# ==============================
def update_packing_google_sheets2(csv_file_path2):
    try:
        if not os.path.exists(csv_file_path2):
            print(f"Arquivo {csv_file_path2} não encontrado.")
            return
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("hxh.json", scope)
        client = gspread.authorize(creds)
        sheet1 = client.open_by_url(
            "https://docs.google.com/spreadsheets/d/1LZ8WUrgN36Hk39f7qDrsRwvvIy1tRXLVbl3-wSQn-Pc/edit#gid=734921183"
        )
        worksheet1 = sheet1.worksheet("Base Handedover")
        df = pd.read_csv(csv_file_path2).fillna("")
        worksheet1.clear()
        worksheet1.update([df.columns.values.tolist()] + df.values.tolist())
        print(f"Arquivo enviado com sucesso para a aba 'Base Pending'.")
    except Exception as e:
        print(f"Erro durante o processo: {e}")
        
# ==============================
# Fluxo principal Playwright
# ==============================
async def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        try:
            # LOGIN (seu código de login aqui...)
            await page.goto("https://spx.shopee.com.br/")
            await page.wait_for_selector('xpath=//*[@placeholder="Ops ID"]', timeout=15000)
            await page.locator('xpath=//*[@placeholder="Ops ID"]').fill('Ops113074')
            await page.locator('xpath=//*[@placeholder="Senha"]').fill('@Shopee123')
            await page.locator('xpath=/html/body/div[1]/div/div[2]/div/div/div[1]/div[3]/form/div/div/button').click()
            await page.wait_for_load_state("networkidle", timeout=20000) # É melhor esperar a página carregar
            
            try:
                await page.locator('.ssc-dialog-close').click(timeout=5000)
            except:
                print("Nenhum pop-up foi encontrado.")
                await page.keyboard.press("Escape")

            # ================== DOWNLOAD 1: PENDING ==================
            print("\nIniciando Download 1: Base Pending")
            await page.goto("https://spx.shopee.com.br/#/hubLinehaulTrips/trip")
            # ATENÇÃO: Substitua esperas fixas por esperas de elementos quando possível
            await page.wait_for_timeout(8000) 
            
            # Clicando no filtro específico para "Pending" (ajuste o seletor se necessário)
            await page.locator('xpath=/html[1]/body[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]').click()
            await page.wait_for_timeout(5000)
            await page.get_by_role("button", name="Exportar").nth(0).click()
            await page.wait_for_timeout(10000)

            await page.goto("https://spx.shopee.com.br/#/taskCenter/exportTaskCenter")
            # Use a lógica de espera robusta que discutimos anteriormente aqui!
            await page.wait_for_timeout(8000)
            
            async with page.expect_download() as download_info:
                await page.get_by_role("button", name="Baixar").nth(0).click()
            
            download = await download_info.value
            download_path = os.path.join(DOWNLOAD_DIR, download.suggested_filename)
            await download.save_as(download_path)

            # Usando a função unificada
            new_file_path = rename_downloaded_file(DOWNLOAD_DIR, download_path, "PEND")
            if new_file_path:
                update_google_sheet(new_file_path, "Base Pending")

            # ================== DOWNLOAD 2: HANDEDOVER ==================
            print("\nIniciando Download 2: Base Handedover")
            await page.goto("https://spx.shopee.com.br/#/hubLinehaulTrips/trip")
            await page.wait_for_timeout(8000)
            
            # Clicando no filtro específico para "Handedover" (ajuste o seletor se necessário)
            await page.locator('xpath=/html[1]/body[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]').click()
            await page.wait_for_timeout(5000)
            await page.get_by_role("button", name="Exportar").nth(0).click()
            await page.wait_for_timeout(10000)

            await page.goto("https://spx.shopee.com.br/#/taskCenter/exportTaskCenter")
            await page.wait_for_timeout(8000)

            async with page.expect_download() as download_info2: # Use uma nova variável para clareza
                # Clica no botão mais recente, que deve ser o da segunda exportação
                await page.get_by_role("button", name="Baixar").nth(0).click()

            download2 = await download_info2.value
            download_path2 = os.path.join(DOWNLOAD_DIR, download2.suggested_filename) # Correção aqui
            await download2.save_as(download_path2)
            
            # Usando a função unificada
            new_file_path2 = rename_downloaded_file(DOWNLOAD_DIR, download_path2, "PROD")
            if new_file_path2:
                update_google_sheet(new_file_path2, "Base Handedover")

            print("\n✅ Processo concluído com sucesso.")

        except Exception as e:
            print(f"❌ Erro fatal durante o processo: {e}")
        finally:
            await browser.close()

# Não se esqueça de adicionar as duas funções unificadas no topo do seu script!
if __name__ == "__main__":
    asyncio.run(main())
