from .common import generic_links
URL="https://www.ajkppra.gov.pk/"
def fetch():return generic_links(URL,"AJK","AJ&K PPRA",("tender","bid","procurement"),100)
