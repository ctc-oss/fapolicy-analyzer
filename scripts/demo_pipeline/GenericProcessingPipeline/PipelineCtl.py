#!/usr/bin/python3
# Copyright Concurrent Technologies Corporation 2023
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# PipelineCtl.py - Generic Processing Pipeline run manager
# TPArchambault 20240209
#

import logging
import argparse
import subprocess
import time
import os

logging.basicConfig(level=logging.INFO)

# globals #######################################################
gbVerbose = False
gbArtifacts = False
gbTestMode = False
gbSingleXfer = False
gbMultiXfer = False

# mk_runtime_dirs #################################
def mk_runtime_dirs():
    os.system("mkdir -p /tmp/pipeline/")
    os.system("mkdir -p /tmp/pipeline/it_p0/")
    os.system("mkdir -p /tmp/pipeline/p0_p1/")
    os.system("mkdir -p /tmp/pipeline/p1_ot/")
    os.system("mkdir -p /tmp/pipeline/p0_working/")
    os.system("mkdir -p /tmp/pipeline/p1_working/")

# kill_pipeline #################################
def kill_pipeline():
    os.system("pkill client")
    os.system("pkill xlator")
    os.system("pkill server")
    os.system("pkill p_unit")

# test_processing_unit #################################
def test_processing_unit():
    logging.debug("test_processing_unit()")

    # Initialize environment
    os.system("cp test/test_input.xml /tmp/test_input.xml")
    os.system("rm -f /tmp/p_unit.out")
    
    # Execute the p_unit, testing simple I/O
    p_uut = subprocess.Popen(['bin/p_unit',
                              '-I', '/tmp/',
                              '-i','test_input.xml',
                              '-O', '/tmp/',                                
                              '-o', 'p_unit.out',
                              '-T', '/tmp/',
                                ])

    p_uut.wait(5)
    
    logging.debug("/usr/bin/diff -q /tmp/test_input.xml /tmp/p_unit.out")
    if os.system("/usr/bin/diff -q /tmp/test_input.xml /tmp/p_unit.out") == 0:
        bReturn = True
    else:
        bReturn = False

    if not gbArtifacts:
        os.system("rm -f /tmp/test_input.xml")
        os.system("rm -f /tmp/p_unit.out")
        
    return bReturn

# test_client_server ############################################
def test_client_server():
    logging.debug("test_client_server()")

    # Initialize environment
    os.system("rm -f server.out")

    # Execute client/server back to back
    logging.debug("Starting the server")
    pSvr = subprocess.Popen(['bin/server', '-o', 'server.out', '-p', '31337'])
    time.sleep(3)
    pClient = subprocess.Popen(['bin/client', '-i', 'cpp/client.cpp',
                                '-p', '31337'])
    pClient.wait(5)
    pSvr.wait(10)
    logging.debug("/usr/bin/diff -q cpp/client.cpp server.out")
    if os.system("/usr/bin/diff -q cpp/client.cpp server.out") == 0:
        bReturn = True
    else:
        bReturn = False

    if not gbArtifacts:
        os.system("rm -f server.out")

    kill_pipeline()
    return bReturn

# test_client_in_xlator ###########################################
def test_client_in_xlator():
    logging.debug("test_client_in_xlator()")

    # Initialize environment
    os.system("rm -f /tmp/input_xlator.out")

    # Execute client/input_xlator back to back
    logging.debug("Starting the input_xlator")
    pInXLator = subprocess.Popen(['bin/input_xlator',
                                  '-O', '/tmp/',
                                  '-o', 'input_xlator.out',
                                  '-p', '31337'])
    time.sleep(2)
    pClient = subprocess.Popen(['bin/client', '-i', 'cpp/client.cpp',
                                '-p', '31337'])
    pInXLator.wait(10)

    logging.debug("/usr/bin/diff -q cpp/client.cpp /tmp/input_xlator.out")
    if os.system("/usr/bin/diff -q cpp/client.cpp /tmp/input_xlator.out") == 0:
        bReturn = True
    else:
        bReturn = False

    if not gbArtifacts:
        os.system("rm -f /tmp/input_xlator.out")

    kill_pipeline()
    return bReturn

