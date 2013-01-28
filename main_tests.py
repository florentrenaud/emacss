'''Test script for EMACSS v2.0. This is princiapally designed to operate as a
stand alone test script for the compiled version of EMACSS. It intends to 
validate EMACSS by confirming the results generated confirm to known values. We aim to have four sections to the validation:

1. Bounds validation - affirms that unreaslistic cluster setups are correctly rejected at input. This also entends to clusters far out of bounds.
 
2. Input validation - confirms that the range of cluster inputs is correctly undersood. This class will also test a) that the default function calls (relaxation time, jacobi radius) are operating correctly, b) that the scaling factors are correctly calculated.

3. Output validation - tests the outputs supplied make sense for the required options.

4. Equal mass runtime validation - tests the output reduced by the code is (within a small tolerance) idential to published results from AG2012. This confirms that the code 'does what it should', and is able to reprodice the evoltuion represented in that paper

Script written 25/01/13 by P. Alexander.
'''

import re, sys, subprocess as sp, numpy as np

class boundaries_tests:
    NTESTS = 0                     #Total number of tests
    NSUCCESS = 0                   #NUmber of successes
    NFAIL = 0                      #Number of failures

    def __init__(self,f):
        print "Initialising Boundaries Tests..."
        self.exe = f

    def __del__(self):
        self.NSUCCESS += 1e-10; self.NFAIL += 1e-10; self.NTESTS += 1e-10
        print "Tests completed."
        print "%i"%self.NSUCCESS,"of %i"%self.NTESTS,"sucessful (%.0f" %(100*(self.NSUCCESS/self.NTESTS)),"%)"
        print "%i"%self.NFAIL,"of %i"%self.NTESTS,"failed (%.0f" %(100*(self.NFAIL/self.NTESTS)),"%)"

    def test_N(self):

      self.NTESTS += 4
      #Checks inner bounds
      N = 101, 1e6-1
      for n in N:
        try:
          sp.check_output([self.exe,"-N",str(n)],stderr=sp.PIPE)
          self.NSUCCESS += 1
        except sp.CalledProcessError:
          self.NFAIL += 1
          print "N boundaries not applied!"

      #Checks outer bounds
      N = 99,1e6+1
      for n in N:
        try:
          sp.check_call([self.exe,"-N",str(n)],stderr=sp.PIPE)
          self.NFAIL += 1
          print "N boundaries not applied!"
        except sp.CalledProcessError:
          self.NSUCCESS += 1

    def test_r(self):

      self.NTESTS += 2
      r = 10                     #Checks a valid radius
      try:
        sp.check_output([self.exe,"-r",str(r)],stderr=sp.PIPE)
        self.NSUCCESS += 1
      except sp.CalledProcessError:
        self.NFAIL += 1
        print "r boundaries not applied!"
      r = 26                     #Checks an invalid radius
      try:
        sp.check_call([self.exe,"-r",str(r)],stderr=sp.PIPE)
        self.NFAIL += 1
        print "r boundaries not applied!"
      except sp.CalledProcessError:
        self.NSUCCESS += 1

    def test_zeta(self):

      self.NTESTS += 3
      zeta = 0.15                #Checks a valid zeta
      try:
        sp.check_output([self.exe,"-z",str(zeta)],stderr=sp.PIPE)
        self.NSUCCESS += 1
      except sp.CalledProcessError:
        self.NFAIL += 1
        print "zeta boundaries not applied!"
      z = -0.1, 1.1              #Checks invalid zetas
      for zeta in z:
        try:
          sp.check_call([self.exe,"-z",str(zeta)],stderr=sp.PIPE)
          self.NFAIL += 1
          print "zeta boundaries not applied!"
        except sp.CalledProcessError:
          self.NSUCCESS += 1

    def test_meta(self):

      self.NTESTS += 5
      flags = 0,1                #Valid flags
      for flag in flags:
        try:
          sp.check_output([self.exe,"-o",str(flag),"-s","0"],stderr=sp.PIPE)
          sp.check_output([self.exe,"-s",str(flag)],stderr=sp.PIPE)
          self.NSUCCESS += 1
        except sp.CalledProcessError:
          self.NFAIL += 1
          print "Flag Error"
      flags = -1,3               #Invalid Flags
      for flag in flags:
        try:
          sp.check_call([self.exe,"-o",str(flag),"-s","0"],stderr=sp.PIPE)
          sp.check_call([self.exe,"-s",str(flag)],stderr=sp.PIPE)
          self.NFAIL += 1
          print "Flag Error"
        except sp.CalledProcessError:
          self.NSUCCESS += 1
      try:                        #Disallowed combo (allowed is implicit in preceeding tests)
          sp.check_call([self.exe,"-o","0","-s","1"],stderr=sp.PIPE)
          self.NFAIL += 1
          print "Flag Exclusion Error"
      except sp.CalledProcessError:
          self.NSUCCESS += 1

    def test_galaxy(self):

      self.NTESTS += 4
      try:
        sp.check_output([self.exe,"-M","-1"],stderr=sp.PIPE)
        self.NFAIL += 1
        print "Galaxy Masses Error"
      except sp.CalledProcessError:
        self.NSUCCESS += 1
      try:
        sp.check_output([self.exe,"-v","-5000"],stderr=sp.PIPE)
        self.NFAIL += 1
        print "Galaxy Orbital Velocity Error"
      except sp.CalledProcessError:
        self.NSUCCESS += 1
      types = -2, 2              #Checks invalid zetas
      for t in types:
        try:
          sp.check_call([self.exe,"-g",str(t)],stderr=sp.PIPE)
          self.NFAIL += 1
          print "Invalid Galaxy Type!"
        except sp.CalledProcessError:
          self.NSUCCESS += 1

