import psutil
import subprocess

pythons_psutil = []
indexerRunning = False

for p in psutil.process_iter():
	try:
		if p.name() == 'indexer':
			indexerRunning = True

			# Process information
			# print p.cmdline()
			# print p.status()

			pythons_psutil.append(p)
	except psutil.Error:
		indexerRunning = False

if indexerRunning is False:
	commandIndexer = "/usr/bin/indexer xenforo_post_delta --rotate && /usr/bin/indexer --merge xenforo_post_blank xenforo_post_delta --rotate"
	proc = subprocess.Popen(commandIndexer, shell=True, stdout=subprocess.PIPE)
	proc.wait()
