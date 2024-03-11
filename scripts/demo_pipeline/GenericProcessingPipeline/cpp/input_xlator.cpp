/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

// input_xlator.cpp - Inputs a file via TCP/IP transfer

#include <Log4Cxx.h>
#include <iostream>
#include <fstream>

#include <experimental/filesystem>

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <signal.h>
#include <uuid/uuid.h>

#include "fs_utils.h"

using namespace std;
using namespace log4cxx;
namespace fs = experimental::filesystem;

LoggerPtr logger(log4cxx::Logger::getLogger("input_xlator"));

// Globals
bool gbVerbose = false;
bool gbDaemon = false;
bool gbArtifacts = false;
bool gbGenerateUuid = false;
string gszFileOut;
string gszDirOut;
int giListeningPort(0);

char const* error_messages[] = {
  "Ok",
  "Output file not specified",
  "Output directory not specified",
  "Listening port not specified",
};

// print_help()
void print_help(string szProgName)
{
  cout << endl;
  cout << "\tUsage: " << szProgName << " [options]" << endl;
  cout << endl;
  cout << "\t      Options" << endl;
  cout << "\t\t-o OUTPUT_FILE\tSpecify the output file" << endl;
  cout << "\t\t-O OUTPUT_DIR\tSpecify an (existing) output directory" << endl;
  cout << "\t\t-p LISTENING_PORT\tSpecify the listening port" << endl;
  cout << "\t\t-h\tPrint this help page." << endl;
  cout << "\t\t-d\tEnable daemon mode." << endl;
  cout << "\t\t-a\tEnable artifact mode." << endl;
  cout << "\t\t-v\tEnable verbose mode." << endl;
  cout << endl;
}

// parse_options()
int parse_options(int argc, char* argv[])
{
  int arg;
  while((arg = getopt(argc, argv, "avdho:O:p:")) != -1)
    {
      switch(arg)
	{
	case 'p':
	  giListeningPort = atoi(optarg);
	  break;
	  
	case 'o':
	  gszFileOut = optarg;
	  break;
	  
	case 'O':
	  gszDirOut = optarg;
	  break;
	  
	case 'v':
	  gbVerbose = true;
	  break;
	  
	case 'd':
	  gbDaemon = true;
	  break;
	  
	case 'a':
	  gbArtifacts = true;
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
  if(giListeningPort == 0) return 2;

  return 0;
}

// main()
int main(int argc, char* argv[])
{
  int iReturn(0);
  int iSvrSockFd;
  int iClientSockFd;
  struct sockaddr_in svr_addr;
  struct sockaddr_in client_addr;
    
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
  
  // Create the listening socket
  iSvrSockFd = socket(AF_INET, SOCK_STREAM, 0);
  svr_addr.sin_family = AF_INET;
  svr_addr.sin_addr.s_addr = htonl(INADDR_ANY);
  svr_addr.sin_port = htons(giListeningPort);
  int iAddrSize = sizeof(svr_addr);

  const int enable(1);
  if(setsockopt(iSvrSockFd, SOL_SOCKET, SO_REUSEADDR,
		&enable, sizeof(int))<0)
    {
      perror("setsockopt(SO_REUSEADDR) failed");
      exit(1);
    }
  
  if(setsockopt(iSvrSockFd, SOL_SOCKET, SO_REUSEPORT,
		&enable, sizeof(int))<0)
    {
      perror("setsockopt(SO_REUSEPORT) failed");
      exit(1);
    }
  
  if(bind(iSvrSockFd, (struct sockaddr*) &svr_addr, iAddrSize))
    {
      cout << "bind() failed. Exiting." << endl;
      exit(1);
    }

  if(listen(iSvrSockFd, 1) == -1)
    {
      cout << "listen() failed. Exiting." << endl;
      exit(1);
    }

  signal(SIGCHLD, SIG_IGN);
  
  do // Daemon mode loop
    {
      // Open the output file and transfer 1K blocks
      int iReadCount;
      char inputBuffer[1024] = {};
      string szFullPathOut(generate_out_path(gszDirOut, gszFileOut));
      string szTmpPathOut(szFullPathOut);
      szTmpPathOut.append(".part");
      ofstream ofsOutput;

      int iClientAddrSize = sizeof(client_addr);
      iClientSockFd = accept(iSvrSockFd, (struct sockaddr*)&client_addr,
			     (socklen_t*)&iClientAddrSize);
      while(1)
	{
	  iReadCount = read(iClientSockFd, inputBuffer, 1024);
	  if(iReadCount > 0)
	    {
	      // If this is the first read, open ofsOutput stream
	      if(!ofsOutput.is_open())
		{
		  // Verify directory exists
		  fs::path fileTmp(szTmpPathOut);//.c_str());
		  fs::path  dirTmp(fs::absolute(fileTmp).parent_path());
		  if(!fs::is_directory(dirTmp))
		    {
		      cout << "Non-existent director: " << dirTmp << endl;
		      exit(1);
		    }
		  ofsOutput.open(szTmpPathOut.c_str(), ofstream::out);
		}
	      ofsOutput.write(inputBuffer, iReadCount);
	    }
	  else
	    {
	      if(ofsOutput.is_open())
		{
		  ofsOutput.flush();
		  ofsOutput.close();
		  rename(szTmpPathOut.c_str(), szFullPathOut.c_str());
		}
	      break;
	    }

	  if( gbVerbose)
	    {
	      // add null terminator
	      inputBuffer[iReadCount] = 0;
	      cout << inputBuffer << endl;
	    }
	}
      close(iClientSockFd);
    } while ( gbDaemon );
  return 0;
}
