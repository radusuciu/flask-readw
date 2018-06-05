#!/bin/bash

set -eo pipefail

# so we can use globbing instead of find
shopt -s globstar nullglob nocaseglob

readonly READW_PATH='/home/wine/readw/ReAdW.exe'

# can't get this to stay registered during container build
# so registering it every time before we run
# perhaps this is only an issue with the .dll obtained
# from the Cravatt lab XCalibur install
regsvr32 /home/wine/readw/XRawfile2.dll &>/dev/null


convert() {
    local item files

    item="${1}"

    if [[ -d "${item}" ]]; then
        # note that globbing should be set to be case insensitive
        files="${item}/*.raw"

        if [[ -z "${files}" ]]; then
            echo "Error: ${item} does not contain any .raw files." >&2
            return
        fi
    elif [[ -f "${item}" ]]; then
        files="${item}"

        if [[ "${item,,}" != *.raw ]]; then
            echo "Error: ${item} is not a .raw file." >&2
            return            
        fi
    else
        echo "Error: ${item} is not a valid directory or .raw file." >&2
        return
    fi

    local filename parent outputFile result

    for file in ${files}; do
        filename="$(basename -- "$file")"
        filename="${filename%.*}"

        parent="$(dirname "${file}")"

        outputFile="${parent}/${filename}.mzXML"
        result=$(wine "${READW_PATH}" --mzXML --centroid "${file}" "${outputFile}")
        echo "${result}"
    done
}

main() {
    local f success conversionResult

    success=true

    for f in "${@}"; do
        echo "==== Converting file ${f} ===="
        conversionResult=$(convert "${f}")
        echo "$conversionResult"

        conversionResult=${conversionResult,,}

        if [[ $conversionResult = *"--done"* ]] && [[ $conversionResult != *"error"* ]]; then
            echo "Successful conversion of ${f}"
        else
            success=false
            echo "Error during conversion of ${f}"
        fi
    done

    if [ "$success" = false ]; then
        { exit 1; }
    fi
}

main "$@"

{ exit 0; }
