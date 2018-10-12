all: CS BS user

CS:
	chmod +x CentralServer.py
BS:
	chmod +x BackupServer_new.py
user:
	chmod +x client.py

clean:
	rm -rf BackupServer
	rm -rf CentralServer
