from .common import generic_links
URL="https://ppra.punjab.gov.pk/public_procurement"
def fetch():
    # Punjab's redesigned portal can expose navigation without row data; return only genuine public links found.
    return generic_links(URL,"Punjab","Punjab PPRA",("tender","procurement","epad","bid"),120)
