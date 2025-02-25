import re,urllib,os,socket,sys
from moduleBS import BeautifulSoup
import urlparse
from dtectcolors import Style,Fore,Back,init 
init()
if os.name == 'nt':
	os.system('cls')
else:
	os.system('clear')

d4rk = 0
dr1 = "D4rk "


# -- Colors Start -- 
boldwhite 		= 		Style.BRIGHT+Fore.WHITE
boldgrey		=		Style.DIM+Fore.WHITE
reset 			= 		Style.RESET_ALL
green			=		Style.BRIGHT+Fore.GREEN
lightgreen		=		Fore.GREEN
red 			=		Fore.RED 
boldred			=		Style.BRIGHT+Fore.RED
# -- Colors End -- 


# -- Switches Start -- 
wpenumerator	=		"off"
filedetector	=  		"off"
headercheck		= 	 	"on"
subdomainscan	=		"off"
portscan 		= 		"off"
wpscan 			= 		"off"
xssscanner		= 		"off"
wpbackupscan	=		"off"
sqliscanner		=		"off"
# -- Swiches End --


def dtect():
	print("  ____   _____ _____ ____ _____ ")
	print(" |  _ \ |_   _| ____/ ___|_   _|")
	print(" | | | |__| | |  _|| |     | |  ")
	print(" | |_| |__| | | |__| |___  | |  ")
	print(" |____/   |_| |_____\____| |_|  v1.0")
	print("") 
	print(" D-TECT - Pentest the Modern Web")
	print(" Author: Shawar Khan - ( https://shawarkhan.com )")
	print("")
	def menu():
		global filedetector,wpenumerator,subdomainscan,portscan,wpscan,xssscanner,wpbackupscan,sqliscanner
		print(" -- "+boldwhite+"Menu"+reset+" -- \n \n  1. 	"+boldwhite+"WordPress Username Enumerator"+reset+"   \n  2. 	"+boldwhite+"Sensitive File Detector"+reset+"        \n  3. 	"+boldwhite+"Sub-Domain Scanner"+reset+"\n  4. 	"+boldwhite+"Port Scanner"+reset+"        \n  5. 	"+boldwhite+"Wordpress Scanner\n"+reset+"  6. 	"+boldwhite+"Cross-Site Scripting [ XSS ] Scanner\n"+reset+"  7.    "+boldwhite+"Wordpress Backup Grabber\n"+reset+"  8.    "+boldwhite+"SQL Injection [ SQLI ] Scanner\n"+reset)
		option = raw_input("[+] Select Option\n    > ")
		if option == "1":
			wpenumerator = "on"
		elif option == "2":
			filedetector = "on"
		elif option == "3":
			subdomainscan = "on"
		elif option == "4":
			portscan = "on"
		elif option == "5":
			wpscan = "on"
		elif option == "6":
			xssscanner = "on"
		elif option == "7":
			wpbackupscan = "on"
		elif option == "8":
			sqliscanner = "on"
		else:
			print("[+] Incorrect Option selected")
			menu()

	def sock(i,secretswitch=0):
		secret = secretswitch
		global data,page,sourcecode
		if redirect == 1:
			data = host+i
		else:
			data = host.strip("/")+'/'+i
		page = urllib.urlopen(data)
		sourcecode = page.read()
		if secret == "1":
			return sourcecode
	def cloudflare():
		data = host #+'/'
		page = urllib.urlopen(data)
		pagesource = page.read()
		if "used CloudFlare to restrict access</title>" in pagesource:
			print("[!] Cloudflare blocked the IP")
			again()
	def alive():
		try:
			global page,splithost,ip
			data = host#+'/'
			page = urllib.urlopen(data)
			source = page.read()
			splithost = str(data.split("://")[1].split("/")[0])
			ip = socket.gethostbyname(splithost)
			print("[i] "+green+"Site is up!"+reset)
			print("  \n[+] Target Info:\n | URL: "+boldwhite+"%s"+reset+"\n | IP: "+boldwhite+"%s"+reset+"\n  ")%(data,ip)
			print("[+] Checking if any Cloudflare is blocking access...")
			cloudflare()
			redirectcheck()
		except(IOError):
			print("[!] "+red+"Error connecting to site! Site maybe down."+reset)
			again()
	def responseheadercheck():
		print('')
		headers 		= ['set-cookie','x-cache','Location','Date','Content-Type','Content-Length','Connection','Etag','Expires','Last-Modified','Pragma','Vary','Cache-Control','X-Pingback','Accept-Ranges']
		headersfound 	= []
		interesting 	= []
		caution 		= []
		cj = 0
		for i in page.headers:
			if i.lower() in str(headers).lower():
				pass
			elif i == "server":
				structure = str(i)+" : "+str(page.headers[i])
				headersfound.append(structure)
				structure = "Server : "+boldwhite+str(page.headers[i])+reset
				interesting.append(structure)
			elif i == "x-powered-by":
				structure = str(i)+" : "+str(page.headers[i])
				headersfound.append(structure)
				structure = "Powered by: "+boldwhite+str(page.headers[i])+reset
				interesting.append(structure)
			elif i == "x-frame-options":
				cj = 1
				pass
			else:
				structure = str(i)+" : "+str(page.headers[i])
				headersfound.append(structure)
		if cj == 0:
			caution.append("[!]"+red+" X-Frame-Options header Missing\n"+reset+"[!] "+red+"Page might be vulnerable to "+boldred+"Click Jacking\n"+reset+"[!] "+boldred+page.geturl()+reset+"\n[i] About ClickJacking: [ "+green+"https://www.owasp.org/index.php/Clickjacking"+reset+" ]")
		print("[+] Interesting Headers Found:")
		for i in headersfound:
			print(" | %s")%(i)
		if len(interesting) != 0:
			print("\n[i] Information from Headers:")
			for i in interesting:
				print(" | %s")%i
		print('')
		if cj == 0:
			print(caution[0])
		print('')
	def parameterarrange(payload):
		parsedurl = urlparse.urlparse(host)
		parameters = urlparse.parse_qsl(parsedurl.query, keep_blank_values=True)
		parameternames = []
		parametervalues = []

		for m in parameters:
			parameternames.append(m[0])
			parametervalues.append(m[1])


		for n in parameters:
			try:
				print("Checking '%s' parameter")%n[0]
				index = parameternames.index(n[0])
				original = parametervalues[index]
				parametervalues[index] = payload
				return urllib.urlencode(dict(zip(parameternames,parametervalues)))
				parametervalues[index] = original
			except(KeyError):
				pass
	def SQLIscan(site):
		print("[+] [ SQLI ] Scanner Started...\n")
		vuln = []
		payloads = {
					'2':'"',
					'1':'\''
		}
		errors = {
					'MySQL':'You have an error in your SQL syntax;',
					'Oracle':'SQL command not properly ended',
					'MSSQL':'Unclosed quotation mark after the character string',
					'PostgreSQL':'syntax error at or near'
		}
		path = urlparse.urlparse(site).scheme+"://"+urlparse.urlparse(site).netloc+urlparse.urlparse(site).path
		parsedurl = urlparse.urlparse(host)
		parameters = urlparse.parse_qsl(parsedurl.query, keep_blank_values=True)
		parameternames = []
		parametervalues = []

		for m in parameters:
			parameternames.append(m[0])
			parametervalues.append(m[1])


		for n in parameters:
			found = 0
			print("[+] Checking '%s' parameter")%n[0]
			try:
				for i in payloads:	
					pay = payloads[i]
					index = parameternames.index(n[0])
					original = parametervalues[index]
					parametervalues[index] = pay
					modifiedurl = urllib.urlencode(dict(zip(parameternames,parametervalues)))
					parametervalues[index] = original
					modifiedparams = modifiedurl
					payload = urllib.quote_plus(payloads[i])
					u = urllib.urlopen(path+"?"+modifiedparams)
					source = u.read()
					#print ("[+] Checking HTML Context...")
					
					for i in errors:
						if errors[i] in source:#htmlcode[0].contents[0]:
							dbfound = " | Back-End Database: "+green+str(i)+reset
							found = 1
							break
					if found != 1:
						break
			except(KeyError):
				pass

			if found == 1:
				print("[!] "+red+"SQL Injection Vulnerability Found!"+reset)
				print(dbfound)
				vuln.append("'"+n[0]+"'")
				found = 0
		if len(vuln) != 0:
			print(" | Vulnerable Parameter/s:"), 
			for i in vuln:
				print(i),

		else:
			print("[!] Not Vulnerable")
	def XSSscan(site):
		print("[+] [ XSS ] Scanner Started...")
		vuln = []
		payloads = {
					'3':'d4rk();"\'\\/}{d4rk',
					'2':'d4rk</script><script>alert(1)</script>d4rk',
					'1':'<d4rk>'
		}
		path = urlparse.urlparse(site).scheme+"://"+urlparse.urlparse(site).netloc+urlparse.urlparse(site).path
		parsedurl = urlparse.urlparse(host)
		parameters = urlparse.parse_qsl(parsedurl.query, keep_blank_values=True)
		parameternames = []
		parametervalues = []

		for m in parameters:
			parameternames.append(m[0])
			parametervalues.append(m[1])


		for n in parameters:
			found = 0
			print(" | Checking '%s' parameter")%n[0]
			try:
				for i in payloads:	
					pay = payloads[i]
					index = parameternames.index(n[0])
					original = parametervalues[index]
					parametervalues[index] = pay
					modifiedurl = urllib.urlencode(dict(zip(parameternames,parametervalues)))
					parametervalues[index] = original
					modifiedparams = modifiedurl
					payload = urllib.quote_plus(payloads[i])
					u = urllib.urlopen(path+"?"+modifiedparams)
					source = u.read()
					code = BeautifulSoup(source)
					if str(i) == str(1):
						#print ("[+] Checking HTML Context...")
						if payloads[i] in source:#htmlcode[0].contents[0]:
							#print("[+] XSS Vulnerability Found.")
							found = 1
					script = code.findAll('script')
					if str(i) == str(3) or str(i) == str(2):
						#print("[+] Checking JS Context...")
						if str(i) == str(3):
							#JS Context
							for p in range(len(script)):
								try:
									if pay in script[p].contents[0]:
										#print("[+] XSS Vulnerability Found")
										found = 1
								except(IndexError):
									pass
						if str(i) == str(2):
							if payloads['2'] in source:
								#	print("[+] XSS Vulnerability Found")
								found = 1
			except(KeyError):
				pass

			if found == 1:
				vuln.append("'"+n[0]+"'")
				found = 0
		if len(vuln) != 0:
			print("[!] "+red+"Vulnerable Parameter/s:"+reset), 
			for i in vuln:
				print(boldred+i+reset),
		else:
			print("[!] Not Vulnerable")
	def portscanner():
		print("[i] Syntax	:	Function")
  		print("    23,80,120	:	Scans Specific Ports, e.g, Scans Port 23,80 and 120")
  		print("    23-80	:	Scans a Range of Ports, e.g, Scans Port from 23 to 80")
  		print("    23   	:	Scans a single port, e.g, Scans Port 23")
  		print("    all  	:	Scans all ports from 20 to 5000")
  		print(" ")
  		portoption = raw_input("[+] Enter Range or Port:\n    > ")
  		wasmultiple		 = 		0
  		wasrange		 = 		0
  		wasone			 =		0
  		if ',' in portoption:
  			wasmultiple = 1
  			multipleport = portoption.split(',')
  			notexpected = 0
  			for i in multipleport:
  				if not str(i).isdigit():
  					print("[!] Incorrect Syntax!")
  					notexpected = 1
  			if notexpected == 1:
  				again()
  			totallength = multipleport
  		elif '-' in portoption:
  			wasrange = 1
  			rangeport = portoption.split('-')
  			totalrange = range(int(rangeport[0]),int(rangeport[1])+1)
  			if len(rangeport) != 2:
  				print("[!] Incorrect Syntax!")
  				again()
  			totallength = totalrange
  		elif portoption == 'all':
  			totallength = range(20,5000)
  		elif portoption.isdigit():
  			wasone = 1
  			oneport = int(portoption)
  			totallength = range(1)
  		else:
  			print("[+] Incorrect Syntax!")
  			again()
		print("[+] Scanning %s Port/s on Target: %s")%(len(totallength),ip)
		ports = 5000
		found = 1
		protocolname = 'tcp'
		progress = 20
		loopcondition = range(20,5000)
		if portoption == 'all':
			loopcondition = range(20,5000)
			ports = 5000
			progress = 20
		elif wasmultiple == 1:
			loopcondition = multipleport
			ports = int(len(multipleport))
			progress = 0 #int(min(multipleport))
		elif wasrange == 1:
			loopcondition = totalrange
			ports = int(rangeport[1])
			progress = int(rangeport[0])-1
		elif wasone == 1:
			onlyport = []
			onlyport.append(portoption)
			loopcondition = onlyport
			progress = 0
			ports = 1
		else:
			loopcondition = range(20,5000)
		for i in loopcondition:
			i = int(i)
			progress += 1
			sys.stdout.write("\r[+] Progress %i / %s ..."% (progress,ports))
			sys.stdout.flush()
			portconnect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			response = portconnect.connect_ex((ip, i))
			if(response == 0) :
				print ('\n | Port: '+boldwhite+'%d'+reset+' \n | Status: '+green+'OPEN'+reset+'\n | Service: '+boldwhite+'%s'+reset+'\n')% (i,socket.getservbyport(i, protocolname))
				found += 1
			portconnect.close()
		if found == 1:
			print("\n | "+red+"No Open Ports Found!"+reset)
	def subdomainscanner():
		
		import sys
		print("\n[+] Subdomain Scanner Start!")
		wordlist = ["mail","localhost","blog","forum","0","01","02","03","1","10","11","12","13","14","15","16","17","18","19","2","20","3","3com","4","5","6","7","8","9","ILMI","a","a.auth-ns","a01","a02","a1","a2","abc","about","ac","academico","acceso","access","accounting","accounts","acid","activestat","ad","adam","adkit","admin","administracion","administrador","administrator","administrators","admins","ads","adserver","adsl","ae","af","affiliate","affiliates","afiliados","ag","agenda","agent","ai","aix","ajax","ak","akamai","al","alabama","alaska","albuquerque","alerts","alpha","alterwind","am","amarillo","americas","an","anaheim","analyzer","announce","announcements","antivirus","ao","ap","apache","apollo","app","app01","app1","apple","application","applications","apps","appserver","aq","ar","archie","arcsight","argentina","arizona","arkansas","arlington","as","as400","asia","asterix","at","athena","atlanta","atlas","att","au","auction","austin","auth","auto","av","aw","ayuda","az","b","b.auth-ns","b01","b02","b1","b2","b2b","b2c","ba","back","backend","backup","baker","bakersfield","balance","balancer","baltimore","banking","bayarea","bb","bbdd","bbs","bd","bdc","be","bea","beta","bf","bg","bh","bi","billing","biz","biztalk","bj","black","blackberry","blogs","blue","bm","bn","bnc","bo","bob","bof","boise","bolsa","border","boston","boulder","boy","br","bravo","brazil","britian","broadcast","broker","bronze","brown","bs","bsd","bsd0","bsd01","bsd02","bsd1","bsd2","bt","bug","buggalo","bugs","bugzilla","build","bulletins","burn","burner","buscador","buy","bv","bw","by","bz","c","c.auth-ns","ca","cache","cafe","calendar","california","call","calvin","canada","canal","canon","careers","catalog","cc","cd","cdburner","cdn","cert","certificates","certify","certserv","certsrv","cf","cg","cgi","ch","channel","channels","charlie","charlotte","chat","chats","chatserver","check","checkpoint","chi","chicago","ci","cims","cincinnati","cisco","citrix","ck","cl","class","classes","classifieds","classroom","cleveland","clicktrack","client","clientes","clients","club","clubs","cluster","clusters","cm","cmail","cms","cn","co","cocoa","code","coldfusion","colombus","colorado","columbus","com","commerce","commerceserver","communigate","community","compaq","compras","con","concentrator","conf","conference","conferencing","confidential","connect","connecticut","consola","console","consult","consultant","consultants","consulting","consumer","contact","content","contracts","core","core0","core01","corp","corpmail","corporate","correo","correoweb","cortafuegos","counterstrike","courses","cr","cricket","crm","crs","cs","cso","css","ct","cu","cust1","cust10","cust100","cust101","cust102","cust103","cust104","cust105","cust106","cust107","cust108","cust109","cust11","cust110","cust111","cust112","cust113","cust114","cust115","cust116","cust117","cust118","cust119","cust12","cust120","cust121","cust122","cust123","cust124","cust125","cust126","cust13","cust14","cust15","cust16","cust17","cust18","cust19","cust2","cust20","cust21","cust22","cust23","cust24","cust25","cust26","cust27","cust28","cust29","cust3","cust30","cust31","cust32","cust33","cust34","cust35","cust36","cust37","cust38","cust39","cust4","cust40","cust41","cust42","cust43","cust44","cust45","cust46","cust47","cust48","cust49","cust5","cust50","cust51","cust52","cust53","cust54","cust55","cust56","cust57","cust58","cust59","cust6","cust60","cust61","cust62","cust63","cust64","cust65","cust66","cust67","cust68","cust69","cust7","cust70","cust71","cust72","cust73","cust74","cust75","cust76","cust77","cust78","cust79","cust8","cust80","cust81","cust82","cust83","cust84","cust85","cust86","cust87","cust88","cust89","cust9","cust90","cust91","cust92","cust93","cust94","cust95","cust96","cust97","cust98","cust99","customer","customers","cv","cvs","cx","cy","cz","d","dallas","data","database","database01","database02","database1","database2","databases","datastore","datos","david","db","db0","db01","db02","db1","db2","dc","de","dealers","dec","def","default","defiant","delaware","dell","delta","delta1","demo","demonstration","demos","denver","depot","des","desarrollo","descargas","design","designer","detroit","dev","dev0","dev01","dev1","devel","develop","developer","developers","development","device","devserver","devsql","dhcp","dial","dialup","digital","dilbert","dir","direct","directory","disc","discovery","discuss","discussion","discussions","disk","disney","distributer","distributers","dj","dk","dm","dmail","dmz","dnews","dns","dns-2","dns0","dns1","dns2","dns3","do","docs","documentacion","documentos","domain","domains","dominio","domino","dominoweb","doom","download","downloads","downtown","dragon","drupal","dsl","dyn","dynamic","dynip","dz","e","e-com","e-commerce","e0","eagle","earth","east","ec","echo","ecom","ecommerce","edi","edu","education","edward","ee","eg","eh","ejemplo","elpaso","email","employees","empresa","empresas","en","enable","eng","eng01","eng1","engine","engineer","engineering","enterprise","epsilon","er","erp","es","esd","esm","espanol","estadisticas","esx","et","eta","europe","events","domain","exchange","exec","extern","external","extranet","f","f5","falcon","farm","faststats","fax","feedback","feeds","fi","field","file","files","fileserv","fileserver","filestore","filter","find","finger","firewall","fix","fixes","fj","fk","fl","flash","florida","flow","fm","fo","foobar","formacion","foro","foros","fortworth","forums","foto","fotos","foundry","fox","foxtrot","fr","france","frank","fred","freebsd","freebsd0","freebsd01","freebsd02","freebsd1","freebsd2","freeware","fresno","front","frontdesk","fs","fsp","ftp","ftp-","ftp0","ftp2","ftp_","ftpserver","fw","fw-1","fw1","fwsm","fwsm0","fwsm01","fwsm1","g","ga","galeria","galerias","galleries","gallery","games","gamma","gandalf","gate","gatekeeper","gateway","gauss","gd","ge","gemini","general","george","georgia","germany","gf","gg","gh","gi","gl","glendale","gm","gmail","gn","go","gold","goldmine","golf","gopher","gp","gq","gr","green","group","groups","groupwise","gs","gsx","gt","gu","guest","gw","gw1","gy","h","hal","halflife","hawaii","hello","help","helpdesk","helponline","henry","hermes","hi","hidden","hk","hm","hn","hobbes","hollywood","home","homebase","homer","honeypot","honolulu","host","host1","host3","host4","host5","hotel","hotjobs","houstin","houston","howto","hp","hpov","hr","ht","http","https","hu","hub","humanresources","i","ia","ias","ibm","ibmdb","id","ida","idaho","ids","ie","iis","il","illinois","im","images","imail","imap","imap4","img","img0","img01","img02","in","inbound","inc","include","incoming","india","indiana","indianapolis","info","informix","inside","install","int","intern","internal","international","internet","intl","intranet","invalid","investor","investors","invia","invio","io","iota","iowa","iplanet","ipmonitor","ipsec","ipsec-gw","iq","ir","irc","ircd","ircserver","ireland","iris","irvine","irving","is","isa","isaserv","isaserver","ism","israel","isync","it","italy","ix","j","japan","java","je","jedi","jm","jo","jobs","john","jp","jrun","juegos","juliet","juliette","juniper","k","kansas","kansascity","kappa","kb","ke","kentucky","kerberos","keynote","kg","kh","ki","kilo","king","km","kn","knowledgebase","knoxville","koe","korea","kp","kr","ks","kw","ky","kz","l","la","lab","laboratory","labs","lambda","lan","laptop","laserjet","lasvegas","launch","lb","lc","ldap","legal","leo","li","lib","library","lima","lincoln","link","linux","linux0","linux01","linux02","linux1","linux2","lista","lists","listserv","listserver","live","lk","load","loadbalancer","local","log","log0","log01","log02","log1","log2","logfile","logfiles","logger","logging","loghost","login","logs","london","longbeach","losangeles","lotus","louisiana","lr","ls","lt","lu","luke","lv","ly","lyris","m","ma","mac","mac1","mac10","mac11","mac2","mac3","mac4","mac5","mach","macintosh","madrid","mail2","mailer","mailgate","mailhost","mailing","maillist","maillists","mailroom","mailserv","mailsite","mailsrv","main","maine","maint","mall","manage","management","manager","manufacturing","map","mapas","maps","marketing","marketplace","mars","marvin","mary","maryland","massachusetts","master","max","mc","mci","md","mdaemon","me","media","member","members","memphis","mercury","merlin","messages","messenger","mg","mgmt","mh","mi","miami","michigan","mickey","midwest","mike","milwaukee","minneapolis","minnesota","mirror","mis","mississippi","missouri","mk","ml","mm","mn","mngt","mo","mobile","mom","monitor","monitoring","montana","moon","moscow","movies","mozart","mp","mp3","mpeg","mpg","mq","mr","mrtg","ms","ms-exchange","ms-sql","msexchange","mssql","mssql0","mssql01","mssql1","mt","mta","mtu","mu","multimedia","music","mv","mw","mx","my","mysql","mysql0","mysql01","mysql1","mz","n","na","name","names","nameserv","nameserver","nas","nashville","nat","nc","nd","nds","ne","nebraska","neptune","net","netapp","netdata","netgear","netmeeting","netscaler","netscreen","netstats","network","nevada","new","newhampshire","newjersey","newmexico","neworleans","news","newsfeed","newsfeeds","newsgroups","newton","newyork","newzealand","nf","ng","nh","ni","nigeria","nj","nl","nm","nms","nntp","no","node","nokia","nombres","nora","north","northcarolina","northdakota","northeast","northwest","noticias","novell","november","np","nr","ns","ns-","ns0","ns01","ns02","ns1","ns2","ns3","ns4","ns5","ns_","nt","nt4","nt40","ntmail","ntp","ntserver","nu","null","nv","ny","nz","o","oakland","ocean","odin","office","offices","oh","ohio","ok","oklahoma","oklahomacity","old","om","omaha","omega","omicron","online","ontario","open","openbsd","openview","operations","ops","ops0","ops01","ops02","ops1","ops2","opsware","or","oracle","orange","order","orders","oregon","orion","orlando","oscar","out","outbound","outgoing","outlook","outside","ov","owa","owa01","owa02","owa1","owa2","ows","oxnard","p","pa","page","pager","pages","paginas","papa","paris","parners","partner","partners","patch","patches","paul","payroll","pbx","pc","pc01","pc1","pc10","pc101","pc11","pc12","pc13","pc14","pc15","pc16","pc17","pc18","pc19","pc2","pc20","pc21","pc22","pc23","pc24","pc25","pc26","pc27","pc28","pc29","pc3","pc30","pc31","pc32","pc33","pc34","pc35","pc36","pc37","pc38","pc39","pc4","pc40","pc41","pc42","pc43","pc44","pc45","pc46","pc47","pc48","pc49","pc5","pc50","pc51","pc52","pc53","pc54","pc55","pc56","pc57","pc58","pc59","pc6","pc60","pc7","pc8","pc9","pcmail","pda","pdc","pe","pegasus","pennsylvania","peoplesoft","personal","pf","pg","pgp","ph","phi","philadelphia","phoenix","phoeniz","phone","phones","photos","pi","pics","pictures","pink","pipex-gw","pittsburgh","pix","pk","pki","pl","plano","platinum","pluto","pm","pm1","pn","po","policy","polls","pop","pop3","portal","portals","portfolio","portland","post","posta","posta01","posta02","posta03","postales","postoffice","ppp1","ppp10","ppp11","ppp12","ppp13","ppp14","ppp15","ppp16","ppp17","ppp18","ppp19","ppp2","ppp20","ppp21","ppp3","ppp4","ppp5","ppp6","ppp7","ppp8","ppp9","pptp","pr","prensa","press","print >> sys.stdout,er","print >> sys.stdout,serv","print >> sys.stdout,server","priv","privacy","private","problemtracker","products","profiles","project","projects","promo","proxy","prueba","pruebas","ps","psi","pss","pt","pub","public","pubs","purple","pw","py","q","qa","qmail","qotd","quake","quebec","queen","quotes","r","r01","r02","r1","r2","ra","radio","radius","rapidsite","raptor","ras","rc","rcs","rd","re","read","realserver","recruiting","red","redhat","ref","reference","reg","register","registro","registry","regs","relay","rem","remote","remstats","reports","research","reseller","reserved","resumenes","rho","rhodeisland","ri","ris","rmi","ro","robert","romeo","root","rose","route","router","router1","rs","rss","rtelnet","rtr","rtr01","rtr1","ru","rune","rw","rwhois","s","s1","s2","sa","sac","sacramento","sadmin","safe","sales","saltlake","sam","san","sanantonio","sandiego","sanfrancisco","sanjose","saskatchewan","saturn","sb","sbs","sc","scanner","schedules","scotland","scotty","sd","se","search","seattle","sec","secret","secure","secured","securid","security","sendmail","seri","serv","serv2","server","server1","servers","service","services","servicio","servidor","setup","sg","sh","shared","sharepoint","shareware","shipping","shop","shoppers","shopping","si","siebel","sierra","sigma","signin","signup","silver","sim","sirius","site","sj","sk","skywalker","sl","slackware","slmail","sm","smc","sms","smtp","smtphost","sn","sniffer","snmp","snmpd","snoopy","snort","so","socal","software","sol","solaris","solutions","soporte","source","sourcecode","sourcesafe","south","southcarolina","southdakota","southeast","southwest","spain","spam","spider","spiderman","splunk","spock","spokane","springfield","sprint >> sys.stdout,","sqa","sql","sql0","sql01","sql1","sql7","sqlserver","squid","sr","ss","ssh","ssl","ssl0","ssl01","ssl1","st","staff","stage","staging","start","stat","static","statistics","stats","stlouis","stock","storage","store","storefront","streaming","stronghold","strongmail","studio","submit","subversion","sun","sun0","sun01","sun02","sun1","sun2","superman","supplier","suppliers","support","sv","sw","sw0","sw01","sw1","sweden","switch","switzerland","sy","sybase","sydney","sysadmin","sysback","syslog","syslogs","system","sz","t","tacoma","taiwan","talk","tampa","tango","tau","tc","tcl","td","team","tech","technology","techsupport","telephone","telephony","telnet","temp","tennessee","terminal","terminalserver","termserv","test","test2k","testbed","testing","testlab","testlinux","testo","testserver","testsite","testsql","testxp","texas","tf","tftp","tg","th","thailand","theta","thor","tienda","tiger","time","titan","tivoli","tj","tk","tm","tn","to","tokyo","toledo","tom","tool","tools","toplayer","toronto","tour","tp","tr","tracker","train","training","transfers","trinidad","trinity","ts","ts1","tt","tucson","tulsa","tumb","tumblr","tunnel","tv","tw","tx","tz","u","ua","uddi","ug","uk","um","uniform","union","unitedkingdom","unitedstates","unix","unixware","update","updates","upload","ups","upsilon","uranus","urchin","us","usa","usenet","user","users","ut","utah","utilities","uy","uz","v","va","vader","vantive","vault","vc","ve","vega","vegas","vend","vendors","venus","vermont","vg","vi","victor","video","videos","viking","violet","vip","virginia","vista","vm","vmserver","vmware","vn","vnc","voice","voicemail","voip","voyager","vpn","vpn0","vpn01","vpn02","vpn1","vpn2","vt","vu","w","w1","w2","w3","wa","wais","wallet","wam","wan","wap","warehouse","washington","wc3","web","webaccess","webadmin","webalizer","webboard","webcache","webcam","webcast","webdev","webdocs","webfarm","webhelp","weblib","weblogic","webmail","webmaster","webproxy","webring","webs","webserv","webserver","webservices","website","websites","websphere","websrv","websrvr","webstats","webstore","websvr","webtrends","welcome","west","westvirginia","wf","whiskey","white","whois","wi","wichita","wiki","wililiam","win","win01","win02","win1","win2","win2000","win2003","win2k","win2k3","windows","windows01","windows02","windows1","windows2","windows2000","windows2003","windowsxp","wingate","winnt","winproxy","wins","winserve","winxp","wire","wireless","wisconsin","wlan","wordpress","work","world","write","ws","ws1","ws10","ws11","ws12","ws13","ws2","ws3","ws4","ws5","ws6","ws7","ws8","ws9","wusage","wv","ww","www","www-","www-01","www-02","www-1","www-2","www-int","www0","www01","www02","www1","www2","www3","www_","wwwchat","wwwdev","wwwmail","wy","wyoming","x","x-ray","xi","xlogan","xmail","xml","xp","y","yankee","ye","yellow","young","yt","yu","z","z-log","za","zebra","zera","zeus","zlog","zm","zulu","zw"]
		progress = 0
		for i in wordlist:
			progress += 1
			sys.stdout.write("\r[+] Progress %i / %s ..."% (progress,len(wordlist)))
			sys.stdout.flush()
			try:
				s = socket.gethostbyname(i+'.'+splithost)
				if (s):
					so = socket.gethostbyname_ex(i+'.'+splithost)
					print("\n[+] Subdomain found!\n | Subdomain: %s.%s \n | Nameserver: %s\n | IP: %s")%(i,splithost,so[0],s)
					if s == '127.0.0.1':
						print("[!] "+red+"Sub-domain is vulnerable to "+boldred+"Same-Site Scripting! "+reset+"\n[!] About Same-Site Scripting:\n[!] [ "+green+"https://www.acunetix.com/vulnerabilities/web/same-site-scripting"+reset+" ] ")
					print('')
			except(socket.gaierror):
				pass
	def enumform(listofIDs,listofnames):
		lengthofnames =  len(max(listofnames, key=len))
		lengthofIDs = len(max(listofIDs, key=len))
		if lengthofnames < 12:
			lengthofnames = 12
		print "[i] "+green+"Found the following Username/s:"+reset
		print "\t+-"+'-'.center(6, '-')+'-+-'+'-'.center(lengthofnames, '-')+"-+"
		print "\t| "+'ID/s'.center(6, ' ')+' | '+'Username/s'.center(lengthofnames, ' ')+" |"
		print "\t+-"+'-'.center(6, '-')+'-+-'+'-'.center(lengthofnames, '-')+"-+"
		for i,d in zip(listofnames,listofIDs):
			print '\t| '+d.center(6, ' ')+" | "+i.center(lengthofnames, ' ')+' |'
		print "\t+-"+'-'.center(6, '-')+'-+-'+'-'.center(lengthofnames, '-')+"-+"
		print("")
	def wpbackupscanner():
		backups = ['wp-config.php~','wp-config.php.txt','wp-config.php.save','.wp-config.php.swp','wp-config.php.swp','wp-config.php.swo','wp-config.php_bak','wp-config.bak','wp-config.php.bak','wp-config.save','wp-config.old','wp-config.php.old','wp-config.php.orig','wp-config.orig','wp-config.php.original','wp-config.original','wp-config.txt']
		print("[+] Scan Started")
		print("[+] Searching Wordpress Backups...")
		print("[?] Note: Press CTRL+C to skip\n  ")
		progress = 0
		backup = []
		backupurl = []
		try:
			for i in backups:
				progress += 1
				sys.stdout.write("\r[+] Progress %i / %s ..."% (progress,len(backups)))
				sys.stdout.flush()
				sock(i)
				if page.getcode() == 200:
					detecting = sock(i,"1")
					if "define('DB_PASSWORD'" in detecting:
						s1 = i
						s2 = data
						backup.append(s1)
						backupurl.append(s2)
		except(KeyboardInterrupt):
			print("\n[+] File detection skipped")
		print('')
		for ifile,iurl in zip(backup,backupurl):
			print("[!] "+boldred+"Backup Found!\n"+reset+" | "+red+"Filename: "+boldred+"%s"+reset+"\n | "+red+"URL: "+boldred+"%s\n"+reset)%(ifile,iurl)
	def wpenumeration():
		import time
		global d4rk,dr1,host
		page = urllib.urlopen(host)
		url = page.geturl()
		if page.geturl() != host:
			print("[i] The remote host redirects to '"+str(url)+"' \n    Following the redirection...")
			host = page.geturl()
		print("\n[+] Scan Started : "+lightgreen+"%s"+reset) % time.strftime("%c")
		print "[+] Enumeration Usernames..."
		T = 33
		found = 0
		listofusernames = []
		listofids = []
		for i in range(30):
			authorlink = host+"?author="+str(i+1)
			url = urllib.urlopen(authorlink)
			source = url.read()
			if url.geturl() == authorlink:
				break
			else:
				com = str(host)+"/author/"
				res = url.geturl()
				res = res.split("/")
				while len(res) >=3:
					res.pop(0)
				listofusernames.append(res[0])
				listofids.append(str(i+1))
				found = 1
		d4rk = dr1+str(1)+str(T)+str(7)
		if found == 0:
			print("[+] "+red+"No Usernames detected"+reset)
		else:
			enumform(listofids,listofusernames)
		print("[+] Enumeration Completed.")
		print("[+] Scan Ended : "+lightgreen+"%s"+reset) % time.strftime("%c")
	def wpscanner():
		print("  \n[+] Detecting Wordpress")
		wp = 0
		i = 'wp-admin/'
		sock(i)
		if "wp-login.php?redirect_to" in page.geturl():
			wp = 1
			print(green+"[i] "+green+"Wordpress Detected!"+reset)
			if wpenumeration == "on":
				wpenumeration()
			else:
				
				wpenumeration()
		if wp == 0:
			i = 'wp-content/index.php'
			sock(i)
			if page.getcode() == 200 and "" in page.read():
				print("[!] "+green+"Wordpress Detected!"+reset)
				wp = 1
				if wpenumeration == "on":
					wpenumeration()
				else:
					wpbackupscanner()
					wpenumeration()
		if wp == 0:
			print("[!] "+red+"No Wordpress Detected"+reset)
	def redirectcheck():
		global redirect,host
		redirect = 0
		print("[+] Checking Redirection")
		page = urllib.urlopen(host)
		url = page.geturl()
		if page.geturl() != host:
			option = raw_input("[i] "+boldgrey+"Host redirects to "+str(url)+reset+" \n    Set this as default Host? [Y/N]:\n    > ")
			if option.lower() == "y":
				host = page.geturl()
				redirect = 1
		else:
			print("[+] URL isn't redirecting")
	def again():
		global wpenumerator,filedetector,subdomainscan,portscan,wpscan,xssscanner,wpbackupscan,sqliscanner
		# -- Switches Reset -- 
		wpenumerator	=		"off"
		filedetector	=  		"off"
		subdomainscan	=		"off"
		portscan 		= 		"off"
		wpscan 			= 		"off"
		xssscanner		= 		"off"
		wpbackupscan	=		"off"
		sqliscanner		=		"off"
		# -- Swiches Reset --
		inp = raw_input("\n[+] [E]xit or launch [A]gain? (e/a)").lower()
		if inp == 'a':
			dtect()
		elif inp == 'e':
			exit()
		else:
			print("[!] Incorrect option selected")
			again()

