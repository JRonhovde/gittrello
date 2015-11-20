# !bin/bash
gittrello() {
    PUSH=1
    ADDLABEL=0
    REMOVELABEL=0
    while test $# -gt 0; do
        case "$1" in
            -h|--help)
                echo "GitTrello - Link github pull requests and Trello cards"
                echo " "
                echo "GitTrello [options] application [arguments]"
                echo " "
                echo "options:"
                echo "-h, --help                show brief help"
                echo "-al, --add-label          add label to pull request for current branch"
                echo "-rl, --remove-label       add label to pull request for current branch"
                echo "-np, --no-push            don't push branch to remote"
                return 1
                ;;
            -al)
                shift
                if test $# -gt 0; then
                    ADDLABEL="$1"
                else
                    echo "no label specified"
                    exit 1
                fi
                shift
                ;;
            --add-label*)
                ADDLABEL=$(echo $1 | sed -e 's/^[^=]*=//g')
                shift
                ;;
            -rl)
                shift
                if test $# -gt 0; then
                    REMOVELABEL="$1"
                else
                    echo "no label specified"
                    exit 1
                fi
                shift
                ;;
            --remove-label*)
                REMOVELABEL=$(echo $1 | sed -e 's/^[^=]*=//g')
                shift
                ;;
            -n|--no-push)
                PUSH=0
                shift
                ;;
            *)
                break
                ;;
        esac
    done

    SOURCE="${BASH_SOURCE[0]}"
    while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
        DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
        SOURCE="$(readlink "$SOURCE")"
        [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
    done
    DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
    URL="$(git config --get remote.origin.url)"
    BRANCH="$(git rev-parse --abbrev-ref HEAD)"
    if [ $PUSH == 1 ]; then
        git push origin "$BRANCH"
    fi
    python "$DIR/gittrello.py" "$BRANCH" "$URL" "$ADDLABEL" "$REMOVELABEL"
}
_gittrello() {
    local cur=${COMP_WORDS[COMP_CWORD]}

    case "$cur" in
        -*)
        COMPREPLY=( $(compgen -W "--add-label --remove-label" -- $cur ) )
    esac

    return 0
}
complete -F _gittrello gittrello
