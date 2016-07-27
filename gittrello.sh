# !bin/bash
gittrello(){
    # Push branch to remote by default
    PUSH=1

    # Always pass something in these two variables
    ADDLABEL=0
    REMOVELABEL=0

    # $# is the number of parameters passed
    while test $# -gt 0; do
        # '$1' is automatically populated with the first parameter.
        #
        # Shift(used below) directly modifies the array of parameters, changing
        # the value of '$1'
        case "$1" in
            -h|--help)
                echo "GitTrello - Link github pull requests and Trello cards"
                echo " "
                echo "GitTrello [options] application [arguments]"
                echo " "
                echo "options:"
                echo "-h, --help"
                echo ""
                echo "-al <labels>, --add-label[s]=<labels>"
                echo "   Add GitHub labels to pull request for current branch. To add multiple labels, separate them by commas. '<label1>, <label2>'"
                echo ""
                echo "-rl <labels>, --remove-label[s]=<labels>"
                echo "   Remove GitHub labels to pull request for current branch. To remove multiple labels, separate them by commas. '<label1>, <label2>'"
                echo ""
                echo "-np, --no-push"
                echo "   Don't push branch to remote."
                echo ""
                return 1
                ;;
            -al)
                shift
                if test $# -gt 0; then
                    ADDLABEL="$1"
                else
                    echo "Error: No label specified"
                    exit 1
                fi
                shift
                ;;
            --add-label=*|--add-labels=*)
                ADDLABEL=$(echo $1 | sed -e 's/^[^=]*=//g')
                shift
                ;;
            -rl)
                shift
                if test $# -gt 0; then
                    REMOVELABEL="$1"
                else
                    echo "Error: No label specified"
                    exit 1
                fi
                shift
                ;;
            --remove-label=*|--remove-labels=*)
                REMOVELABEL=$(echo $1 | sed -e 's/^[^=]*=//g')
                shift
                ;;
            -n|--no-push)
                # don't push branch to remote
                PUSH=0
                shift
                ;;
            *)
                break
                ;;
        esac
    done

    # Handle symlinks
    #
    # We need to get back to the directory where both scripts
    # are located (.sh and .py)
    SOURCE="${BASH_SOURCE[0]}"

    # while current script location is a symlink
    while [ -h "$SOURCE" ]; do 
        DIR="$( cd "$( dirname "$SOURCE" )" && pwd )"
        SOURCE="$(readlink "$SOURCE")"
        # if $SOURCE was a relative symlink, we need to resolve it 
        # relative to the path where the symlink file was located
        [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" 
    done

    DIR="$( cd "$( dirname "$SOURCE" )" && pwd )"
    URL="$(git config --get remote.origin.url)"
    BRANCH="$(git rev-parse --abbrev-ref HEAD)"

    # never push to remote master
    if [ $BRANCH == "master" ]; then
        PUSH=0
    fi
    if [ "$PUSH" -eq "1" ]; then
        git push origin "$BRANCH"
    fi

    # Call Python script
    # Note: All parameters must be populated
    python "$DIR/gittrello.py" "$BRANCH" "$URL" "$ADDLABEL" "$REMOVELABEL"
}

# Autocomplete function
_gittrello() {
    local cur=${COMP_WORDS[COMP_CWORD]}

    case "$cur" in
        -*)
        COMPREPLY=( $(compgen -W "--add-label --remove-label" -- $cur ) )
    esac

    return 0
}
complete -F _gittrello gittrello
