// fs_utils.cpp
// TPArchambault 20240214
//

#include <unordered_set>

#include <unistd.h>
#include <sys/stat.h>
#include <dirent.h>
#include <uuid/uuid.h>

#include <string>

using namespace std;

string generate_out_path(string& szDirOut, string& szFileOut)
{
  string szReturn;
  char szUuidBuf[37] = {}; //uuid buffer

  // File name supplied but no directory arg supplied
  if(szDirOut.length() == 0 && szFileOut.length() > 0)
    {
      return szFileOut;
    }

  // Filename arg passed in with directory arg
  if(szDirOut.length() > 0 && szFileOut.length() > 0)
    {
      return szReturn = szDirOut + "/" + szFileOut;
    }

  // Create uu on the stack
  uuid_t uu;
  uuid_generate(uu);
  uuid_unparse(uu, szUuidBuf);

  // No filename arg passed in but with directory arg
  if(szDirOut.length() > 0 && szFileOut.length() == 0)
    {
      return szDirOut + szUuidBuf;
    }

  // Neither filename arg passed in nor directory arg
  return szUuidBuf;
}

// monitor_dir - Poll the directory contents; a new filename is returned
// Args: iPollingPeriod: scan period in seconds; iMaxLoopCount: 0 = infinite
string monitor_dir(const char* szDir, int iPollingPeriod = 1,
		   int iMaxLoopCount = 0)
{
  string strReturn("");
  unordered_set<string> setBaseline;
  
  struct dirent *entry;
  struct stat statbuf;  
  DIR* pdir;

  // Build baseline directory contents set
  if((pdir = opendir(szDir)) == NULL)
    {
      fprintf(stderr, "cannot open directory %s\n", szDir);
      strReturn = "cannot open directory";
      return strReturn;
    }

  chdir(szDir);
  while((entry = readdir(pdir)) != NULL)
    {
      lstat(entry->d_name, &statbuf);
      // if a directory, ignore it
      if(S_ISDIR(statbuf.st_mode) != 0)
	{
	  continue;
	}
      if(setBaseline.count(entry->d_name) == 0)
	{
	  setBaseline.insert(entry->d_name);
	}
    }
  closedir(pdir);  
  
  do {

    pdir = opendir(szDir); // No error handling because opened above
    while((entry = readdir(pdir)) != NULL)
      {
	lstat(entry->d_name, &statbuf);
	if(S_ISDIR(statbuf.st_mode))
	  {
	    continue;
	  }
	if(setBaseline.count(entry->d_name) == 0)
	  {
	    strReturn = entry->d_name;
	    break;
	  }
      }
    closedir(pdir);
    sleep(iPollingPeriod);
  } while( strReturn.length() == 0);
  return strReturn;
}
