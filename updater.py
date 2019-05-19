'''
Gitea Remote Updater

Copyright 2018, 2019 The Gitea-Auto-Update Authors
All rights reserved.

License: GNU General Public License
'''
import settings
import requests
import os
import functions

if not functions.is_tool("xz"):
	print ("missing dependency: xz")
	quit()

# Version from gitea site
current_version = requests.get(settings.gtsite).json()['version']

# Get version tag from github and remove first char (v)
github_version_tag = requests.get(settings.gtgithubapiurl).json()['tag_name']

## Testing ##
current_version = 1.8.0

# Get version from version tag
github_version = github_version_tag[1:]
print ("Current version =", current_version)
print (" Github version =", github_version_tag)
# Check if there is a new version
if functions.checkVersion(github_version, current_version):


    # Stop systemd service
    print ("new version available, stopping service")
    os.system("systemctl stop gitea.service")

    # Should the new version be build from source?
    if settings.build_from_source:

        functions.buildFromSource(github_version_tag)

    else:
        # Set download url
        ## main file
        gtdownload = settings.gtgithubfileurl+github_version_tag+'/gitea-'+github_version+'-'+settings.gtsystem+'.xz'
        print (gtdownload)
        ## sha256 file
        shadownload = settings.gtgithubfileurl+github_version_tag+'/gitea-'+github_version+'-'+settings.gtsystem+'.xz.sha256'
        print (shadownload)

        # Download file

        ## downloading sha
        print 	("downloading sha256 hashsum")
        functions.download(shadownload, settings.tmpdir+'gitea.xz.sha256')
        ## downloading xz
        print ("downloading", github_version_tag+'gitea.xz')
        tmpxz = settings.tmpdir+'gitea-'+github_version+'-'+settings.gtsystem+'.xz'
        functions.download(gtdownload, tmpxz)

        # doing sha256 sum
        os.chdir(settings.tmpdir)

        if os.system("sha256sum -c gitea.xz.sha256 > /dev/null") == 0:
        	print ("sha ok, extracting file to location")
        	# extracting download file
        	cmd = "xz -d "+tmpxz
        	print (cmd)
        	os.system(cmd)
        	#  moving temp file to gtfile location
        	#cmd = 'mv '+settings.tmpdir+'gitea-'+github_version+'-'+settings.gtsystem+' '+settings.gtfile
        	#print (cmd)
        	os.rename(f"{settings.tmpdir}gitea-{github_version}-{settings.gtsystem}", settings.gtfile)
			os.chmod(settings.gtfile, st.st_mode | stat.S_IEXEC)
        else:
        	print ("error, sha256 mismatch")
        	quit()

    # Start systemd service
    print ("starting gitea.service")
    os.system("systemctl start gitea.service")

    print ("update successfully")


else:

	#Print current version is uptodate
	print ("current version is uptodate")