# test_out_xlator_server ########################################
def test_out_xlator_server():
    logging.debug("test_out_xlator_server()")

    # Initialize environment
    os.system("rm -f server.out")
    
    # Execute output_xlator/server back to back
    logging.debug("Starting the output_xlator")
    pServer = subprocess.Popen(['bin/server', '-o', 'server.out', '-p','31337'])
    pOutXLator = subprocess.Popen(['bin/output_xlator',
                                   '-S', '127.0.0.1',
                                   '-I', 'cpp/',
                                   '-i', 'output_xlator.cpp', '-p','31337'])
    pOutXLator.wait(5)

    logging.debug("/usr/bin/diff -q cpp/output_xlator.cpp server.out")
    if os.system("/usr/bin/diff -q cpp/output_xlator.cpp server.out") == 0:
        bReturn = True
    else:
        bReturn = False

    kill_pipeline()
    return bReturn

# test_client_io_xlators_server #################################
def test_client_io_xlators_server():
    logging.debug("test_client_io_xlators_server()")

    # Initialize environment
    os.system("rm -f server.out")
    
    # Execute the tests, starting up processes w/listening sockets first.
    pServer = subprocess.Popen(['bin/server', '-o', 'server.out', '-p','31338'])
    pInXLator = subprocess.Popen(['bin/input_xlator',
                                  '-O', '/tmp/',
                                  '-o', 'input_xlator.out',
                                  '-p', '31337'])

    time.sleep(1)
    pClient = subprocess.Popen(['bin/client', '-i', 'cpp/client.cpp',
                                '-p', '31337'])

    pInXLator.wait(5)
    pOutXLator = subprocess.Popen(['bin/output_xlator', '-S', '127.0.0.1',
                                   '-I', '/tmp/',
                                   '-i', 'input_xlator.out',
                                   '-p','31338'])
    pOutXLator.wait(5)
    pServer.wait(5)
    logging.debug("/usr/bin/diff -q cpp/client.cpp server.out")
    if os.system("/usr/bin/diff -q cpp/client.cpp server.out") == 0:
        bReturn = True
    else:
        bReturn = False

    if not gbArtifacts:
        os.system("rm -f /tmp/input_xlator.out")

    kill_pipeline()
    return bReturn

# single_xfer_client_server_ene2end #############################
def single_xfer_client_server_ene2end():
    logging.debug("single_xfer_client_server_ene2end()")

    # Initialize environment
    os.system("rm -f /tmp/pipeline/it_p0/input_xlator.out")
    os.system("rm -f /tmp/pipeline/p0_p1/p_unit_0.out")
    os.system("rm -f /tmp/pipeline/p1_ot/p_unit_1.out")
    os.system("rm -f /tmp/pipeline/server.out")

    artifact_opt = "-a" if gbArtifacts else ""
    
    # Execute single file test, starting up processes w/listening sockets first.
    # server, listens on 31338
    logging.debug("Starting the server on port 31338...")
    pServer = subprocess.Popen(['bin/server',
                                '-o', '/tmp/pipeline/server.out',
                                '-p','31338'])

    # input_translator, listens on 31337, writes to /tmp/pipeline/it_p0/ dir
    logging.debug("Starting the input_xlator on port 31337...")
    pInXLator = subprocess.Popen(['bin/input_xlator',
                                  '-O', '/tmp/pipeline/it_p0/',
                                  '-o', 'input_xlator.out',
                                  '-p', '31337'])

    # client, sends file to IT via tcp/ip
    time.sleep(3)
    logging.debug("Starting the client, sending test/test_input.xml via 31337")
    pClient = subprocess.Popen(['bin/client',
                                '-i', 'test/test_input.xml',
                                '-p', '31337'])
    pClient.wait(10)
    pInXLator.wait(5)
    
    # First processing unit, /tmp/pipeline/{read:it_p0/, write dir:p0_p1/}
    logging.debug("Starting the first p_unit...")
    pPUnit0 = subprocess.Popen(['bin/p_unit',
                                '-I', '/tmp/pipeline/it_p0/',
                                '-i', 'input_xlator.out',
                                '-O', '/tmp/pipeline/p0_p1/',
                                '-o', 'p_unit_0.out',
                                '-T', '/tmp/pipeline/p0_working/',
                                artifact_opt])
    pPUnit0.wait(5)

    # Second processing unit, /tmp/pipeline/{read:p0_p1/, write dir:p1_ot/}
    logging.debug("Starting the second p_unit...")
    pPUnit1 = subprocess.Popen(['bin/p_unit',
                                '-I', '/tmp/pipeline/p0_p1/',
                                '-i', 'p_unit_0.out',
                                '-O', '/tmp/pipeline/p1_ot/',
                                '-o', 'p_unit_1.out',
                                '-T', '/tmp/pipeline/p1_working/',
                                artifact_opt])
    pPUnit1.wait(5)

    # output_translator, send to srvr at 31337, read from /tmp/pipeline/p1_ot/
    logging.debug("Starting the output translator, sending to port 31338")
    pOutXLator = subprocess.Popen(['bin/output_xlator',
                                   '-S', '127.0.0.1',
                                   '-I', '/tmp/pipeline/p1_ot/',
                                   '-i', 'p_unit_1.out',
                                   '-p','31338'])
    pOutXLator.wait(5)
    #pServer.wait(10)
    logging.debug("/usr/bin/diff -q test/test_input.xml /tmp/pipeline/server.out")
    if os.system("/usr/bin/diff -q test/test_input.xml /tmp/pipeline/server.out") == 0:
        print("Single xfer execution: Input file successfully transferred")
    else:
        print("Single xfer execution: Fail")
    kill_pipeline()
    
