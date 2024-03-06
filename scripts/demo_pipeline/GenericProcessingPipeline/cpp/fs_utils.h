/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

// fs_utils.h

#ifndef _FS_UTILS_H_
#define _FS_UTILS_H_

using namespace std;

std::string generate_out_path(std::string& szDirOut, std::string& szFileOut);
std::string monitor_dir(const char* szDir, int iPollingPeriod = 1,
			int iMaxLoopCount = 0);

#endif //_FS_UTILS_H_