# -- Program Structure Start -- 
	menu()
	try:
		global host
		host = raw_input("[+] Enter Domain \n    e.g, site.com\n    > ")
		if 'https://' in host:
			pass
		elif 'http://' in host:
			pass
		else:
			host = "http://"+host
		print("[+] Checking Status...")
		alive()
		responseheadercheck()
		if xssscanner == "on":
			XSSscan(host)
		if sqliscanner == "on":
			SQLIscan(host)
		if wpbackupscan == "on":
			wpbackupscanner()
		if filedetector == "on":
			files = ['robots.txt','crossdomain.xml','.htaccess','clientaccesspolicy.xml','infophp.php','log.txt','logs.txt','CHANGELOG.txt','awstats/data/']
			print("[+] Scan Started")
			print("[+] Searching sensitive files...")
			print("[?] Note: Press CTRL+C to skip\n  ")
			try:
				for i in files:
					if i == "awstats/data/":
						sock(i)
						if "<title>Index of /awstats/data</title>" in sourcecode:
							print("[!] awstats detected!\n[!] URL: %s")%(data)
					else:
						sock(i)
						if page.getcode() == 200:
							print("[!] File Found!\n | Name: %s\n | URL: %s\n")%(i,data)
			except(KeyboardInterrupt):
				print("\n[+] File detection skipped")
		if wpenumerator == "on":
			print("  \n[+] Detecting Wordpress")
			wp = 0
			i = 'wp-admin/'
			sock(i)
			if "wp-login.php?redirect_to" in page.geturl():
				wp = 1
				print(green+"[i] "+green+"Wordpress Detected!"+reset)
				wpenumeration()
			if wp == 0:
				i = 'wp-content/index.php'
				sock(i)
				if page.getcode() == 200 and "" in page.read():
					print("[!] "+green+"Wordpress Detected!"+reset)
					wp = 1
					wpenumeration()
			if wp == 0:
				print("[!] "+red+"No Wordpress Detected"+reset)
		if wpscan == "on":
			wpscanner()
		if subdomainscan == "on":
			subdomainscanner()
		if portscan == "on":
			portscanner()
		again()
	except(KeyboardInterrupt) as Exit:
		print("\n[+] Exiting...")
		sys.exit()
# -- Program Structure End --
dtect()
