/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

// client.cpp

#include <Log4Cxx.h>
#include <iostream>
#include <string>
#include <fstream>

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

using namespace std;
using namespace log4cxx;

LoggerPtr logger(log4cxx::Logger::getLogger("client"));

// Globals
bool gbVerbose = false;
string gszFileIn;
string gszServerAddr("127.0.0.1"); // IPv4 octet format; default localhost
int giServerPort(0);

char const* error_messages[] = {
  "Ok",
  "Input file not specified",
  "Server address not specified",
  "Server port not specified",
};

// print_help()
void print_help(string szProgName)
{
  cout << endl;
  cout << "\tUsage: " << szProgName << " [options]" << endl;
  cout << endl;
  cout << "\t      Options" << endl;
  cout << "\t\t-i INPUT_FILE\tSpecify the input file" << endl;
  cout << "\t\t-S SERVER_IP\tSpecify the server IP address" << endl;
  cout << "\t\t-p SERVER_PORT\tSpecify the server port" << endl;
  cout << "\t\t-h\tPrint this help page." << endl;
  cout << "\t\t-v\tEnable verbose mode." << endl;
  cout << endl;
}

// parse_options()
int parse_options(int argc, char* argv[])
{
  int arg;
  while( (arg = getopt(argc, argv, "vhi:S:p:")) != -1)
    {
      switch(arg)
	{
	case 'S':
	  gszServerAddr = optarg;
	  break;
	  
	case 'p':
	  giServerPort = atoi(optarg);
	  break;
	  
	case 'i':
	  gszFileIn = optarg;
	  break;
	  
	case 'v':
	  gbVerbose = true;
	  break;
	  
	case 'h':
	  print_help(argv[0]);
	  exit(0);
	  
	default:
	  print_help(argv[0]);
	  exit(1);
	}
    }

  // validate options
  if(gszFileIn.length() == 0) return 1;
  if(gszServerAddr.length() == 0) return 2;
  if(giServerPort == 0) return 3;
  return 0;
}

// main()
int main(int argc, char* argv[])
{
  int iReturn(0);
  int iSockFd;
  struct sockaddr_in svr_addr;
  
  //Set up logging
  BasicConfigurator::configure();

  // Parse the args
  iReturn = 0;
  if(0 != (iReturn = parse_options(argc, argv)))
    {
      cout << endl;
      cout << "\t" << error_messages[iReturn] << endl;
      cout << endl;
      
      print_help(argv[0]);
      exit(1);
    }

  // Set log level
  if(gbVerbose)
    {
      logger->setLevel(log4cxx::Level::getDebug());
    }
  else
    {
      logger->setLevel(log4cxx::Level::getInfo());
    }
  LOG4CXX_DEBUG(logger, "Executing client...");
  

  // Create the sending socket
  iSockFd = socket(AF_INET, SOCK_STREAM, 0);
  svr_addr.sin_family = AF_INET;
  svr_addr.sin_addr.s_addr = inet_addr(gszServerAddr.c_str());
  svr_addr.sin_port = htons(giServerPort);
  int iAddrSize = sizeof(svr_addr);

  if(connect(iSockFd, (struct sockaddr*) &svr_addr, iAddrSize))
    {
      cout << "connect() failed. Exiting." << endl;
      exit(1);
    }
  
  // Open the input file and read in 1K blocks
  char inputBuffer[1024] = {};
  ifstream ifsInput(gszFileIn);


  do {
      ifsInput.read(inputBuffer, 1023);

      int iReadLength = ifsInput.gcount();
      write(iSockFd, inputBuffer, iReadLength);

      if( gbVerbose)
	{
	  // add null terminator
	  inputBuffer[iReadLength] = 0;
	  cout << inputBuffer << endl;
	}
    }while(ifsInput.good());
  //close(iSockFd);
  return 0;
}