class input_tests:
    NTESTS = 0                     #Total number of tests
    NSUCCESS = 0                   #NUmber of successes
    NFAIL = 0                      #Number of failures

    def __init__(self,f):
        print "Initialising Input Properties Tests..."
        self.exe = f

    def __del__(self):
        self.NSUCCESS += 1e-10; self.NFAIL += 1e-10; self.NTESTS += 1e-10
        print "Tests completed."
        print "%i"%self.NSUCCESS,"of %i"%self.NTESTS,"sucessful (%.0f" %(100*(self.NSUCCESS/self.NTESTS)),"%)"
        print "%i"%self.NFAIL,"of %i"%self.NTESTS,"failed (%.0f" %(100*(self.NFAIL/self.NTESTS)),"%)"

    def test_initialise(self):
        
        self.NTESTS += 4
        A = sp.check_output([self.exe,"-N","65536","-r","1","-m","0.547","-v","220","-d","8.5","-z 0.15"]
                            ,stderr=sp.STDOUT).split('\n')

        cluster =  A[6].split()
        galaxy =  A[10].split()

        if cluster[3] == "65536" and cluster[6] == "0.547" and cluster[10] == "1" and cluster[-1] == "0.15":
          self.NSUCCESS += 1
        else:
          self.NFAIL += 1
          print "Cluster Initialisation Error"
        if galaxy[2] == "8.5" and galaxy[6] == "220" and galaxy[14] == "0":
          self.NSUCCESS += 1
        else:
          self.NFAIL += 1
          print "Galaxy Initialisation Error"

        A = sp.check_output([self.exe,"-N","32768","-r","0.1","-m","0.663","-v","200","-d","10","-z 0.111",
                            "-g","0"],stderr=sp.STDOUT).split('\n')

        cluster = A[6].split()
        galaxy = A[10].split()

        if cluster[3] == "32768" and cluster[6] == "0.663" and cluster[10] == "0.1" and cluster[-1] == "0.111":
          self.NSUCCESS += 1
        else:
          self.NFAIL += 1
          print "Cluster Initialisation Error"
        if galaxy[2] == "10" and galaxy[6] == "200" and galaxy[14] == "0":
          self.NSUCCESS += 1
        else:
          self.NFAIL += 1
          print "Galaxy Initialisation Error"

    def test_conversion(self):
        
        self.NTESTS += 4
        A = sp.check_output([self.exe,"-N","65536","-r","0.66","-m","0.547","-v","220","-d","8.5","-z 0.15",
                            "-o","2"],stderr=sp.STDOUT).split('\n')

        factors =  A[9].split()
        sample1 =  A[140].split()
        sample2 =  A[142].split()
        if (float(sample1[1]) > float(sample2[1])*float(factors[11])*0.999 \
             and float(sample1[1]) < float(sample2[1])*float(factors[11])*1.001):
          self.NSUCCESS += 1
        else:
          self.NFAIL += 1
          print "Time Conversion Error"
        if (float(sample1[2]) > float(sample2[2])*0.999 and float(sample1[2]) < float(sample2[2])*1.001):
          self.NSUCCESS += 1
        else:
          self.NFAIL += 1
          print "N not consisitent between outputs"
        if (float(sample1[3]) > float(sample2[3])*float(factors[5])*0.999 \
             and float(sample1[3]) < float(sample2[3])*float(factors[5])*1.001):
          self.NSUCCESS += 1
        else:
          self.NFAIL += 1
          print "Mass Conversion Error"
        if (float(sample1[5]) > float(sample2[5])*float(factors[8])*0.999 \
             and float(sample1[5]) < float(sample2[5])*float(factors[8])*1.001):
          self.NSUCCESS += 1
        else:
          self.NFAIL += 1
          print "Radius Conversion Error"

    def test_calculated_parameters(self):
        
        self.NTESTS += 6
        vg = 220; d = 8500; M = 9.563e10

        A = sp.check_output([self.exe,"-N","65536","-r","1","-m","0.547","-v","220","-d","8.5","-z 0.15"]
                            ,stderr=sp.STDOUT).split('\n')
        galaxy = A[10].split()
        if float(galaxy[10]) > 0.99*9.564e10 and float(galaxy[10]) < 1.01*9.564e10:
            self.NSUCCESS += 1
        else:
          self.NFAIL += 1
          print "Galaxy Mass Calculation Error", float(galaxy[10]),0.999*9.564e10

        A = sp.check_output([self.exe,"-N","65536","-r","1","-m","0.547","-M","9.564e10","-d","8.5","-z 0.15"]
                            ,stderr=sp.STDOUT).split('\n')
        galaxy = A[10].split()
        if float(galaxy[2]) > 0.99*8.5 and float(galaxy[2]) < 1.01*8.5:
            self.NSUCCESS += 1
        else:
          self.NFAIL += 1
          print "Galactocentric radius Calculation Error"

        A = sp.check_output([self.exe,"-N","65536","-r","1","-m","0.547","-v","220","-M","9.564e10","-z 0.15"]
                            ,stderr=sp.STDOUT).split('\n')
        if float(galaxy[6]) > 0.99*220 and float(galaxy[6]) < 1.01*220:
            self.NSUCCESS += 1
        else:
          self.NFAIL += 1
          print "Orbital Velocity Calculation Error"

        N = 13762; mm = 0.547; r = 1; vG = 220; RG = 8.5; G = 0.00449857
        A = sp.check_output([self.exe,"-N",str(N),"-r",str(r),"-m",str(mm),"-v",str(vg),"-d",str(RG),"-z 0.15"]
                            ,stderr=sp.STDOUT).split('\n')
        rj = ((G*N*mm*(RG*1e3)**2)/(3.0*vG**2))**(1.0/3.0)      #Calculates exactly
        trh = 0.138*np.sqrt((N*r**3)/(G*mm))*(1/np.log(0.02*N))
        rj_calc =  float(A[17].split()[-1])
        trh_calc =  float(A[18].split()[1])

        if rj_calc > 0.999*rj and rj_calc < 1.001*rj:
            self.NSUCCESS += 1
        else:
          self.NFAIL += 1
          print "Jacbi Radius Calculation Error"

        if trh_calc > 0.999*trh and trh_calc < 1.001*trh:
            self.NSUCCESS += 1
        else:
          self.NFAIL += 1
          print "Relaxation Time Calculation Error"

        A = sp.check_output([self.exe,"-N",str(N),"-R","0.01","-m",str(mm),"-v",str(vg),"-d",str(RG),"-z 0.15"]
                            ,stderr=sp.STDOUT).split('\n')
        cluster =  A[6].split()
        if float(cluster[10]) > 0.999*rj*0.01 and float(cluster[10]) < 1.001*rj*0.01:
          self.NSUCCESS += 1
        else:
          self.NFAIL += 1
          print "Filling Factor definition error"

