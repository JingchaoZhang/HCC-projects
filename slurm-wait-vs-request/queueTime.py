#!/util/opt/anaconda/4.3/envs/python-2.7/bin/python

import os, sys
import csv
import datetime
import re
from optparse import OptionParser
import pylab
import matplotlib.patches as mpatches

if len(sys.argv)<2:
    print('Usage: wt.py -g GROUP -s YYYY-MM-DD')
    sys.exit()

#define campus groups
UNL = 'perez,swanson,starace,elbaum,goddard,jiang,rowe,zeng,seth,reid,costello,ramamurthy,cse496,bahar,choueiry,anderson,jaecks,loope,tsymbal,sayood,srisa-an,jaswal,yang,sellmyer,hoffman,deogun,samal,bobaru,bsbm,cse477,g03,scott,li,dominguez,hibbing,hep,reichenbach,parkhurst,geppert,tuan,gogos,cohen,umstadter,snow,moriyama,jaturner,harbourne,dimagno,soh,batelaan,vcr,belashchenko,gitelson,lu,nowak,feng,ahouston,sicking,harbison,berkowitz,du,pytlikzillig,cse856,bigweather,powers,eckhardt,ducharme,riethoven,shadwick,soulakova,cheung,mech950,lhoffman,lxu,dzenis,woodward,oglesby,han,wood,vinod,vuran,li508,mccutcheon,shield,idb,gay,cse435,fabrikant,kelley,radiology,construction,jbartonme,bockelman,cdrh,sysbio,bloom,bartelthunt,velev,kolbe,cse456,wysocki,tellab,bilder,esquared,vandenbroeke,mnegahban,takacs,dbatur,tenhumberg,rfeng,eemarket,brassil,archcrg,gulinxia,yusongli,colek,nianno,rajca,centurion,machines,markatlnk,balkir,cb3,ebrank,chem484,delong,osg,weberlab,stattools,nimbus,schubert,jockers,rebarber,gates,xuli,psyc943,tvalab,nikolova,juancui,pierolab,haaslab,otu,galaxy,fnal_users,aestructures,jzhang,brittenham,pedhealthlab,jjew1963,schuttelab,jsmyth,mccharguelab,kolson5,bobbelli,crplgisnam,solizrsrch,ebuhs2,dbrainlab,meiklejohn,nsociology,eevak,larios,kovalev,edadhighed,cwsto2,jguo4,fritz,lilab313,bioinfo2014,schachtman,eenji,steelman,geos900,edpsyc,bbrwscgroup,eng2014,farritor,structures,cnelson5,akramlab,nmrlndao,rsacrack,rgroup,nasawrf,cse896,francisco,mathcoding,actuarialsci,cse990,hydraulics,edps971,xuphysics,unlkegg,pilson,fuchs,radcliffe,zgshen,cojmc,qizhangstat,minds,unldr,alexandrov,shizuka,montooth,wpickering,ndtce,atkinlab,zoyalab,osgus,hemsath,riekhoflab,robstein,npodtest,strudynamics,libmediasvcs,serussolab,cematerials,thinklab,gauss,puckett,dmarx,khanford,memshvac,zupan,trlab,juliewucba,codingtheory,ssbio,appliedmath,canlab,snrglab,reachlab,yuill,csong,heritatony,perovskite,zhangchem,buros,christensen,manterlab,commalg,chme412,plantvision,raogroup,alggeom,downes,yingresearch,cse990ying,rcourse998,netthinker,yanggroup,qinghuilab,testgroup02,greeksyntax,unsmgenomics,parklab,celincolnsea,tml2017'
UNO = 'frontiers,combin,primedegconj,drewlab,halll,taylor,kimek,mahesh,unklopers,csit499unk,kovacslab'
UNMC = 'pauley,sabirianov,mfurtney,biocore,unobioinformatics,csci4440,mei,glims,glu,helikar,networks,zhonggroup,uno_cs,uno_biology,unknots,uno_steele,mathbio,kellar,skynet,mathnpdes,uno_iso,swift,mathlab,csci8150,rwong,chase,dmtm2014,collide,biomechanics,aswift,chaselab,isqa8080,cryptouno,glu4class,germonprez,optimization,nporesgrp,econfeng,blankenship,ghersilab,netsim'
UNK = 'smith,unmc_ngs,tahirov,unmc-networking,unmc-ding,norgrenlab,natarajan,luca,kimbioinfo,monaghan,mgarlingfmri,meza,lyubchenko,buchlab,unmc_cbsb,kucuk_c,chanlab,lewis,yu,qiu,oakley,epigenomics,larsonm,unmcresit,bioimaging,cophnayar,bonasera,unmccompen,unmc_com,endocrine,unmc_gudalab,wagnerlab,opavskylab,pavlov,unmcngscore,mottlab,radonc,medphys,mahollin,conda,mcguire,javeediqbal,mohsgroup,greenlab,borgstahl,unmcbiostats,aizenberg,kaifulab,warrenlab'
IANR = 'gladyshev,diestler,deallab,mackenzie,chen,hu,tyre,ladunga,calmit,woldt,subbiah,irmak,mower,shea,walter,calmit-geocomputation,hprcc,fulginiti41,zempleni,samodha,sarath,fulginiti,entomology,amundsen,waters,baenziger,miller,benson,walia,hydro,nielsen,eskridge,lorenz,wtp,drose,jclarke,agrobinf,franz,hutkinslab,compbio,sattler,spangler,jleelab,guru,hallenadams,pblack,rmlewis,ramertait,harrislab,millerburkey,roselab,schachtmanlb,everhartlab,altcropsprec,helikarlab,popcorn,tadesse,coopaquatic,waterforfood,grassini,agriwateruse,chunglab,dbecker,bsesensing,yateslab,sulab,anscgenomics,morota,schnablelab,staswick,stablefly,stroup,nematologytp,lzhang,yzstat,prhpaltar,herrlab,amitmitra,ciobanu,soybean,keen918,vanetten,hgrlab,barletta,roston,adamecgroup,nres879,harris,aliaktar,sathishkumar,yerka,yumouqiu,veghyperspec,unlsbp,gamonlab,cornsoywater,statsgeneral,mieno,mena2016,foodsafety,lindquist,fatttlab,twidwell,alfanolab,howard,cropmodel,zhengxu,asci431,citbpheno,schoengold,stat802,microbiome,qssblab,sinha,cv473,plattebasin,jyanglab'

