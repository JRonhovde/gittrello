# !bin/bash
gittrello() {
    SOURCE="${BASH_SOURCE[0]}"
    while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
        DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
        SOURCE="$(readlink "$SOURCE")"
        [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
    done
    DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
    repoUrl="$(git config --get remote.origin.url)"
    branchName="$(git rev-parse --abbrev-ref HEAD)"
    git push origin "$branchName" && python $DIR/gittrello.py "$branchName" "$repoUrl"
}
