from .common import generic_links
URL="https://gbppra.gov.pk/"
def fetch():return generic_links(URL,"Gilgit-Baltistan","GB PPRA",("tender","bid","procurement","tse-"),100)
