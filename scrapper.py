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
    "MXN": "Pesos Mexicanos",
    "USD": "Dólar Americano"
}


def load_env_selectors():
    """Load environment settings for scrap web"""
    env_selectors.update({
        "main_block_id": config("MAIN_BLOCK_ID", default="block-quicktabs-m-dulo-tasa-de-cambio"),
        "widget_block_id": config("WIDGET_BLOCK_ID", default="block-views-m-dulo-tasa-de-cambio-block"),
        "base_url": config("BASE_URL", default="https://www.cadeca.cu/"),
        "mlc_rate": config("MLC_RATE", default=120)
    })


def print_error_message(msg=None):
    """Prints standard error message if any error occur on parsing data

        :param msg: string customized message to print
    """
    if not msg:
        msg = "ERROR: No podemos leer el contenido de la página"
    print(msg)


def get_mlc_rate():
    return env_selectors.get("mlc_rate")


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
            headers = [
                f"{'Moneda':>20}",
                f"{'Signo':>6}",
                f"{'Compra':>11}",
                f"{'Venta':>11}",
                f"{'~MLC':>9}",
                f"{'~100 MLC':>16}",
                f"{'Total CUP':>12}"
            ]
            print(" ".join(headers))
            mlc_rate = get_mlc_rate()
            for currency_sign, currency_name in CURRENCIES.items():
                tr = widget.find_next("tr", class_=currency_sign)
                if tr:
                    tds = tr.find_all("td")
                    if len(tds) == 4:
                        buy_price = tds[2].text.strip()
                        sale_price = tds[3].text.strip()
                        mlc = float(buy_price)/mlc_rate
                        currency_amount = (100/mlc)
                        total_cup = currency_amount * float(sale_price)
                        row_items = [
                            f"{currency_name:>20}",                        # currency name
                            f"{currency_sign:>6}",                         # currency sigil
                            f"{buy_price:>11}",                            # buy price
                            f"{sale_price:>11}",                           # sale price
                            f"{mlc:>9.5f}",                                # currency equivalent to MLC
                            f"{currency_amount:>12.5f} {currency_sign}",   # total currency needed for 100 MLC
                            f"{total_cup:>12.5f}",                         # total CUP needed for 100 MLC

                        ]
                        print(" ".join(row_items))


##################
# Running script #
##################

# First load environment settings
load_env_selectors()

print("{:#^91}".format(" Estamos parseando la información, espere unos segundos "))

URL = env_selectors.get("base_url")
page = None
try:
    page = requests.get(URL)
except Exception as e:
    print_error_message("Ha ocurrido un problema, necesitas refrescar.")
    print("------------------------")
    print(e.__str__())

if page:
    process_html(page.content)
else:
    print_error_message()