# parse_args ####################################################
def parse_args():
    global gbVerbose
    global gbArtifacts
    global gbTestMode
    global gbSingleXfer
    global gbMultiXfer

    logging.debug("parse_args()")
    parser = argparse.ArgumentParser( prog="PipelineCtl.py",
                                      description="""
                                      Utility to test & run the generic pipeline
                                      """)
    parser.add_argument('-s', '--single',
                        help='Single file end-to-end transfer mode',
                        action='store_true')
    parser.add_argument('-m', '--multi',
                        help='Multi-file end-to-end transfer mode', 
                        action='store_true')
    parser.add_argument('-t', '--test', help='Execute test cases',
                        action='store_true')
    parser.add_argument('-v', '--verbose', help='Enable verbose mode',
                        action='store_true')
    parser.add_argument('-a', '--artifacts', help='Enable artifact mode',
                        action='store_true')
    parser.add_argument('-d', '--directories', help='Create runtime dirs',
                        action='store_true')
    
    args = parser.parse_args()

    if args.verbose:
        gbVerbose =  True
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbosity logging enabled")

    if args.single:
        gbSingleXfer = True

    if args.multi:
        gbMultiXfer = True

    if args.test:
        gbTestMode = True

    if args.artifacts:
        gbArtifacts = True
    
    if args.directories:
        mk_runtime_dirs()

# main() ########################################################
def main():
    logging.debug("main()")

    if gbTestMode:
        listTests = [
            test_processing_unit,
            test_client_server,
            test_client_in_xlator,
            test_out_xlator_server,
            test_client_io_xlators_server,
        ]
        
        logging.debug("Testing Mode executing...")
        ### Test initialization
        test_count = 0
        fail_test_count = 0
        pass_test_count = 0

        for t in listTests:
            logging.debug(f"Testing {t.__name__}()")
            test_count += 1
            if not t():
                print(f"{t.__name__}() failed")
                fail_test_count += 1
            else:
                logging.debug(f"{t.__name__}() passed")
                pass_test_count += 1            
            time.sleep(1)
            
        # Summarize testing
        if fail_test_count == 0:
            print(f"All {pass_test_count} tests passed")
        else:
            print(f"{fail_test_count} of {test_count} tests failed")

        logging.debug("Testing completed")

    if gbSingleXfer:
        logging.debug("Single file transfer mode entered...")
        single_xfer_client_server_ene2end()        
        logging.debug("Single file tranfer mode completed")
        
    if gbMultiXfer:
        logging.debug("Multi-file transfer mode entered...")
        print("Multi-file transfer mode currently not implemented")
        logging.debug("Multi-file transfer mode entered...")
        
# main entry # main entry # main entry # main entry # main entry #
if __name__ == '__main__':
    parse_args()
    main()
