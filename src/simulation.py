import pandas as pd
import random

PROVINCES=["Punjab","Sindh","Khyber Pakhtunkhwa","Balochistan","Federal","AJK","Gilgit-Baltistan"]

def national_simulation(seed=42):
    r=random.Random(seed)
    rows=[]
    for p in PROVINCES:
        opportunities=r.randint(25,140)
        matched=r.randint(8,max(9,opportunities-5))
        rows.append({"Region":p,"Simulated opportunities":opportunities,"Matched":matched,"Avg readiness":r.randint(58,91)})
    return pd.DataFrame(rows)

def yearly_company_demo():
    return pd.DataFrame({
        "Year":[2022,2023,2024,2025,2026],
        "Bids":[12,18,24,31,39],
        "Qualified":[8,13,18,25,32],
        "Awards":[3,5,7,9,11],
        "Revenue (PKR m)":[38,57,83,121,166]
    })
