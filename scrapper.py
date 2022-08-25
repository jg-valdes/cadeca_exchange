import requests
from decouple import config
from bs4 import BeautifulSoup

env_selectors = dict()
CURRENCIES = {
    "CAD": "Dólar Canadiense",
    "CHF": "Franco Suizo",
    "EUR": "Euro",
    "GBP": "Libra Esterlina",
    "JYP": "Yuan Japonés",
    "MXM": "Pesos Mexicanos",
    "USD": "Dólar Americano",
    "MLC": "MLC :("
}


def load_env_selectors():
    """Load environment settings for scrap web"""
    env_selectors.update({
        "main_block_id": config("MAIN_BLOCK_ID", default="block-quicktabs-m-dulo-tasa-de-cambio"),
        "widget_block_id": config("WIDGET_BLOCK_ID", default="block-views-m-dulo-tasa-de-cambio-block"),
        "base_url": config("BASE_URL", default="https://www.cadeca.cu/")
    })


def print_error_message(msg=None):
    """Prints standard error message if any error occur on parsing data

        :param msg: string customized message to print
    """
    if not msg:
        msg = "ERROR: No podemos leer el contenido de la página"
    print(msg)


def process_html(page_content):
    """
    Process html content to extract exchange rates and print in human-readable

        :param page_content: str html page content to process
    """
    if not page_content:
        print_error_message("ERROR: contenido vacío")
        return

    soup = BeautifulSoup(page_content, "html.parser")
    block = soup.find(id=env_selectors.get("main_block_id"))
    if not block:
        print_error_message()
    else:
        widget = block.find(id=env_selectors.get("widget_block_id"))
        if not widget:
            print_error_message()
        else:
            print(f"{'Moneda':>20}", f"{'Signo':>5}", f"{'Compra':>10}", f"{'Venta':>10}")
            for currency_sign, currency_name in CURRENCIES.items():
                tr = widget.find_next("tr", class_=currency_sign)
                if tr:
                    tds = tr.find_all("td")
                    if len(tds) == 4:
                        buy_price = tds[2].text.strip()
                        sale_price = tds[3].text.strip()
                        print(f"{currency_name:>20}", f"{currency_sign:>5}", f"{buy_price:>10}", f"{sale_price:>10}")


##################
# Running script #
##################

# First load environment settings
load_env_selectors()

print("======= Start parsing wait a few seconds =======")

URL = env_selectors.get("base_url")
page = None
try:
    page = requests.get(URL)
except Exception as e:
    print_error_message("Some problem has occur, you need to reload.")
    print("------------------------")
    print(e.__str__())

if page:
    process_html(page.content)
else:
    print_error_message()