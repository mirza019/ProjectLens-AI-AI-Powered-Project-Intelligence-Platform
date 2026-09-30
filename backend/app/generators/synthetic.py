import random
from datetime import date

NAMES=["Aurora","Orion","Atlas","Nova","Summit","Harbor","Cascade","Vega","Pioneer","Horizon","Nimbus","Helios","Cobalt","Keystone","Terra","Zenith","Argon","Aquila","Meridian","Solstice","Ember","Vertex","Falcon","Polaris","Delta","Canyon","Odyssey","Sterling","Phoenix","Everest"]
CUSTOMERS=["Northstar Utilities","Vertex Infrastructure","Apex Grid Partners","Meridian Engineering","Continental Works","Bluewater Systems"]
REGIONS=["Europe","Americas","Middle East","Asia Pacific"]
def generate_projects(seed=42,count=30):
    rng=random.Random(seed); rows=[]
    for i,name in enumerate(NAMES[:count]):
        value=rng.randint(5,150)*1_000_000; completion=rng.randint(22,91); event=rng.random()<.36
        delay=rng.randint(8,35) if event else rng.randint(0,5); budget=value*rng.uniform(.67,.83)
        overrun=budget*rng.uniform(.015,.075) if event else budget*rng.uniform(-.025,.012); forecast=budget+overrun
        margin=(value-forecast)/value*100
        rows.append({"code":f"PL-{2401+i}","name":f"Project {name}","customer":CUSTOMERS[i%len(CUSTOMERS)],"region":REGIONS[i%len(REGIONS)],"value":value,"completion":completion,"budget_cost":round(budget,2),"forecast_cost":round(forecast,2),"expected_margin":round(margin,2),"schedule_days":delay,"root_cause":"Supplier delay" if event else None})
    return rows

