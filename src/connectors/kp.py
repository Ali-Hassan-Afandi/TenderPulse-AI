from .common import generic_links
URL="https://www.kppra.gov.pk/"
def fetch():return generic_links(URL,"Khyber Pakhtunkhwa","KP PPRA",("tender","bid","procurement","download"),120)
