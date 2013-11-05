from fsh import FuncShell, is_error

"""Func Impoved SHell

a sub-class of fsh that includes less of the features that the author hates
while still re-using the innards of fsh

"""

# kinda plugins.
from ShellWithFuncCommands import ShellWithFuncCommands
from ShellWithSave         import ShellWithSave 

# this class is imported with -M fish
class Shell(FuncShell,ShellWithSave,ShellWithFuncCommands):
    """The shell itself"""
    @staticmethod
    def name(): return 'shell'

    def __init__(self, files, opts):
        self.vars    = {
            # commands are more noisy
            'verbose': True, 
            # run unrecognised things with fsh's parse_and_run before giving up
            'fallback': False,
            # print what's being run
            'trace' : False,
        }
        self.commands = [ 'opt', ]
        self.commands_in = {
            # other classes can pile crap in here, keyed on their "name" 
            'shell': ['opt']
        }
        self.command_sources = {}
        self.last_run_line = '' # set after running the command
    
        # sigh, plugin registration even when they're my super-class

        for c in self.__class__.__bases__:
            if c != type(self):
                c.__init__(self, files, opts)
            try:                        self.command_sources[ c.name() ] = c
            except AttributeError as e: pass

        if self.verbose: # -v 
            self.vars['verbose'] = self.verbose

        if self.vars['verbose']:
            print self.banner(), " Starting: %s" % ', '.join([c.__name__ for c in self.__class__.__bases__ ])
        for k in self.commands_in.keys():
            self.commands.extend( self.commands_in.get(k, [] ))
            # used by the command runner still 

    def fish_version(self): return 'pre'

    def banner(self):
        return "><((\"> Func Improved Shell '%s' plugged into FuncShell %s" % (
            self.fish_version(), FuncShell.version(self)
        )
    def run_help(self,*args,**kwawrts):
        """usage information for Func Improved SHell"""

        print self.banner()
        if self.vars.get('fallback',0):
            print "fsh fallback is enabled, so you can use this:"
            FuncShell.run_help(self,args)

        try:
            c = args[0]
            if c in self.commands: 
                # I should also identify the class it comes from here...
                print "Help for %s\n%s" % (c,getattr(self,"run_%s"%c).__doc__)
        except IndexError as e:
            for name,objclass in self.command_sources.iteritems():
                for c in self.commands_in[name]:
                    try:
                        print "%-10s: %s" % (c,getattr(objclass,"run_%s"%c).__doc__.split("\n",1)[0])
                    except AttributeError as e:
                        print "%-10s: (has no help)" % c
                print "\t\t... from %s: %s" % (name, objclass.__doc__)

    def run_opt(self,*command,**kwargs):
        """set options local to fish
    available options:
        fallback - allow old style fsh commands (? = + and -)
        verbose  - include extra information in output
        trace    - explain how commands are dispatched
        """

        if len(command) == 0: 
            print self.vars
            return
    
        try:
            name, value = command
        except ValueError as e:
            name, value = command[0], True
            if name.endswith('!'):
                name=name.split('!')[0]
                value=False

        if name not in self.vars.keys():
            self.print_error("%s is not one of the options I recognise, try: %s" % ( name, self.vars.keys() ))
        else:
            self.vars[name] = value;


    def prompt(self):
        format = "%s fsh> " 
        if len(self.hosts):
            return format  % len(self.hosts)
        else:
            return format % '(no hosts)'

    def parse_and_run(self, line):
        noisy = self.vars.get('trace',False)
        if noisy: print "running:     %s" %line
        original_line = line
        words = line.split(' ')
        if line.startswith('help'):
            if noisy: print "     ->      %s" % 'help'
            self.run_help(*words[1:])
        elif words[0] in self.commands:
            if noisy: print "     ->      %s" % 'run_..'
            method = getattr(self,'run_%s' % words[0])
            method(*words[1:])
        elif self.vars.get('fallback', False):
            if noisy: print "     ->      %s" % 'fallback'
            FuncShell.parse_and_run(self,line)
        else:
            if noisy: print "     ->      %s" % 'unknown'
            self.print_error("I don't know what to do with '%s' - maybe set opt fallback\nHere's the help:" % line)
            self.run_help(*words[1:])
        self.last_run_line = line

    def print_error(self, *args):
        print 'Err:', (''.join(args)).replace("\n","\nErr: ")
