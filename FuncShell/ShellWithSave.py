class ShellWithSave:
    """Allows saving the results of the last command"""
    @staticmethod
    def name(): return 'save'

    def shorten(self,a,context=10):
        """Take a long string (from a func call) and cut it to 3 * context"""
        if len(a) < 2 * context:
            return a
        res = "%s%s%s" % (
            a[:context],
            " ...%s bytes... " % len(a[context:-context])
                if len(a[context:-context])
                else '',
            a[-context:]
        )
        return res.replace("\n",'')

    def __init__(self, files, opts):
        self.commands_in['save']=['save']

    def run_save(self, *command):
        """dump the output of the previous command to a directory
    -e              # only STDERR
    -i              # only STDOUT
    $ok $failed     # only success, only non-success
    /path/to/stuff  # a directory to fill with hostnaed files.
                    # hostname.$exit.STDOUT

files for each minion will be created, one for STDOUT and one for STDERR
each will contain the exit code of the command

TODO: additionally, a file with the host list and command will be created
        """
        command = [x for x in list(command) if x != '' ]
        import os

        flags = dict((x,x in command) for x in ('-e','-i','$ok','$failed') )

        for x in ('-e','-i','$ok','$failed'):
            if x in command:
                flags[ x ] = x
                command.remove(x)

        try:
            path = command[0]
        except IndexError as e:
            print "Err: I need a path to save to. Maybe check help save"
            return 

        try:
            # this likely happens as root :S
            os.makedirs( path )
        except OSError as e:
            if e.errno == 17:
                if self.vars['verbose']:
                    print "I guess it's ok that: %s" % e
            else: raise e

        script = [ '#! /usr/bin/env fsh.py -i' ]
        script.extend([ "+ " + x for x in self.hosts ])
        script.extend([ self.last_run_line, 'save ' + path ,''])
        with open( os.path.join(path,'rerun'), 'w') as f:
            f.write("\n".join(script))

        for host,out in sorted(self.last_result.items()):
            for (idx,type,flag) in (1,'STDOUT','-e'),(2,'STDERR', '-i'):
                filename = os.path.join( path, "%s.%s.%s" % (host,out[0], type))
                if not flags.get( flag, 0):
                    if self.vars.get('verbose',0):
                        print "Writing %s -> %s" % (filename,self.shorten(out[idx]))
                    with open( filename,'w') as f:
                        f.write(str(out[idx]))
                else:
                    if self.vars.get('verbose',0):
                        print "Not writing %s -> %s" % (filename,self.shorten(out[idx]))
        print "results from %s hosts saved to %s" % ( len(self.hosts), path ) 

