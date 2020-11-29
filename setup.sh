
echo $@



check_directory () {
    if [ ! -d ${1} ]; then
        echo "Creating directory ${1}"
        mkdir ${1}; fi
}

check_file () {
    if [ ! -d ${1} ]; then
        echo "Creating file ${1}"
        mkdir ${1}; fi
}

create_file () {
    echo ''
    echo "Creating ${1} file"
    echo "${@:2}" > ${1}
}

remove_file () {
    PAUSETIMER=5
    echo ''
    echo "About to delete file '${1}'. Pausing for ${PAUSETIMER} to silently confirm consent."
    sleep ${PAUSETIMER}
    rm -f ${1}
    echo 'Delete successful, continuing'
}

# Directories
check_directory "db/"
check_directory "db/archive/"
check_directory "out"
check_directory "logs/behave/old"
check_directory "logs/archive"


# Files
# Names
KEY_FILE_NAME='etc/test_key.yml'
LOCATIONS_FILE_NAME='etc/test_weather_api_private.yml'

# Key file
create_key() {
echo ''
echo 'Prepare to enter your Open Weather Map API key.'
echo 'If you dont have one please follow this link and start the process: https://home.openweathermap.org/users/sign_up'
echo 'If you want to replace the value later just hit enter'
echo 'Please enter your Open Weather Map key now. If you want to skip just hit enter'
read KEYVALUE
[[ $KEYVALUE == '' ]] && KEYVALUE='REPLACE_TEXT_WITH_KEY' || echo "Saving key"

KEY_FILE_CONTENTS="$(cat <<-EOF
Weather_Key: ${KEYVALUE}

EOF
)"
FILENAME=${KEY_FILE_NAME}
FILECONT=${KEY_FILE_CONTENTS}
}

# Locations file
create_locations() {
WAITTIMER=1
GZNAME='city.list.json.gz'
GZLINK="http://bulk.openweathermap.org/sample/${GZNAME}"
UNZIPLOCATION='city.list.json'
echo ''
echo 'About to start the download of the very large json file that contains the different locations available.'
echo "I will wait for ${WAITTIMER}s for you to cancle out before the download begins."
echo 'If you want to download the contents and look through it yourself, go to http://bulk.openweathermap.org/sample/city.list.json.gz'
echo "pausing for ${WAITTIMER} seconds for user to break before continuing"
sleep ${WAITTIMER}

echo 'Verifying older versions of the files do not exist...'


echo "skipping donloads while developing HERE"
if [ -f ${GZNAME} ]; then
    echo 'Deleting old gz file'
    remove_file ${GZNAME}
fi
if [ -f ${UNZIPLOCATION} ]; then
    echo 'Deleting old json file'
    remove_file ${UNZIPLOCATION}
fi
echo "Downloading .gz file to ${GZNAME}"
wget ${GZLINK}
echo "Unziping the file to ${UNZIPLOCATION}"
gunzip ${GZNAME}

# Select locations
location_select
}

location_select() {
    echo ''
    echo 'Starting city selection.'
    CITYNAMES=()
    CITYIDS=()
    FINALCITYNAMES=()
    FINALCITYIDS=()

    # Location selection
    while : ;
    do
        CITYNAME=''
        city_list
        verify_results
        [[ $? != 0 ]] || break
    done

    # Updating the file
    echo ''
    echo ''
    echo 'Updating locations file'
    echo 'locations:' > ${LOCATIONS_FILE_NAME}
    for ((i=0;i<${#FINALCITYIDS[@]};++i)); do
        echo "'${FINALCITYNAMES[i]}' is the current city name for city ID '${FINALCITYIDS[i]}'"
        echo "    ${FINALCITYNAMES[i]}: ${FINALCITYIDS[i]}" >> ${LOCATIONS_FILE_NAME}
    done

    # Cleanup
    echo ''
    echo 'Cleaning up'
    if [ -f ${GZNAME} ]; then
        echo 'Deleting old gz file'
        remove_file ${GZNAME}
    fi
    if [ -f ${UNZIPLOCATION} ]; then
        echo 'Deleting old json file'
        remove_file ${UNZIPLOCATION}
    fi
}

city_list () {
    while [ "${CITYNAME}" != 'done' ]
    do
        echo 'Enter a city name to use to search or "done" if you are done.'
        read CITYNAME

        if [[ "${CITYNAME}" == '' ]]; then
            echo "Invalid entry '${CITYNAME}' so skipping"
            continue; fi
        if [[ "${CITYNAME}" == 'done' ]]; then
            echo "Exiting city selection"
            continue; fi

        echo ''
        echo "Searching for ${CITYNAME}"
        grep -B1 -A7 "${CITYNAME}" ${UNZIPLOCATION}

        echo 'If you see the location you want enter the city "id" now.'
        echo 'If you dont see it just hit return to go back to city name selection.'
        read CITYID
        if [[ "${CITYID}" == '' ]]; then
            echo "Selection cancled"
            continue; fi

        echo 'Selected city:'
        grep -A6 "${CITYID}" ${UNZIPLOCATION}
        echo "Confirm you want cityID ${CITYID} (y/n)"
        read CONFIRMATION

        if [[ "${CONFIRMATION}" != 'y' ]]; then
            echo "Selection cancled"
            continue; fi

        CITYNAMES+=("${CITYNAME}")
        CITYIDS+=("${CITYID}")
    done
}

verify_results () {
    echo ''
    for ((i=0;i<${#CITYIDS[@]};++i)); do
        echo ''
        echo "'${CITYNAMES[i]}' is the current city name for city ID '${CITYIDS[i]}'"
        echo 'You can re-name the city now by typing the new name or hit enter to confirm.'
        echo 'If it was not a valid selection type "skip", or if you want more cities type "more cities"'
        read NEWNAME

        if [[ "${NEWNAME}" == '' ]]; then
            NEWNAME=${CITYNAMES[i]}; fi
        if [[ "${NEWNAME}" == 'skip' ]]; then
            echo "City removed"
            continue; fi
        if [[ "${NEWNAME}" == 'more cities' ]]; then
        echo 'Going back to city selection'
            return 1
        fi

        echo "New city name is ${NEWNAME} for city ID ${CITYIDS[i]}"
        FINALCITYNAMES+=("${NEWNAME}")
        FINALCITYIDS+=("${CITYIDS[i]}")
    done
}

# Resetting files
reset_key() {
    create_key
    create_file ${FILENAME} ${FILECONT}
}
reset_locations() {
    create_locations
}

about () {
    echo '
    The setup portion of build verifies some directories and files that are not in the github are there.
    After cloaning the repo you should run "build setup reset-all" so everything gets run. 
    Without the reset-all it just verifies the directories are in the correct location. 
    reset-key creates a new key file based on the user input key
    reset-locations creates a new file of locations. 
        The locations include an abreviated name and the city ID. 
        The city ID is what the program uses for all locations but the name is for humans. 
    reset-all performs reset-key then reset-locations. 
    help runs this function. 
    '
}

echo "Resetting files based on '${2}'"
case "${2}" in
    # Reset types
    reset-key)
        reset_key
        ;;
    reset-locations)
        reset_locations
        ;;
    reset-all)
        reset_key
        reset_locations
        ;;
    help)
        about
        ;;
esac
