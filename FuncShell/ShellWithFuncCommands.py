class ShellWithFuncCommands:
    """run func commands with fsh"""

    @staticmethod
    def name(): return 'func';

    def __init__(self,files,opts): 
        self.commands_in['func']=[ 'run', 'call', 'on' ]

    def run_call(self,*command):
        """call this func method. ex: call module method args"""
        self.run_func_call(command)

    def run_run(self,*command):
        """run this shell command on the hosts. ex: run ls -l | grep kitten.jpg"""
        self.run_shell_command(' '.join(command))

    def run_on(self, *args):
        "select or list the hosts to run on. ex: on httpd*.dc1* # all the webservers in dc1"
        if len(args):
            self.hosts = self.parse_hosts(' '.join(args))
            print "%s hosts selected" % len(self.hosts)
        else:
            print "the following are selected: \n\t%s" % "\n\t".join(self.hosts)


        
