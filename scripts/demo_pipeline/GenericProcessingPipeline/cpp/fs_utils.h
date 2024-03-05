// fs_utils.h
// TPArchambault 20240214
//

#ifndef _FS_UTILS_H_
#define _FS_UTILS_H_

using namespace std;

std::string generate_out_path(std::string& szDirOut, std::string& szFileOut);
std::string monitor_dir(const char* szDir, int iPollingPeriod = 1,
			int iMaxLoopCount = 0);

#endif //_FS_UTILS_H_
