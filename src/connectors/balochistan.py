from .common import generic_links
URL="https://bppra.gob.pk/"
def fetch():return generic_links(URL,"Balochistan","Balochistan PPRA",("tender","bid","procurement"),120)