class output_tests:
    NTESTS = 0                     #Total number of tests
    NSUCCESS = 0                   #NUmber of successes
    NFAIL = 0                      #Number of failures

    def __init__(self,f):
        print "Initialising Output Properties Tests..."
        self.exe = f

    def __del__(self):
        self.NSUCCESS += 1e-10; self.NFAIL += 1e-10; self.NTESTS += 1e-10
        print "Tests completed."
        print "%i"%self.NSUCCESS,"of %i"%self.NTESTS,"sucessful (%.0f" %(100*(self.NSUCCESS/self.NTESTS)),"%)"
        print "%i"%self.NFAIL,"of %i"%self.NTESTS,"failed (%.0f" %(100*(self.NFAIL/self.NTESTS)),"%)"

    def test_time(self):
        
        self.NTESTS +=2
        times = 10,100
        for time in times:
          A = sp.check_output([self.exe,"-t",str(time),"-N","1e5"],stderr=sp.STDOUT).split('\n')[19].split()
          if float(A[1]) > time and float(A[1]) < time*1.01:
              self.NSUCCESS += 1
          else:
              self.NFAIL += 1
              print "Specified output time error"

    def test_fail(self):
        
        self.NTESTS +=2
        times = 10,100
        for time in times:
          A = sp.check_output([self.exe,"-t",str(time),"-N","8192"],stderr=sp.STDOUT).split('\n')[19].split()
          if float(A[2]) < 1:
              self.NSUCCESS += 1
          else:
              self.NFAIL += 1
              print "Specified output time bounds error"

