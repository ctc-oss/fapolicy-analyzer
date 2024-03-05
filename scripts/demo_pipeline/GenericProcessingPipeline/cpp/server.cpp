// server.cpp
// TPArchambault 2024.01.25
//

#include <Log4Cxx.h>
#include <iostream>
#include <fstream>

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <signal.h>

using namespace std;
using namespace log4cxx;

LoggerPtr logger(log4cxx::Logger::getLogger("server"));

// Globals
bool gbVerbose = false;
bool gbDaemon = false;
string gszFileOut;
int giListeningPort(0);

char const* error_messages[] = {
  "Ok",
  "Output file not specified",
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
  cout << "\t\t-p LISTENING_PORT\tSpecify the listening port" << endl;
  cout << "\t\t-h\tPrint this help page." << endl;
  cout << "\t\t-d\tEnable daemon mode." << endl;
  cout << "\t\t-v\tEnable verbose mode." << endl;
  cout << endl;
}

// parse_options()
int parse_options(int argc, char* argv[])
{
  int arg;
  while((arg = getopt(argc, argv, "vdho:p:")) != -1)
    {
      switch(arg)
	{
	case 'p':
	  giListeningPort = atoi(optarg);
	  break;
	  
	case 'o':
	  gszFileOut = optarg;
	  break;
	  
	case 'v':
	  gbVerbose = true;
	  break;
	  
	case 'd':
	  gbDaemon = true;
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
  if(gszFileOut.length() == 0) return 1;
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
  LOG4CXX_DEBUG(logger, "Executing server...");
  
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
      char inputBuffer[1025] = {}; // element 1025 is for the null terminator
      string szFullPathOut(gszFileOut);
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
		  ofsOutput.open(szFullPathOut.c_str(), ofstream::out);
		}
	      ofsOutput.write(inputBuffer, iReadCount);

	      if( gbVerbose)
		{
		  // add null terminator
		  inputBuffer[iReadCount] = 0;
		  cout << inputBuffer << endl;
		}
	    }
	  else
	    {
	      if(ofsOutput.is_open())
		{
		  ofsOutput.flush();
		  ofsOutput.close();
		}
	      break;
	    }
	}
      close(iClientSockFd);
    } while ( gbDaemon );
  return 0;
}
