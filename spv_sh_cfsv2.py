# Python 3.7 code to make an animation of the Southern Hemisphere
# Stratospheric Polar Vortex, in terms of 850K isentropic potential
# vorticity
#
# If you have any questions or comments, please contact me at:
# Mathew_Barlow@uml.edu
#
# Uses CFSv2 isentropic data from the NOMADS server
#
# Output is a bunch of png plots that I use Imagemagick to convert
# into a GIF
#
# CAUTION: side effects of reading or using this poorly coded,
# uncommented program may include nausea, hives, and uncontrolled
# weeping.  Good luck!
#

import numpy as np
import matplotlib.pyplot as plt
import requests
import pygrib
import datetime
import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from scipy.ndimage import gaussian_filter

# start date
year1 = '2019'
mon1 = '08'
day1 = '23'
hr1 = '00'

# end date
year2 = '2019'
mon2 = '09'
day2 = '14'
hr2 = '18'


dt = datetime.datetime(int(year1), int(mon1), int(day1), int(hr1))
end = datetime.datetime(int(year2), int(mon2), int(day2), int(hr2))
step = datetime.timedelta(hours=12)

years = []
mons = []
days = []
hours = []

while dt <= end:
    years.append(dt.strftime('%Y'))
    mons.append(dt.strftime('%m'))
    days.append(dt.strftime('%d'))
    hours.append(dt.strftime('%H'))
    dt += step

nt = len(hours)
ny = 361
nx = 720

pv_850_in = np.zeros([ny, nx])
pv_850 = np.zeros([181, nx])
lat = np.zeros([181, nx])
lon = np.zeros([181, nx])

it = 0
while it < nt:

    year = years[it]
    mon = mons[it]
    day = days[it]
    hr = hours[it]

    print(year+mon+day, hr)

    site = 'https://nomads.ncdc.noaa.gov'
    ipvh_section = 'modeldata/cfsv2_analysis_ipvh'
    url = site + '/' + ipvh_section + '/' + year + '/' + year + mon + '/' + \
          year + mon + day + '/' + 'cdas1.t' + hr + 'z.ipvgrbhanl.grib2'
    r = requests.get(url, allow_redirects=True)
    
    fdate = year + ' ' + mon + ' ' + day + ' ' + hr + 'Z'
  

    try:
# why write robust code when you can just give up if it doesn't work?
        open('test.grib2', 'wb').write(r.content)
        file = 'test.grib2'
        grb = pygrib.open(file)
        grb_var = grb.select(name='Potential vorticity')[12] 
        pv_850_in[:] = grb_var.values
        lat_in, lon_in = grb_var.latlons()
        pv_850[:] = pv_850_in[180::, :]
        lat[:] = lat_in[180::, :]
        lon[:] = lon_in[180::, :]
        
        
        lonwrap=np.concatenate((lon,np.full(181,360)[:,None]),axis=1)
        latwrap=np.concatenate((lat, lat[:, 0][:,None]),axis=1)
        pvwrap = np.concatenate((pv_850, pv_850[:, 0][:, None]), axis=1)
        
        pvwrapf = gaussian_filter(pvwrap,sigma=3)
        
        clevs=np.linspace(-1e-3,0,50)
        
        plt.clf()
        ax = plt.axes(projection=ccrs.Orthographic(central_latitude=-90 ))
        plt.contourf(lonwrap,latwrap,pvwrap,clevs,transform=ccrs.PlateCarree(),
                     cmap='plasma',extend='both')
        
        ax.coastlines('50m', linewidth=0.5, color='gray', alpha = 0.5)      
        
        plt.title('Isentropic Potential Vorticity (850K)\n'+fdate)
        plt.text(0.5,-0.05,r'@MathewABarlow', horizontalalignment='center',
                 verticalalignment='center', transform=ax.transAxes)
        
        plt.savefig('hoo'+ '{:04d}'.format(it)+'.png', bbox_inches='tight',
                    dpi=300)
        
    except:
        print('passed')
        pass

    it += 1
