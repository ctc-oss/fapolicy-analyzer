// p_unit.cpp - Inputs a file, outputs 'watermarked' version of that file
// TPArchambault 2024.01.25
//

#include <Log4Cxx.h>
#include <iostream>
#include <string>
#include <fstream>

#include <experimental/filesystem>

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

#include "fs_utils.h"

using namespace std;
using namespace log4cxx;
namespace fs = experimental::filesystem;

LoggerPtr logger(log4cxx::Logger::getLogger("p_unit"));

// Globals
bool gbVerbose = false;
bool gbDaemon = false;
bool gbMonitorDir = false;
bool gbGenerateUuid = false;
bool gbArtifacts = false;
string gszFileIn;
string gszDirIn;
string gszFileOut;
string gszDirOut;
string gszFileTmp;
string gszDirTmp;
string gszWatermarkText;
int giPollingPeriod(1);

char const* error_messages[] = {
  "Ok",
  "Input file and directory not specified. One must be specified",
  "Output file and directory not specified. One must be specified",
  "Tmp file and directory not specified. One must be specified",
};

// print_help()
void print_help(string szProgName)
{
  cout << endl;
  cout << "\tUsage: " << szProgName << " [options]" << endl;
  cout << endl;
  cout << "\t      Options" << endl;
  cout << "\t\t-i INPUT_FILE\tSpecify the input file" << endl;
  cout << "\t\t-I INPUT_DIR\tSpecify the input directory" << endl;
  cout << "\t\t-o OUTPUT_FILE\tSpecify the output file" << endl;
  cout << "\t\t-O OUTPUT_DIR\tSpecify an (existing) output directory" << endl;
  cout << "\t\t-t TMP_FILE\tSpecify the tmp/working file" << endl;
  cout << "\t\t-T TMP_DIR\tSpecify an (existing) working directory" << endl;
  cout << "\t\t-w WATERMARK\tSpecify the watermark text" << endl;
  cout << "\t\t-P POLL_PERIOD\tSpecify polling period (seconds)" << endl;
  cout << "\t\t-d\tEnable daemon mode." << endl;
  cout << "\t\t-v\tEnable verbose mode." << endl;
  cout << "\t\t-a\tEnable artifact mode." << endl;
  cout << "\t\t-h\tPrint this help page." << endl;
  cout << endl;
}

// parse_options()
int parse_options(int argc, char* argv[])
{
  int arg;
  while( (arg = getopt(argc, argv, "advhi:I:o:O:t:T:P:w:")) != -1)
    {
      switch(arg)
	{
	case 'o':
	  gszFileOut = optarg;
	  break;
	  
	case 'O':
	  gszDirOut = optarg;
	  break;
	  
	case 'i':
	  gszFileIn = optarg;
	  break;
	  
	case 'I':
	  gszDirIn = optarg;
	  break;
	  
	case 't':
	  gszFileTmp = optarg;
	  break;
	  
	case 'T':
	  gszDirTmp = optarg;
	  break;
	  
	case 'w':
	  gszWatermarkText = optarg;
	  break;
	  
	case 'P':
	  giPollingPeriod = atoi(optarg);
	  gbDaemon = true;
	  break;
	  
	case 'd':
	  gbDaemon = true;
	  break;
	  
	case 'v':
	  gbVerbose = true;
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
  if(gszFileIn.length() == 0 && gszDirIn.length() == 0) return 1;
  if(gszFileOut.length() == 0 && gszDirOut.length() == 0) return 2;
  if(gszFileOut.length() == 0 && gszDirOut.length() == 0) return 3;
  if(gszFileIn.length() == 0 && gszDirIn.length() > 0)
    {
      gbMonitorDir = true;
      gbDaemon = true;
    }
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
  LOG4CXX_DEBUG(logger, "Executing input_xlator...");
  
  // Daemon mode loop
  do {
    string szFileIn;
    // Determine input filename
    // Dir and filename both specified
    if (gszFileIn.length() > 0 && gszDirIn.length() >0)
      {
	szFileIn = gszDirIn + gszFileIn;
      }
    // Only the filename is specified
    else if (gszFileIn.length() > 0 && gszDirIn.length() == 0)
      {
	szFileIn = gszFileIn;
      }
    // Only the dir is specified, monitor mode
    else if  (gszFileIn.length() == 0 && gszDirIn.length() > 0)
      {
	szFileIn = monitor_dir(gszDirIn.c_str(), 2);
	if(szFileIn.length() == 0)
	  {
	    LOG4CXX_DEBUG(logger, "No new input files...");
	    continue;
	  }
      }
    else
      {
	cout << "Not enough input information specified" << endl;
	exit(1);
      }
    
    // Instantiate and open the input and tmp file and transfer 1K blocks
    char inputBuffer[1025] = {};
    string szTmpPathOut(generate_out_path(gszDirTmp, gszFileTmp));
    ifstream ifsInput(szFileIn);
    ofstream ofsTmp;

    do
      {
	ifsInput.read(inputBuffer, 1024);
	int iReadCount = ifsInput.gcount();
	// If this is the first read, open ofsOutput stream
	if(!ofsTmp.is_open())
	  {
	    // Verify directory exists
	    fs::path fileTmp(szTmpPathOut);//.c_str());
	    fs::path  dirTmp(fs::absolute(fileTmp).parent_path());
	    if(!fs::is_directory(dirTmp))
	      {
		cout << "Non-existent director: " << dirTmp << endl;
		exit(1);
	      }
	    ofsTmp.open(szTmpPathOut.c_str(), ofstream::out);
	  }
	ofsTmp.write(inputBuffer, iReadCount);
	
	
	if( gbVerbose)
	  {
	    // add null terminator
	    inputBuffer[iReadCount] = 0;
	    cout << inputBuffer << endl;
	  }
      } while(ifsInput.good());
    ifsInput.close();
    ofsTmp.close();

    string szFullPathOut(generate_out_path(gszDirOut, gszFileOut));
    string szPartPathOut(szFullPathOut);
    szPartPathOut.append(".part");

    string szTmpPathIn = szTmpPathOut; //Tmp working file is now input file
    ifstream ifsTmpInput(szTmpPathIn);
    ofstream ofsOutput;
    
    while(1)
      {
	ifsTmpInput.read(inputBuffer, 1024);
	int iReadCount = ifsTmpInput.gcount();
	if(iReadCount > 0)
	  {
	    // If this is the first read, open ofsOutput stream
	    if(!ofsOutput.is_open())
	      {
		// Verify directory exists
		fs::path fileTmp(szPartPathOut);//.c_str());
		fs::path  dirTmp(fs::absolute(fileTmp).parent_path());
		if(!fs::is_directory(dirTmp))
		  {
		    cout << "Non-existent director: " << dirTmp << endl;
		    exit(1);
		  }
		ofsOutput.open(szPartPathOut.c_str(), ofstream::out);
	      }
	    ofsOutput.write(inputBuffer, iReadCount);
	  }
	else
	  {
	    // Close and delete tmp file
	    ifsTmpInput.close();
	    if(!gbArtifacts)
	      {
		LOG4CXX_DEBUG(logger, "Removing tmp file.");
		remove(szTmpPathIn.c_str());
	      }
	    if(ofsOutput.is_open())
	      {
		ofsOutput.flush();
		ofsOutput.close();
		rename(szPartPathOut.c_str(), szFullPathOut.c_str());
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
  } while(gbDaemon);
  return 0;
}
