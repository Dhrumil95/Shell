import pexpect
import os
import csv
import sys
import time

sum = 0
failed = 0
print('-----------------start to test-----------------')

if os.path.exists('hw3.c'):
    os.system('gcc -o hw3 hw3.c')
    if os.path.exists('hw3'):
        print('compiled hw3.c successfully: 5')
        sum+=5
        os.system('chmod 775 hw3')
        child = pexpect.spawn('./hw3')
        
        
        #test prompt
        prompt='CS361 >'
        try:
            child.expect(prompt,timeout=3)
            sum += 5
            print('Prompt: 5')
                
        except pexpect.EOF:
            print('your hw3 unexpectedly teminated!')
            child.terminate(True)
            exit()
        except pexpect.TIMEOUT:
            print('Prompt: failed!')
            child.terminate(True)
            exit()
            
        #test pid,status,command(noargs)
        try:
            com_noargs = True
            child.sendline('/bin/ls')
            child.expect(prompt,timeout=3)
            output = child.before.lower()
            if 'pid' in output:
                sum+=5
                print('Print pid: 5')
            else:
                print('Print pid: failed!')
            if 'status' in output:
                sum+=5
                print('Print status: 5')
            else:
                print('Print status: failed!')


            if 'hw3' not in output:
                com_noargs = False
                
            child.sendline('/bin/date')
            child.expect(prompt,timeout=3)
            output = child.before.lower()
            if '2016' not in output:
                com_noargs = False
                
            if com_noargs:
                sum+=20
                print('Runs a command(no args): 20')
            else:
                print('Runs a command(no args): failed')
        except pexpect.EOF:
            failed=True
            print('your hw3 unexpectedly teminated!')
            child.terminate(True)
        except pexpect.TIMEOUT:
            failed=True
            print('test script can not detect next prompt!')
            child.terminate(True)
        
        #test command(with args) using 'ls -l' and 'cat Makefile'
        if failed:
            child = pexpect.spawn('./hw3')
            child.expect(prompt,timeout=3)
            failed = False
        try:
            com_args = True
            child.sendline('/bin/ls -l -a')
            child.expect(prompt,timeout=3)
            if 'total' not in child.before.lower():
                com_args = False
            
            os.system('echo commandwithargs > comargs')
            child.sendline('/bin/cat comargs')
            child.expect(prompt,timeout=3)
            if 'commandwith' not in child.before.lower():
                com_args = False
                
            if com_args:
                sum+=10
                print('Runs a command with args: 10')
            else:
                print('Runs a command with args: failed!')
            os.system('rm comargs')
        except pexpect.EOF:
            failed=True
            print('your hw3 unexpectedly teminated!')
            child.terminate(True)
        except pexpect.TIMEOUT:
            failed=True
            print('test script can not detect next prompt!')
            child.terminate(True)
        
        #test redirect stdout using 'date' and 'cat'
        if failed:
            child = pexpect.spawn('./hw3')
            child.expect(prompt,timeout=3)
            failed = False
        try:
            restdout = True
            child.sendline('/bin/date > fstdout')
            if '>' in prompt:
                child.expect('> fs',timeout=3)
            child.expect(prompt,timeout=3)
            child.sendline('/bin/cat fstdout')
            child.expect(prompt,timeout=3)
            if '2016' not in child.before.lower():
                restdout = False
                
            if restdout:
                sum+=5
                print('Redirects stdout(overwrites file): 5')
            else:
                print('Redirects stdout(overwrites file): failed!')
        except pexpect.EOF:
            failed=True
            print('your hw3 unexpectedly teminated!')
            child.terminate(True)
        except pexpect.TIMEOUT:
            failed=True
            print('test script can not detect next prompt!')
            child.terminate(True)
            
        
        #test redirect stdout append using 'date' and 'cat'
        if failed:
            child = pexpect.spawn('./hw3')
            child.expect(prompt,timeout=3)
            failed = False
        try:
            restdout_app = True
            child.sendline('/bin/ls >> fstdout')
            if '>' in prompt:
                child.expect('>> fs',timeout=3)
            
            child.expect(prompt,timeout=3)
            child.sendline('/bin/cat fstdout')                  
            child.expect(prompt,timeout=3)
            if '2016' not in child.before.lower():
                restdout_app = False
            if 'hw3' not in child.before.lower():
                restdout_app = False
                
            if restdout_app:
                sum+=5
                print('Redirects stdout(appends to file): 5')
            else:
                print('Redirects stdout(appends to file): failed!')
            os.system('rm fstdout')
        except pexpect.EOF:
            failed=True
            print('your hw3 unexpectedly teminated!')
            child.terminate(True)
        except pexpect.TIMEOUT:
            failed=True
            print('test script can not detect next prompt!')
            child.terminate(True)
        
        #test redirect if command has arguments
        if failed:
            child = pexpect.spawn('./hw3')
            child.expect(prompt,timeout=3)
            failed = False
        try:
            restdout_args = True
            child.sendline('/bin/ls -l -a > fstdoutargs')
            if '>' in prompt:
                child.expect('> fs',timeout=3)
            
            child.expect(prompt,timeout=3)
            child.sendline('/bin/cat fstdoutargs')
            child.expect(prompt,timeout=3)
            if 'total' not in child.before.lower():
                restdout_args = False
                
            if restdout_args:
                sum+=5
                print('Redirects works if command has arguments: 5')
            else:
                print('Redirects works if command has arguments: failed!')
            os.system('rm fstdoutargs')
        except pexpect.EOF:
            failed=True
            print('your hw3 unexpectedly teminated!')
            child.terminate(True)
        except pexpect.TIMEOUT:
            failed=True
            print('test script can not detect next prompt!')
            child.terminate(True)
            
        #test redirect stdin
        if failed:
            child = pexpect.spawn('./hw3')
            child.expect(prompt,timeout=3)
            failed = False
        try:
            restdin = True
            os.system('echo -a > fstdin')
            if os.path.exists('fstdin'):
                child.sendline('/bin/ls < fstdin')
                child.expect(prompt,timeout=3)
                
                if 'hw3' not in child.before.lower():
                    restdin = False
                    
                if restdin:
                    sum+=10
                    print('Redirects stdin: 10')
                else:
                    print('Redirects stdin: failed!')
                os.system('rm fstdin')
            else:
                print('Cannot create fstdin file!\n')
        except pexpect.EOF:
            print('your hw3 unexpectedly teminated!')
            child.terminate(True)
            exit()
        except pexpect.TIMEOUT:
            failed=True
            print('test script can not detect next prompt!')
            child.terminate(True)
        
        #test catch sigint
        if failed:
            child = pexpect.spawn('./hw3')
            child.expect(prompt,timeout=3)
            failed = False
        try:
            child.sendcontrol('c')
            child.expect(prompt,timeout=3)
            if 'catch sigint' in child.before.lower():
                sum+=10
                print('catch sigint: 10')
            else:
                print('catch sigint: failed!')

        except pexpect.EOF:
            print('your hw3 unexpectedly teminated!')
            child.terminate(True)
            exit()
        except pexpect.TIMEOUT:
            failed=True
            print('test script can not detect next prompt!')
            child.terminate(True)
            
        #test catch sigstp
        if failed:
            child = pexpect.spawn('./hw3')
            child.expect(prompt,timeout=3)
            failed = False
        try:
            child.sendcontrol('z')
            child.expect(prompt,timeout=3)
            if 'catch sigtstp' in child.before.lower():
                sum+=10
                print('catch sigtstp: 10')
            else:
                print('catch sigtstp: failed!')
            
        except pexpect.EOF:
            print('your hw3 unexpectedly teminated!')
            child.terminate(True)
            exit()
        except pexpect.TIMEOUT:
            failed=True
            print('test script can not detect next prompt!')
            child.terminate(True)
         
        #test exit
        if failed:
            child = pexpect.spawn('./hw3')
            child.expect(prompt,timeout=3)
            failed = False
        try:
            child.sendline('exit')
            if child.expect(pexpect.EOF,timeout=3) == 0:
                sum+=5
                print('exit: 5')
            else:
                print('exit: failed!')
        
        except pexpect.TIMEOUT:
            print('test script can not detect exit(EOF)!')
            child.terminate(True)
            
        #print total score
        print('your total score is: ' + str(sum))
        
    else:
        print('can not compile hw3.c')
else:
    print('there is no hw3.c file')
