all:
		chmod u+x dnsserver
		vi +':wq ++ff=unix' dnsserver
		chmod u+x httpserver
		vi +':wq ++ff=unix' httpserver
		chmod u+x deployCDN
		vi +':wq ++ff=unix' deployCDN
		chmod u+x runCDN
		vi +':wq ++ff=unix' runCDN
		chmod u+x stopCDN
		vi +':wq ++ff=unix' stopCDN
		
