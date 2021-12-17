#!/bin/bash
# InsertLicenseHdr.sh - Inserts specified boilplate license within comments
# TPArchambault CTC 2021.12.11
#

##############################################################################
# Globals
##############################################################################
declare -A gdictType2Comment
gbVerbose=0
gbArtifactMode=0
gBnr=" License # CTC License # CTC License # CTC License # CTC License # CTC"
gbDelete=0
gstrLicenseFile=""
gstrManifestFile=""
gstrType=auto
glistFiles=""

# Populate language type to comment characters map
gdictType2Comment["sh"]="#"
gdictType2Comment["py"]="#"
gdictType2Comment["txt"]="#"
gdictType2Comment["rs"]="//"
gdictType2Comment["glade"]="#"

##############################################################################
# Echo() - A conditional print to stdout
##############################################################################
Echo()
{
    if [[ $gbVerbose == 1 ]]; then
	echo "$*"
    fi
}

##############################################################################
# parse_cmd_line() - Parse command line and set globals
##############################################################################
parse_cmd_line()
{
    Echo 'parse_cmd_line()'
    while getopts "hvadt:l:L:" option $*
    do
	case $option in
	    h) # Print help page
		print_help
		exit 0
		;;
	    v) # Enable verbosity
		gbVerbose=1
		Echo Verbosity Enabled
		;;

	    a) # Artifact mode - Keep tmp files around
		gbArtifactMode=1
		;;
	    
	    d) # Delete inserted license text
		gbDelete=1
		;;
	    
	    t) # Type of script/comments
		gstrType=$OPTARG
		;;
	    
	    L) # License file
		gstrLicenseFile=$OPTARG
		;;
	    
	    l) # File list
		gstrManifestFile==$OPTARG
		;;

	    *) # Default
		print_help
		exit 1
		;;
	esac
    done

    # Save the remaining args as the list of target files to process
    shift $(($OPTIND - 1))
    glistFiles="$@"
}

##############################################################################
build_file_list()
{
    fileManifest=$1
    Echo "build_file_list($1, $2)"
    while read f
    do
	glistFiles=$glistFiles $f
    done <  $fileManifest
    Echo $glistFiles
    glistFiles=listFiles
}

##############################################################################
print_help()
{
    Echo 'print_help()'
    echo
    echo -e "\tUsage: $0 [options] <FILE(S)>"
    echo
    echo -e "\t  where the <FILE(S)> argument can be omitted when using the"
    echo -e "\t  -L FILE_LIST option to specify a manifest file list."
    echo
    echo -e "\tOptions:"
    echo
    echo -e "\t  -h - Print this help page"
    echo -e "\t  -v - Enable verbose mode"
    echo -e "\t  -a - Maintain working temp file artifacts for post-mortem use."
    echo -e "\t  -d - Delete an existing leading license block"
    echo -e "\t  -t TYPE [sh,py,c,rs,auto] (Default: auto - from file suffix)"
    echo -e "\t  -L LICENSE_TEXT - Specify the license text to insert."
    echo -e "\t  -l FILE_LIST - Specify an input manifest file"
    echo
    echo
}

##############################################################################
delete_license_hdr()
{
    strTargetFile=$1
    strTmpFile=$2
    Echo 'delete_license_hdr()'
    
    # Locate license demarcation lines
    lines=($(awk '/'"$gBnr"'/{print FNR;}' $strTargetFile))

    # Return if no license comments found
    Echo Line Numbers demarcation lines: ${lines[@]}
    if [ -z $lines ]; then
	return 0
    fi
    sedCmd=${lines[0]},${lines[1]}d
    Echo Executing  sed -E "$sedCmd" $strTargetFile
    sed -E "$sedCmd" $strTargetFile > $strTmpFile
    cp $strTmpFile $strTargetFile
}

##############################################################################
populate_tmp_file()
{
    Echo "populate_tmp_file $1, $2, $3, $4 "
    strType=$1
    strLicenseFile=$2
    strTargetFile=$3
    strTmpFile=$4
    
    # Write pre-license banner line
    echo ${gdictType2Comment[$strType]} CTC $gBnr >$strTmpFile
    echo ${gdictType2Comment[$strType]} >>$strTmpFile
    
    # Write license template to tmp file w/leading comment characters
    while read line
    do
	echo ${gdictType2Comment[$strType]}  $line
    done <"$strLicenseFile"  >>$strTmpFile

    # Write post license comment line
    echo ${gdictType2Comment[$strType]} >>$strTmpFile
    echo ${gdictType2Comment[$strType]} CTC $gBnr >>$strTmpFile

    # Append source file to tmp staging file
    cat $strTargetFile >> $strTmpFile
}

##############################################################################
clean_up()
{
    strTmpFile=$1
    Echo 'clean_up()'
    if [[ $gbArtifactMode == 0 ]]
    then
	rm -f $strTmpFile
    fi
}

##############################################################################
# main # main # main # main # main # main # main # main # main # main # main #
##############################################################################

parse_cmd_line $*
#glistFiles=$(build_file_list $glistFiles)
for f in $glistFiles
do
    # Extract text after the last period to determine the file type/comment
    strType=$(echo $f | sed -E 's/^.*\.(.+)$/\1/')
    Echo $f maps to $strType and comment \'${gdictType2Comment[$strType]}\'
    if [[ $gbDelete == 1 ]]
    then
	Echo Deleting license in $f
	strTmpFile="/tmp/$(basename $f).deletion.$$.tmp"
	delete_license_hdr $f $strTmpFile
	clean_up $strTmpFile
    fi

    # Insert the License text
    if [ ! -z $gstrLicenseFile ]
    then
	Echo Inserting header text, $gstrLicenseFile into $f
	strTmpFile="/tmp/$(basename $f).insertion.$$.tmp"
	populate_tmp_file $strType $gstrLicenseFile $f $strTmpFile
	cp $strTmpFile $f
	clean_up $strTmpFile
    fi
done
