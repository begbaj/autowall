NAME="autowall"
BINDIR="$HOME/.local/bin/"
FULLPATH="$BINDIR$NAME"

mkdir -p $BINDIR
cp "autowall.py" $FULLPATH
echo "$NAME has been successfully installed to $BINDIR."
