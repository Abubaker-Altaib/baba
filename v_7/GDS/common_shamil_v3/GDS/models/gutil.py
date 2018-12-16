import subprocess

xyt_path = '/opt/gds/common_shamil_v3/GDS/static/src/img/xyt_finger_print'
png_path = '/opt/gds/common_shamil_v3/GDS/static/src/img/emp_finger_print/'


'''
shell command names or excuted pathes

ex : {'mkdir' : 'mkdir'  ,'programe' :  '/path/to/prorame'}
'''
commands = {
	'bozorth' : '/opt/bio/bin/bozorth3' ,
	'mindtct' : '/opt/bio/bin/mindtct' ,

}


'''
responsible of excuting shell commands
'''
class ShellCommand(object):

	def _init_command(self ,programe,  args):
		programe_path = commands[programe]
		cmd = [programe_path]
		for a in args :
			cmd.append(a)
		return cmd


	def execute(self , programe , *arg):
		cmd = self._init_command(programe, arg)		
		ping_process = subprocess.Popen(cmd,stdout=subprocess.PIPE)
		stdout = ping_process.stdout.read()
		return stdout


shell = ShellCommand()


class FingerPrint(object):
	'''usde for compare 2 xyt files and return precentage'''

	''' change file name to full path ex:
			fname = 1 , ext = .png
			then : new name = /some/path/1.png 
	'''
	def _adapt_fname(self , fname , ext=""):
		new_name = fname + extension
		return new_name


	def create_png(self , img_data):
		pass


	def create_xyt(self , fname ):
		filePath = self._adaptFName(fname)
		pass


	def compare(self , name1 ,name2):
		pass



if __name__ == "__main__":pass
	#shell.execute('bozorth' , '/home/hassan/fing/1.xyt' , '/home/hassan/fing/11.xyt')