#parse options
parser = OptionParser()
parser.add_option('-g', '--groups', action='store', dest='group',
	help='one or more group names separated by comma')
parser.add_option('-c', '--campus', action='store', dest='campus',
        help='one or more group names separated by comma (UNL, IANR, UNO, UNMC, UNK)')
parser.add_option('-s', '--start', action='store', dest='time',
	help='query start time in format YYYY-MM-DD')

(options, args) = parser.parse_args()
queryGroup = ''
if options.group != None:
    queryGroup = queryGroup + ',' + options.group

if options.campus != None:
    if 'UNL' in options.campus:
	queryGroup = queryGroup + ',' + UNL
    elif 'UNK' in options.campus:
	queryGroup = queryGroup + ',' + UNK
    elif 'UNO' in options.campus:
	queryGroup = queryGroup + ',' + UNO
    elif 'UNMC' in options.campus:
	queryGroup = queryGroup + ',' + UNMC
    elif 'IANR' in options.campus:
	queryGroup = queryGroup + ',' + IANR

slurmQuery = "sacct -A " + queryGroup + " -P -S " + options.time + " -s CD --noheader -o jobid,group,partition,ReqCPUs,ReqMem,NNodes,Timelimit,Submit,Start | sed '/nfsnobody/d' > tmp.txt"

os.system(slurmQuery)

queryResult = open('query.txt', 'w')

with open("tmp.txt","r") as f:
    reader = csv.reader(f, delimiter="|")
    for row in reader:
	#Waiting Time in hours
	wait = (datetime.datetime.strptime(row[8], '%Y-%m-%dT%H:%M:%S') - datetime.datetime.strptime(row[7], '%Y-%m-%dT%H:%M:%S')).total_seconds() / 3600 # waiting time in hour
	#Memory Usage
	if 'Mc' in row[4]:
	    mem2core = float(filter(str.isdigit, row[4])) * float(row[3]) / 1024 / 4 #(Mb/core) * Ncore / (1024M/G) / (4G/core)
	elif 'Mn' in row[4]:
	    mem2core = float(filter(str.isdigit, row[4])) * float(row[5]) / 1024 / 4
	elif 'Gc' in row[4]:
	    mem2core = float(filter(str.isdigit, row[4])) * float(row[3]) / 4
	elif 'Gn' in row[4]:
	    mem2core = float(filter(str.isdigit, row[4])) * float(row[5]) / 4
	#Mem vs Core. The higher number will be used as the final parameter to calculate CPU Hour
	if float(row[3]) > mem2core:
	    ctotal = float(row[3])
	elif float(row[3]) == mem2core:
	    ctotal = float(row[3])
	elif float(row[3]) < mem2core:
	    ctotal = mem2core
	#Wall Time in hours
	if '-' in row[6]:
	    time = re.split('-|:', row[6])
	    ttotal = float(time[0]) * 24 + float(time[1]) + float(time[2]) / 60 + float(time[3]) / 3600
	else:
	    time = re.split(':|:', row[6])
	    ttotal = float(time[0]) + float(time[1]) / 60 + float(time[2]) / 3600
	#Total CPUHour
	cpuTotal = ttotal * ctotal
	#Write results
	queryResult.write(row[0] + ' ' + row[2] + ' ' + str(cpuTotal) + ' ' + str(wait) + '\n')
	#print (row[0] + ' ' + row[2] + ' ' + str(cpuTotal) + ' ' + str(wait))

os.system("rm -f tmp.txt")
queryResult.close()

#Plot the results
DedicGroups = [ 'starace',
                'abg',
                'bigweather',
                'esquared',
                'tsymbal',
                'ahouston',
                'alexandrov',
                'stats',
                'statsgeneral',
                'francisco',
                'jclarke',
                'zeng',
                'waterforfood',
                'juancui',
                'choueiry',
                'benson',
                'guda',
                'larios',
                'riethoven',
		'devel']
xShare = []
yShare = []
xDedic = []
yDedic = []

with open("query.txt", "rb") as f:
    reader=csv.reader(f, delimiter=' ')
    for row in reader:
        if all(i not in row for i in DedicGroups):
            xShare.append(row[2])
            yShare.append(row[3])
        else:
            xDedic.append(row[2])
            yDedic.append(row[3])

caption = 'Query for ' + queryGroup + ' from ' + options.time + ' to date'
pylab.xlabel('Requested CPU Hours')
pylab.ylabel('Job Queue Time (h)')
pylab.plot(xShare, yShare, 'ro', xDedic, yDedic, 'g^')
red_patch = mpatches.Patch(color='red', label='Shared')
green_patch = mpatches.Patch(color='green', label='Dedicated')
pylab.legend(handles=[red_patch, green_patch])
pylab.suptitle(caption)
pylab.show()
#pylab.savefig('result.png')