class em_tests:
    NTESTS = 0                     #Total number of tests
    NSUCCESS = 0                   #NUmber of successes
    NFAIL = 0                      #Number of failures

    def __init__(self,f):
        print "Initialising Equal Mass Evolution Tests..."
        self.exe = f

    def __del__(self):
        self.NSUCCESS += 1e-10; self.NFAIL += 1e-10; self.NTESTS += 1e-10
        print "Tests completed."
        print "%i"%self.NSUCCESS,"of %i"%self.NTESTS,"sucessful (%.0f" %(100*(self.NSUCCESS/self.NTESTS)),"%)"
        print "%i"%self.NFAIL,"of %i"%self.NTESTS,"failed (%.0f" %(100*(self.NFAIL/self.NTESTS)),"%)"
              


def main():

    if len(sys.argv) > 1:
        f = "./"+sys.argv[1]
    else:
        print "Using default name of executable file: emacss_dev "
        f = "./emacss_dev"

    bounds = boundaries_tests(f)
    bounds.test_N()
    bounds.test_r()
    bounds.test_galaxy()
    bounds.test_zeta()
    bounds.test_meta()   
    del bounds

    input = input_tests(f)
    input.test_initialise()
    input.test_conversion()
    input.test_calculated_parameters()
    del input

    output = output_tests(f)             #Only ensures time selected outputs are accurate - others are implicit
    output.test_time()
    output.test_fail()
    del output

    em = equal_mass_tests(f)            #To complete
#    em.high_mass_high_R()
#    em.low_mass_high_R()
#    em.high_mass_low_R()
#    em.low_mass_low_R()
    del em
    
if __name__ == '__main__':
    main()