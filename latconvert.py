import requests 
import json

def convert(lat,long):
	url = "https://webapps.bgs.ac.uk/data/webservices/CoordConvert_LL_BNG.cfc?method=LatLongToBNG&lat={}&lon={}".format(lat,long)
	data = json.loads(requests.get(url).content)
	return data['EASTING'], data['NORTHING']


if __name__=="__main__":
	
	f = "C:\\Users\\Jamie\\Desktop\\Dover\\2010Dover.csv"
	new_f = "C:\\Users\\Jamie\\Desktop\\Dover\\2010Dover_East_North.csv"
			
	with open(f, "r") as f1, open(new_f,"w") as f2:
		f2.write("Easting,Northing,Elevation"+"\n")
		for line in f1.readlines()[1:]:
			data = line.split(",")
			lat,lon,elev = data
			e, n = convert(lat,lon)
			f2.write(",".join([str(i) for i in [e,n,elev]])+"\n")
			

